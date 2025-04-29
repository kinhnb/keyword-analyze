"""
Market gap analysis tools for the AI SERP Keyword Research Agent.

These tools provide functionality to identify market gaps and opportunities
based on SERP analysis and search intent.
"""

from typing import Dict, Any, List, Optional, Set
import re
from collections import Counter

from agents import function_tool
from pydantic import BaseModel, Field


class MarketGapResult(BaseModel):
    """Model representing market gap analysis results."""
    detected: bool = Field(..., description="Whether a market gap was detected")
    description: Optional[str] = Field(None, description="Description of the detected market gap")
    opportunity_score: Optional[float] = Field(None, description="Score representing opportunity size (0.0-1.0)")
    competition_level: Optional[float] = Field(None, description="Score representing competition level (0.0-1.0)")
    related_keywords: Optional[List[Dict[str, Any]]] = Field(None, description="Keywords related to the opportunity")


def extract_pod_specific_terms(serp_results: Dict[str, Any]) -> Set[str]:
    """
    Extract POD-specific terms from SERP results.
    
    Args:
        serp_results: The SERP data to analyze.
        
    Returns:
        Set of POD-specific terms found.
    """
    # Define POD-specific terms to look for
    pod_terms = {
        # Design types
        "funny", "vintage", "retro", "distressed", "minimalist", "cute",
        "cool", "trendy", "aesthetic", "custom", "personalized", "unique",
        # Subject matter
        "quote", "saying", "meme", "graphic", "illustration", "design",
        "artwork", "pattern", "logo", "character", "cartoon", "anime",
        # Product terms
        "shirt", "tee", "t-shirt", "tshirt", "apparel", "clothing",
        "hoodie", "sweatshirt", "tank", "top", "print", "printed",
        # Audience terms
        "men", "women", "unisex", "kids", "children", "family",
        "dad", "mom", "father", "mother", "grandpa", "grandma",
        # Occasion terms
        "gift", "present", "birthday", "christmas", "holiday",
        "anniversary", "graduation", "father's day", "mother's day"
    }
    
    # Extract all text from results
    all_text = ""
    organic_results = serp_results.get("organic_results", [])
    
    for result in organic_results:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        all_text += f" {title} {snippet}"
    
    # Find POD terms in the text
    found_terms = set()
    for term in pod_terms:
        if re.search(r'\b' + re.escape(term) + r'\b', all_text):
            found_terms.add(term)
    
    return found_terms


def identify_content_gaps(serp_results: Dict[str, Any], intent_type: str) -> List[str]:
    """
    Identify content or product gaps in SERP results.
    
    Args:
        serp_results: The SERP data to analyze.
        intent_type: The classified intent type.
        
    Returns:
        List of identified gaps.
    """
    gaps = []
    organic_results = serp_results.get("organic_results", [])
    
    # Extract all text
    all_text = ""
    for result in organic_results:
        title = result.get("title", "").lower()
        snippet = result.get("snippet", "").lower()
        all_text += f" {title} {snippet}"
    
    # Check for common POD niches not addressed in results
    pod_niches = {
        "profession": ["profession", "job", "occupation", "career", "work"],
        "hobby": ["hobby", "interest", "passion", "activity", "sport"],
        "humor": ["funny", "humor", "joke", "pun", "sarcastic", "hilarious"],
        "quote": ["quote", "saying", "phrase", "words", "message"],
        "occasion": ["event", "occasion", "celebration", "party", "holiday"],
        "identity": ["identity", "pride", "heritage", "culture", "background"],
        "fandom": ["fan", "fandom", "series", "movie", "book", "game", "character"]
    }
    
    # Check which niches are missing
    for niche, terms in pod_niches.items():
        # If none of the terms are present, consider it a gap
        if not any(re.search(r'\b' + re.escape(term) + r'\b', all_text) for term in terms):
            if intent_type == "transactional":
                gaps.append(f"No {niche}-themed graphic tees in results")
            elif intent_type == "informational":
                gaps.append(f"No content addressing {niche}-themed graphic tees")
            else:
                gaps.append(f"No {niche}-related results")
    
    # Check for quality gaps (indicators of poor content/products)
    quality_indicators = {
        "personalization": ["personalize", "custom", "customized", "personalized", "name"],
        "sizing": ["size", "sizing", "fit", "measurement", "large", "small", "medium"],
        "material": ["material", "fabric", "cotton", "blend", "quality", "soft"],
        "shipping": ["shipping", "delivery", "fast", "quick", "worldwide"],
        "reviews": ["review", "rating", "star", "feedback", "testimonial"]
    }
    
    for indicator, terms in quality_indicators.items():
        if not any(re.search(r'\b' + re.escape(term) + r'\b', all_text) for term in terms):
            if intent_type == "transactional":
                gaps.append(f"No mention of {indicator} information for products")
            elif intent_type == "informational":
                gaps.append(f"No content addressing {indicator} considerations")
    
    return gaps


def calculate_opportunity_score(
    gaps: List[str], 
    serp_results: Dict[str, Any], 
    pod_terms: Set[str]
) -> float:
    """
    Calculate opportunity score based on identified gaps.
    
    Args:
        gaps: List of identified market gaps.
        serp_results: The SERP data used in analysis.
        pod_terms: Set of POD-specific terms found in results.
        
    Returns:
        Opportunity score between 0.0 and 1.0.
    """
    # Base score based on number of gaps (more gaps = higher opportunity)
    base_score = min(len(gaps) / 10, 0.7)  # Cap at 0.7
    
    # Bonus for POD relevance
    pod_bonus = min(len(pod_terms) / 20, 0.2)  # Cap at 0.2
    
    # Bonus for low similarity among top results
    # (indicates less consolidated competition)
    organic_results = serp_results.get("organic_results", [])
    similarity_penalty = 0.0
    
    if len(organic_results) >= 3:
        # Extract domains
        domains = [result.get("domain", "") for result in organic_results[:5] if result.get("domain")]
        domain_counts = Counter(domains)
        
        # If the same domain appears multiple times, apply penalty
        max_domain_count = max(domain_counts.values()) if domain_counts else 0
        if max_domain_count > 1:
            similarity_penalty = min((max_domain_count - 1) * 0.1, 0.2)
    
    # Calculate final score (capped at 0.95)
    opportunity_score = min(base_score + pod_bonus - similarity_penalty, 0.95)
    
    return opportunity_score


def calculate_competition_level(serp_results: Dict[str, Any]) -> float:
    """
    Calculate competition level based on SERP results.
    
    Args:
        serp_results: The SERP data to analyze.
        
    Returns:
        Competition level score between 0.0 and 1.0.
    """
    organic_results = serp_results.get("organic_results", [])
    
    # Initialize competition factors
    major_marketplace_presence = 0.0
    domain_diversity = 0.0
    brand_presence = 0.0
    
    # Check for major marketplaces in top results
    major_marketplaces = ["amazon.com", "etsy.com", "ebay.com", "walmart.com", "redbubble.com"]
    domains = [result.get("domain", "") for result in organic_results if result.get("domain")]
    
    marketplace_count = sum(1 for domain in domains if any(marketplace in domain for marketplace in major_marketplaces))
    
    # More marketplaces = higher competition
    if marketplace_count > 0:
        major_marketplace_presence = min(marketplace_count / 3, 0.4)  # Cap at 0.4
    
    # Check domain diversity (less diversity = higher competition)
    unique_domains = len(set(domains))
    if domains:
        domain_diversity = 0.3 * (1 - (unique_domains / len(domains)))
    
    # Check for brand presence
    brand_terms = ["official", "store", "shop", "brand", "original"]
    brand_mentions = 0
    
    for result in organic_results:
        title = result.get("title", "").lower()
        if any(term in title for term in brand_terms):
            brand_mentions += 1
    
    if brand_mentions > 0:
        brand_presence = min(brand_mentions / 3, 0.3)  # Cap at 0.3
    
    # Calculate final competition score
    competition_level = min(major_marketplace_presence + domain_diversity + brand_presence, 0.95)
    
    return competition_level


def extract_gap_keywords(gaps: List[str]) -> List[Dict[str, Any]]:
    """
    Extract keywords related to identified gaps.
    
    Args:
        gaps: List of identified market gaps.
        
    Returns:
        List of keywords with relevance scores.
    """
    keywords = []
    
    # Extract key terms from gap descriptions
    for gap in gaps:
        # Extract the main theme (e.g., "profession" from "No profession-themed graphic tees")
        theme_match = re.search(r'No ([a-z-]+)-themed', gap)
        if theme_match:
            theme = theme_match.group(1)
            
            # Add the theme as a keyword
            keywords.append({
                "text": f"{theme} graphic tee",
                "relevance": 0.9,
                "frequency": 1
            })
            
            # Add variations
            keywords.append({
                "text": f"{theme} t-shirt",
                "relevance": 0.85,
                "frequency": 1
            })
            
            # For quality gaps, extract the quality indicator
            if "information" in gap or "considerations" in gap:
                indicator_match = re.search(r'No mention of ([a-z]+) information', gap)
                if indicator_match:
                    indicator = indicator_match.group(1)
                    
                    keywords.append({
                        "text": f"{indicator} graphic tee",
                        "relevance": 0.8,
                        "frequency": 1
                    })
    
    # Remove duplicates and sort by relevance
    unique_keywords = {}
    for kw in keywords:
        text = kw["text"]
        if text not in unique_keywords or kw["relevance"] > unique_keywords[text]["relevance"]:
            unique_keywords[text] = kw
    
    return sorted(unique_keywords.values(), key=lambda k: k["relevance"], reverse=True)


@function_tool
async def detect_market_gap(serp_results: Dict[str, Any], intent_type: str) -> Dict[str, Any]:
    """
    Analyze SERP results to detect market gaps and opportunities.
    
    This tool identifies unaddressed needs or opportunities in search results
    for POD graphic tees, evaluates the opportunity size, and assesses
    competition levels.
    
    Args:
        serp_results: The SERP data to analyze for gaps.
        intent_type: The classified intent type (transactional, informational, etc.).
        
    Returns:
        Dictionary containing market gap analysis with opportunity score and related keywords.
    """
    try:
        # Extract POD-specific terms
        pod_terms = extract_pod_specific_terms(serp_results)
        
        # Skip analysis if no POD relevance
        if not pod_terms:
            result = MarketGapResult(
                detected=False,
                description="No POD graphic tee relevance detected in search results",
                opportunity_score=0.0,
                competition_level=0.0,
                related_keywords=[]
            )
            return result.dict()
        
        # Identify content or product gaps
        gaps = identify_content_gaps(serp_results, intent_type)
        
        # If gaps were found, analyze the opportunity
        if gaps:
            # Calculate opportunity score
            opportunity_score = calculate_opportunity_score(gaps, serp_results, pod_terms)
            
            # Calculate competition level
            competition_level = calculate_competition_level(serp_results)
            
            # Extract gap-related keywords
            gap_keywords = extract_gap_keywords(gaps)
            
            # Create gap description
            gap_description = "Market gap detected: " + "; ".join(gaps[:3])
            if len(gaps) > 3:
                gap_description += f"; and {len(gaps) - 3} more opportunities"
            
            # Create result
            result = MarketGapResult(
                detected=True,
                description=gap_description,
                opportunity_score=opportunity_score,
                competition_level=competition_level,
                related_keywords=gap_keywords
            )
        else:
            # No gaps found
            result = MarketGapResult(
                detected=False,
                description="No significant market gaps detected for POD graphic tees",
                opportunity_score=0.1,
                competition_level=0.8,
                related_keywords=[]
            )
        
        return result.dict()
    except Exception as e:
        raise ValueError(f"Market gap detection failed: {str(e)}") 