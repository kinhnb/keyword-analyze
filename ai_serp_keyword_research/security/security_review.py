"""
Security review utilities for the AI SERP Keyword Research Agent.

This module provides tools for conducting security reviews and audits
to identify potential security issues in the application.
"""

import os
import logging
import re
import glob
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
import json

# Configure logging
logger = logging.getLogger(__name__)

# Common security patterns to check for in codebase
SECURITY_PATTERNS = {
    # API keys and credentials hardcoded in source code
    "hardcoded_secrets": [
        r'(api_key|api\s*key|apikey)\s*=\s*["\']([a-zA-Z0-9_\-]{10,})["\']',
        r'(password|passwd|pwd)\s*=\s*["\']([a-zA-Z0-9_\-]{8,})["\']',
        r'(secret|token)\s*=\s*["\']([a-zA-Z0-9_\-]{8,})["\']',
        r'Authorization:\s*["\']Bearer\s+([a-zA-Z0-9_\-.]{8,})["\']',
    ],
    
    # SQL injection vulnerabilities
    "sql_injection": [
        r'execute\(["\'].*?\s*\+\s*.+?\s*\+.*?["\']\)',
        r'executemany\(["\'].*?\s*\+\s*.+?\s*\+.*?["\']\)',
        r'cursor\.execute\(.*?\%.*?\)',
        r'execute\(f["\'].*?{.*?}.*?["\']\)'
    ],
    
    # Unsanitized user inputs
    "unsanitized_input": [
        r'eval\(["\'].*?["\']\)',
        r'exec\(["\'].*?["\']\)',
        r'subprocess\..*?\(["\'].*?["\']\)',
        r'os\.system\(["\'].*?["\']\)',
        r'os\.popen\(["\'].*?["\']\)',
    ],
    
    # Insecure permissions
    "insecure_permissions": [
        r'os\.chmod\(.*?,\s*0o777\)',
        r'os\.chmod\(.*?,\s*777\)',
        r'os\.chmod\(.*?,\s*0o666\)',
        r'os\.chmod\(.*?,\s*666\)',
    ],
    
    # Missing authentication/authorization
    "missing_authentication": [
        r'@app\.route\(.*?\)\ndef\s+(?!.*auth)',
        r'@router\.get\(.*?\)\s*\n\s*async\s+def\s+(?!.*auth)',
        r'@router\.post\(.*?\)\s*\n\s*async\s+def\s+(?!.*auth)',
        r'@router\.put\(.*?\)\s*\n\s*async\s+def\s+(?!.*auth)',
        r'@router\.delete\(.*?\)\s*\n\s*async\s+def\s+(?!.*auth)',
    ],
    
    # Missing input validation
    "missing_validation": [
        r'def\s+\w+\([^)]*\)\s*:(?![^:]*validate)',
        r'async\s+def\s+\w+\([^)]*\)\s*:(?![^:]*validate)',
    ],
    
    # Insecure deserialization
    "insecure_deserialization": [
        r'pickle\.loads\(',
        r'yaml\.load\((?!.*Loader=yaml\.SafeLoader)',
        r'json\.loads\([^)]*encoding\s*=\s*["\'].*?["\']\)',
    ],
    
    # Improper error handling
    "improper_error_handling": [
        r'except\s*Exception\s*as\s*e\s*:\s*pass',
        r'except\s*:\s*pass',
        r'except\s*Exception\s*:\s*pass',
    ],
    
    # CORS configuration issues
    "cors_issues": [
        r'CORS\(app,\s*origins\s*=\s*["\']\*["\']\)',
        r'add_middleware\(CORSMiddleware,\s*allow_origins\s*=\s*\[["\']\*["\']\]',
    ],
    
    # Logging of sensitive information
    "sensitive_logging": [
        r'logging\.[a-z]+\(.*?(password|token|key|secret|credential).*?\)',
        r'logger\.[a-z]+\(.*?(password|token|key|secret|credential).*?\)',
    ],
}

# File paths to exclude from security review
EXCLUDED_PATHS = [
    "/venv/",
    "/__pycache__/",
    "/.git/",
    "/node_modules/",
    "/.env",
    "/build/",
    "/dist/",
    "/.mypy_cache/",
    "/.pytest_cache/",
    "/tests/",
    "/security_review.py",  # Don't scan this file itself
]

# File extensions to scan
INCLUDED_EXTENSIONS = [
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".sql", ".sh",
    ".yaml", ".yml", ".json", ".xml", ".md", ".cfg", ".ini"
]


class SecurityReviewFinding:
    """Represents a security finding from the review."""
    
    def __init__(
        self, 
        rule_name: str, 
        file_path: str, 
        line_number: int, 
        line_content: str, 
        severity: str = "high"
    ):
        """
        Initialize a security finding.
        
        Args:
            rule_name: Name of the security rule that was triggered
            file_path: Path to the file containing the finding
            line_number: Line number in the file
            line_content: Content of the line
            severity: Severity level ('high', 'medium', 'low')
        """
        self.rule_name = rule_name
        self.file_path = file_path
        self.line_number = line_number
        self.line_content = line_content
        self.severity = severity.lower()
        
        # Validate severity
        if self.severity not in ("high", "medium", "low"):
            self.severity = "high"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "rule_name": self.rule_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "line_content": self.line_content,
            "severity": self.severity
        }
    
    def __str__(self) -> str:
        """String representation of the finding."""
        return (
            f"[{self.severity.upper()}] {self.rule_name} in {self.file_path}:{self.line_number}\n"
            f"  {self.line_content.strip()}"
        )


class SecurityReviewer:
    """
    Performs security reviews of the codebase.
    
    This class provides methods for detecting common security issues
    in the codebase and generating reports.
    """
    
    def __init__(
        self, 
        base_path: Optional[str] = None,
        extra_patterns: Optional[Dict[str, List[str]]] = None,
        exclude_paths: Optional[List[str]] = None
    ):
        """
        Initialize the security reviewer.
        
        Args:
            base_path: Base directory path to scan (defaults to current directory)
            extra_patterns: Additional security patterns to check
            exclude_paths: Additional paths to exclude from scan
        """
        self.base_path = Path(base_path or os.getcwd())
        self.patterns = dict(SECURITY_PATTERNS)
        
        # Add extra patterns if provided
        if extra_patterns:
            for rule_name, patterns in extra_patterns.items():
                if rule_name in self.patterns:
                    self.patterns[rule_name].extend(patterns)
                else:
                    self.patterns[rule_name] = patterns
        
        # Combine excluded paths
        self.excluded_paths = EXCLUDED_PATHS.copy()
        if exclude_paths:
            self.excluded_paths.extend(exclude_paths)
            
        # Compile patterns for performance
        self.compiled_patterns = {
            rule_name: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for rule_name, patterns in self.patterns.items()
        }
        
        # Initialize findings list
        self.findings: List[SecurityReviewFinding] = []

    def should_scan_file(self, file_path: str) -> bool:
        """
        Check if a file should be scanned based on path and extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file should be scanned, False otherwise
        """
        # Check for excluded paths
        if any(excl in file_path for excl in self.excluded_paths):
            return False
        
        # Check for included extensions
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in INCLUDED_EXTENSIONS
    
    def scan_file(self, file_path: str) -> List[SecurityReviewFinding]:
        """
        Scan a single file for security issues.
        
        Args:
            file_path: Path to the file to scan
            
        Returns:
            List of security findings
        """
        findings: List[SecurityReviewFinding] = []
        
        if not self.should_scan_file(file_path):
            return findings
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for line_number, line in enumerate(lines, 1):
                for rule_name, patterns in self.compiled_patterns.items():
                    for pattern in patterns:
                        if pattern.search(line):
                            findings.append(
                                SecurityReviewFinding(
                                    rule_name=rule_name,
                                    file_path=file_path,
                                    line_number=line_number,
                                    line_content=line,
                                    severity=self._get_severity(rule_name)
                                )
                            )
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")
        
        return findings
    
    def _get_severity(self, rule_name: str) -> str:
        """
        Determine severity based on rule name.
        
        Args:
            rule_name: Name of the security rule
            
        Returns:
            Severity level ('high', 'medium', 'low')
        """
        high_severity = ["hardcoded_secrets", "sql_injection", "unsanitized_input", "insecure_deserialization"]
        medium_severity = ["missing_authentication", "insecure_permissions", "cors_issues"]
        
        if rule_name in high_severity:
            return "high"
        elif rule_name in medium_severity:
            return "medium"
        else:
            return "low"
    
    def scan_directory(self, directory: Optional[str] = None) -> List[SecurityReviewFinding]:
        """
        Scan a directory recursively for security issues.
        
        Args:
            directory: Directory to scan (defaults to base_path)
            
        Returns:
            List of security findings
        """
        findings: List[SecurityReviewFinding] = []
        scan_dir = Path(directory or self.base_path)
        
        try:
            for root, _, files in os.walk(scan_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_findings = self.scan_file(file_path)
                    findings.extend(file_findings)
        except Exception as e:
            logger.error(f"Error scanning directory {scan_dir}: {str(e)}")
        
        # Sort findings by severity and file path
        findings.sort(key=lambda x: (
            0 if x.severity == "high" else 1 if x.severity == "medium" else 2,
            x.file_path,
            x.line_number
        ))
        
        # Store findings
        self.findings = findings
        
        return findings
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a security review report.
        
        Args:
            output_file: Optional file path to write the report to
            
        Returns:
            Report as a dictionary
        """
        # Count by severity
        severity_counts = {
            "high": sum(1 for f in self.findings if f.severity == "high"),
            "medium": sum(1 for f in self.findings if f.severity == "medium"),
            "low": sum(1 for f in self.findings if f.severity == "low"),
        }
        
        # Count by rule
        rule_counts: Dict[str, int] = {}
        for finding in self.findings:
            rule_counts[finding.rule_name] = rule_counts.get(finding.rule_name, 0) + 1
        
        # Create report structure
        report = {
            "summary": {
                "total_findings": len(self.findings),
                "severity_counts": severity_counts,
                "rule_counts": rule_counts,
            },
            "findings": [finding.to_dict() for finding in self.findings]
        }
        
        # Write to file if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Security report written to {output_file}")
            except Exception as e:
                logger.error(f"Error writing report to {output_file}: {str(e)}")
        
        return report
    
    def print_findings(self) -> None:
        """Print all findings to console."""
        print(f"\n{'=' * 80}")
        print(f"SECURITY REVIEW RESULTS - {len(self.findings)} findings")
        print(f"{'=' * 80}")
        
        if not self.findings:
            print("\nNo security issues found.")
            return
        
        severity_counts = {
            "high": sum(1 for f in self.findings if f.severity == "high"),
            "medium": sum(1 for f in self.findings if f.severity == "medium"),
            "low": sum(1 for f in self.findings if f.severity == "low"),
        }
        
        print(f"\nSummary:")
        print(f"  High severity issues:   {severity_counts['high']}")
        print(f"  Medium severity issues: {severity_counts['medium']}")
        print(f"  Low severity issues:    {severity_counts['low']}")
        print(f"\nFindings:")
        
        for finding in self.findings:
            print(f"\n{finding}")
        
        print(f"\n{'=' * 80}")


def run_security_review(
    base_path: Optional[str] = None,
    output_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a security review of the codebase.
    
    Args:
        base_path: Base directory path to scan (defaults to current directory)
        output_file: Optional file path to write the report to
        
    Returns:
        Security review report as a dictionary
    """
    reviewer = SecurityReviewer(base_path)
    reviewer.scan_directory()
    report = reviewer.generate_report(output_file)
    reviewer.print_findings()
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run a security review of the codebase")
    parser.add_argument("--path", help="Base directory path to scan", default=os.getcwd())
    parser.add_argument("--output", help="Output file for the report", default=None)
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run the security review
    run_security_review(args.path, args.output) 