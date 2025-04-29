"""
SERP pattern detection tools for the AI SERP Keyword Research Agent.

These tools provide functionality to identify recurring patterns and themes
across search results to detect search intent and content trends.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from collections import Counter

from agents import function_tool
from pydantic import BaseModel, Field


class SerpPatternResult(BaseModel):
    """Model representing SERP pattern detection results."""
    common_themes: List[str] = Field(..., description="Common themes across results")
    content_types: Dict[str, int] = Field(..., description="Content type distribution")
    domain_patterns: Dict[str, int] = Field(..., description="Domain pattern distribution")
    title_patterns: List[str] = Field(..., description="Common patterns in titles")
    similarity_score: float = Field(..., description="Similarity score across results")
    pod_relevance: float = Field(..., description="POD relevance score of patterns")


def extract_content_types(serp_results: Dict[str, Any]) -> Dict[str, int]:
    """
    Extract and count content types from SERP results.
    
    Args:
        serp_results: The SERP data to analyze.
        
    Returns:
        Dictionary of content types with counts.
    """
    content_types = {}
    organic_results = serp_results.get("organic_results", [])
    
    # Content type patterns to look for in URLs and titles
    patterns = {
        "product_page": [
            r'product', r'item', r'/p/', r'shop', r'buy', 
            r'amazon\.com', r'etsy\.com', r'ebay\.com', r'/dp/'
        ],
        "category_page": [
            r'category', r'collection', r'/c/', r'shop-all', 
            r'department', r'all-products', r'/collections/'
        ],
        "article": [
            r'blog', r'article', r'post', r'news', r'guide', 
            r'how-to', r'tips', r'/posts/', r'/articles/'
        ],
        "brand_page": [
            r'about', r'about-us', r'our-story', r'brand', 
            r'company', r'homepage', r'^[^/]*$'  # Root domain
        ],
        "marketplace": [
            r'amazon\.com', r'etsy\.com', r'ebay\.com', r'walmart\.com',
            r'redbubble\.com', r'teespring\.com', r'spreadshirt\.com'
        ]
    }
    
    for result in organic_results:
        url = result.get("url", "").lower()
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        
        detected_type = None
        
        # Check URL and title against patterns
        for content_type, pattern_list in patterns.items():
            if detected_type:
                break
                
            for pattern in pattern_list:
                if (re.search(pattern, url) or 
                    re.search(pattern, title) or 
                    re.search(pattern, snippet)):
                    detected_type = content_type
                    break
        
        # If no pattern matched, use a default
        if not detected_type:
            detected_type = "other"
            
        # Increment the counter for this content type
        content_types[detected_type] = content_types.get(detected_type, 0) + 1
    
    return content_types


def extract_common_themes(serp_results: Dict[str, Any]) -> List[str]:
    """
    Extract common themes across SERP results.
    
    Args:
        serp_results: The SERP data to analyze.
        
    Returns:
        List of common themes.
    """
    organic_results = serp_results.get("organic_results", [])
    
    # Extract all text from titles and snippets
    all_text = ""
    for result in organic_results:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        all_text += f" {title} {snippet}"
    
    # Extract potential themes (2-3 word phrases)
    words = re.findall(r'\b\w+\b', all_text)
    themes = []
    
    for i in range(len(words) - 1):
        if i < len(words) - 2:
            themes.append(f"{words[i]} {words[i+1]} {words[i+2]}")
        themes.append(f"{words[i]} {words[i+1]}")
    
    # Count occurrences and keep those appearing at least twice
    theme_counter = Counter(themes)
    common_themes = [theme for theme, count in theme_counter.items() if count >= 2]
    
    # Filter out generic phrases and focus on POD-relevant themes
    pod_terms = ["shirt", "tee", "t-shirt", "graphic", "print", "design", "apparel", "clothing"]
    pod_themes = []
    
    for theme in common_themes:
        if any(term in theme for term in pod_terms):
            pod_themes.append(theme)
    
    # Sort by relevance (estimated by occurrence and presence of POD terms)
    return sorted(pod_themes, key=lambda t: sum(1 for term in pod_terms if term in t) * theme_counter[t], reverse=True)[:10]


def calculate_similarity_score(serp_results: Dict[str, Any]) -> float:
    """
    Calculate similarity score across SERP results.
    
    Args:
        serp_results: The SERP data to analyze.
        
    Returns:
        Similarity score between 0.0 and 1.0.
    """
    organic_results = serp_results.get("organic_results", [])
    
    if not organic_results or len(organic_results) < 2:
        return 0.0
    
    # Extract words from all results
    result_words = []
    for result in organic_results:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        
        # Extract words
        words = re.findall(r'\b\w+\b', f"{title} {snippet}")
        result_words.append(set(words))
    
    # Calculate average similarity based on word overlap
    total_similarity = 0.0
    comparison_count = 0
    
    for i in range(len(result_words)):
        for j in range(i + 1, len(result_words)):
            words1 = result_words[i]
            words2 = result_words[j]
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union > 0:
                similarity = intersection / union
                total_similarity += similarity
                comparison_count += 1
    
    # Average similarity
    avg_similarity = total_similarity / comparison_count if comparison_count > 0 else 0.0
    
    return avg_similarity


def identify_title_patterns(serp_results: Dict[str, Any]) -> List[str]:
    """
    Identify common patterns in result titles.
    
    Args:
        serp_results: The SERP data to analyze.
        
    Returns:
        List of identified patterns.
    """
    organic_results = serp_results.get("organic_results", [])
    
    # Common title patterns to look for
    patterns = {
        "list": r'(top|best|^\d+|list of|ultimate|complete)\s+\d*',
        "how_to": r'how\s+to|guide|tutorial|tips|ideas',
        "question": r'\?|what|why|when|where|who|which',
        "product": r'(buy|shop|get|purchase|order)',
        "comparison": r'vs|versus|compare|compared to|or'
    }
    
    detected_patterns = {}
    
    for result in organic_results:
        title = result.get("title", "").lower()
        
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, title):
                detected_patterns[pattern_name] = detected_patterns.get(pattern_name, 0) + 1
    
    # Return patterns that appear in at least 2 results
    return [f"{name} ({count})" for name, count in detected_patterns.items() if count >= 2]


@function_tool
async def detect_serp_patterns(serp_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect patterns and commonalities across SERP results.
    
    This tool analyzes SERP data to identify common themes, content types,
    domain patterns, and title patterns to help understand search intent
    and content trends.
    
    Args:
        serp_results: The SERP data to analyze for patterns.
        
    Returns:
        Dictionary containing pattern analysis results.
    """
    try:
        # Extract organic results
        organic_results = serp_results.get("organic_results", [])
        
        # Skip pattern detection if no results
        if not organic_results:
            raise ValueError("No organic results found in SERP data")
        
        # Extract domain patterns
        domains = [result.get("domain", "") for result in organic_results if result.get("domain")]
        domain_counter = Counter(domains)
        
        # Extract content types
        content_types = extract_content_types(serp_results)
        
        # Extract common themes
        common_themes = extract_common_themes(serp_results)
        
        # Identify title patterns
        title_patterns = identify_title_patterns(serp_results)
        
        # Calculate similarity score
        similarity_score = calculate_similarity_score(serp_results)
        
        # Calculate POD relevance of patterns
        pod_terms = ["shirt", "tee", "t-shirt", "graphic", "print", "design", "apparel", "clothing"]
        pod_relevance = 0.0
        
        # Check themes for POD relevance
        if common_themes:
            theme_relevance = sum(1 for theme in common_themes if any(term in theme for term in pod_terms)) / len(common_themes)
            pod_relevance = theme_relevance
        
        # Create response
        result = SerpPatternResult(
            common_themes=common_themes,
            content_types=content_types,
            domain_patterns=dict(domain_counter.most_common(5)),
            title_patterns=title_patterns,
            similarity_score=similarity_score,
            pod_relevance=pod_relevance
        )
        
        return result.dict()
    except Exception as e:
        raise ValueError(f"Pattern detection failed: {str(e)}") 