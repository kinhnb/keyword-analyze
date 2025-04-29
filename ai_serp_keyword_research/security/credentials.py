"""
Credentials management for the AI SERP Keyword Research Agent.

This module provides secure handling of API credentials and secrets
for external services like SERP APIs, OpenAI, and other integrations.
"""

import os
import logging
import json
import base64
from pathlib import Path
from typing import Dict, Optional, Any, List, Union
import hashlib

from ai_serp_keyword_research.utils.env_validator import (
    get_env_api_key, get_env_url, validate_env_var,
    EnvironmentValidationError
)

# Configure logging
logger = logging.getLogger(__name__)

# Default secrets location (can be overridden with ENV var)
DEFAULT_SECRETS_DIR = Path("./secrets")

# Known credential types with their specific validation requirements
CREDENTIAL_TYPES = {
    "SERP_API": {
        "required": ["api_key"],
        "optional": ["base_url"]
    },
    "OPENAI_API": {
        "required": ["api_key"],
        "optional": ["organization_id"]
    },
    "DATABASE": {
        "required": ["connection_string"],
        "optional": ["max_connections", "timeout"]
    },
    "REDIS": {
        "required": ["url"],
        "optional": ["password", "timeout"]
    }
}


class CredentialManager:
    """
    Manages secure access to API credentials and secrets.
    
    This class provides methods for loading, validating, and accessing
    credentials for external APIs and services while maintaining security
    best practices.
    """
    
    def __init__(self, secrets_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the credential manager.
        
        Args:
            secrets_dir: Optional path to secrets directory for file-based credentials
        """
        self._env_prefix = os.getenv("ENV_PREFIX", "")
        self._secrets_dir = Path(secrets_dir or os.getenv("SECRETS_DIR", DEFAULT_SECRETS_DIR))
        self._credentials: Dict[str, Dict[str, Any]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        
        self._initialized = False
        self._load_context = None
    
    def initialize(self) -> None:
        """
        Initialize the credential manager by loading all credentials.
        
        This method should be called once at application startup.
        """
        if self._initialized:
            logger.warning("Credential manager already initialized")
            return
        
        try:
            self._load_credentials_from_env()
            self._load_credentials_from_files()
            self._initialized = True
            logger.info("Credential manager initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize credential manager: {str(e)}")
            raise
    
    def _generate_credential_key(self, service: str, context: Optional[str] = None) -> str:
        """
        Generate a unique key for a credential.
        
        Args:
            service: Service name
            context: Optional context (e.g., environment, region)
            
        Returns:
            A unique key for the credential
        """
        if context:
            return f"{service}_{context}"
        return service
    
    def _load_credentials_from_env(self) -> None:
        """Load credentials from environment variables."""
        # SERP API credentials
        self._load_serp_api_credentials()
        
        # OpenAI API credentials
        self._load_openai_api_credentials()
        
        # Database credentials
        self._load_database_credentials()
        
        # Redis credentials
        self._load_redis_credentials()
    
    def _load_serp_api_credentials(self) -> None:
        """Load SERP API credentials from environment variables."""
        api_key = get_env_api_key(f"{self._env_prefix}SERP_API_KEY", required=False)
        base_url = get_env_url(f"{self._env_prefix}SERP_API_URL", required=False)
        
        if api_key:
            self.set_credential(
                "SERP_API",
                {
                    "api_key": api_key,
                    "base_url": base_url
                },
                source="environment"
            )
    
    def _load_openai_api_credentials(self) -> None:
        """Load OpenAI API credentials from environment variables."""
        api_key = get_env_api_key(f"{self._env_prefix}OPENAI_API_KEY", required=False)
        org_id = validate_env_var(f"{self._env_prefix}OPENAI_ORGANIZATION_ID", required=False)
        
        if api_key:
            self.set_credential(
                "OPENAI_API",
                {
                    "api_key": api_key,
                    "organization_id": org_id
                },
                source="environment"
            )
    
    def _load_database_credentials(self) -> None:
        """Load database credentials from environment variables."""
        conn_string = get_env_url(
            f"{self._env_prefix}DATABASE_URL", 
            required=False,
            allowed_schemes=["postgresql", "sqlite"]
        )
        
        if conn_string:
            max_connections = os.getenv(f"{self._env_prefix}DATABASE_MAX_CONNECTIONS")
            timeout = os.getenv(f"{self._env_prefix}DATABASE_TIMEOUT")
            
            self.set_credential(
                "DATABASE",
                {
                    "connection_string": conn_string,
                    "max_connections": int(max_connections) if max_connections else None,
                    "timeout": int(timeout) if timeout else None
                },
                source="environment"
            )
    
    def _load_redis_credentials(self) -> None:
        """Load Redis credentials from environment variables."""
        redis_url = get_env_url(
            f"{self._env_prefix}REDIS_URL", 
            required=False,
            allowed_schemes=["redis"]
        )
        
        if redis_url:
            redis_password = validate_env_var(f"{self._env_prefix}REDIS_PASSWORD", required=False)
            redis_timeout = os.getenv(f"{self._env_prefix}REDIS_TIMEOUT")
            
            self.set_credential(
                "REDIS",
                {
                    "url": redis_url,
                    "password": redis_password,
                    "timeout": int(redis_timeout) if redis_timeout else None
                },
                source="environment"
            )
    
    def _load_credentials_from_files(self) -> None:
        """Load credentials from files in the secrets directory."""
        if not self._secrets_dir.exists():
            logger.info(f"Secrets directory {self._secrets_dir} does not exist, skipping file-based credentials")
            return
        
        # Load credentials from JSON files
        for file_path in self._secrets_dir.glob("*.json"):
            try:
                service = file_path.stem
                with open(file_path, "r") as f:
                    credentials = json.load(f)
                
                # Validate required fields based on service type
                self._validate_credential_fields(service, credentials)
                
                # Add to credentials store
                self.set_credential(service, credentials, source="file")
                
                logger.info(f"Loaded credentials for {service} from {file_path}")
            except Exception as e:
                logger.error(f"Failed to load credentials from {file_path}: {str(e)}")
    
    def _validate_credential_fields(self, service: str, credentials: Dict[str, Any]) -> None:
        """
        Validate that credentials contain required fields for the service.
        
        Args:
            service: Service name
            credentials: Credential dictionary
            
        Raises:
            EnvironmentValidationError: If required fields are missing
        """
        # Check if we know this credential type
        credential_type = service.split("_")[0] if "_" in service else service
        
        if credential_type in CREDENTIAL_TYPES:
            required_fields = CREDENTIAL_TYPES[credential_type]["required"]
            
            # Check for missing required fields
            missing_fields = [field for field in required_fields if field not in credentials]
            
            if missing_fields:
                raise EnvironmentValidationError(
                    f"Missing required fields for {service} credentials: {', '.join(missing_fields)}"
                )
    
    def set_credential(
        self, 
        service: str, 
        credentials: Dict[str, Any], 
        context: Optional[str] = None,
        source: Optional[str] = None
    ) -> None:
        """
        Set credentials for a service.
        
        Args:
            service: Service name
            credentials: Credential dictionary
            context: Optional context (e.g., environment, region)
            source: Where the credential came from (environment, file, etc.)
        """
        # Validate required fields based on service type
        self._validate_credential_fields(service, credentials)
        
        # Store credentials
        key = self._generate_credential_key(service, context)
        self._credentials[key] = credentials
        
        # Store metadata
        self._metadata[key] = {
            "source": source or "manual",
            "has_sensitive_data": True,
            "timestamp": os.environ.get("START_TIME", "")
        }
        
        # Log credential addition (without sensitive data)
        sensitive_fields = ["api_key", "password", "token", "secret", "connection_string"]
        safe_creds = {k: "***" if k in sensitive_fields else v for k, v in credentials.items()}
        logger.info(f"Credentials for {key} set: {safe_creds}")
    
    def get_credential(
        self, 
        service: str, 
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get credentials for a service.
        
        Args:
            service: Service name
            context: Optional context (e.g., environment, region)
            
        Returns:
            Credential dictionary or None if not found
        """
        if not self._initialized:
            logger.warning("Credential manager not initialized")
            self.initialize()
        
        key = self._generate_credential_key(service, context)
        return self._credentials.get(key)
    
    def get_api_key(
        self, 
        service: str, 
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Get API key for a service.
        
        Args:
            service: Service name
            context: Optional context (e.g., environment, region)
            
        Returns:
            API key string or None if not found
        """
        credentials = self.get_credential(service, context)
        return credentials.get("api_key") if credentials else None
    
    def get_connection_string(
        self, 
        service: str = "DATABASE", 
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Get connection string for a service.
        
        Args:
            service: Service name (default: DATABASE)
            context: Optional context (e.g., environment, region)
            
        Returns:
            Connection string or None if not found
        """
        credentials = self.get_credential(service, context)
        return credentials.get("connection_string") if credentials else None
    
    def has_credential(
        self, 
        service: str, 
        context: Optional[str] = None
    ) -> bool:
        """
        Check if credentials exist for a service.
        
        Args:
            service: Service name
            context: Optional context (e.g., environment, region)
            
        Returns:
            True if credentials exist, False otherwise
        """
        key = self._generate_credential_key(service, context)
        return key in self._credentials
    
    def get_metadata(
        self, 
        service: str, 
        context: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata for service credentials.
        
        Args:
            service: Service name
            context: Optional context (e.g., environment, region)
            
        Returns:
            Metadata dictionary or None if not found
        """
        key = self._generate_credential_key(service, context)
        return self._metadata.get(key)
    
    def list_services(self) -> List[str]:
        """
        List all services with credentials.
        
        Returns:
            List of service names
        """
        return list(self._credentials.keys())


# Singleton instance for app-wide use
_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    """
    Get the global credential manager instance.
    
    Returns:
        CredentialManager instance
    """
    global _credential_manager
    
    if _credential_manager is None:
        _credential_manager = CredentialManager()
        _credential_manager.initialize()
    
    return _credential_manager 