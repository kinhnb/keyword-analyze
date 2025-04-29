"""
Keyword analysis tools for the AI SERP Keyword Research Agent.

These tools provide functionality to extract and analyze keywords from
text content, including frequency analysis and relevance scoring.
"""

import re
from typing import Dict, Any, List, Tuple
from collections import Counter

from agents import function_tool
from pydantic import BaseModel, Field


class KeywordAnalysisResult(BaseModel):
    """Model representing keyword analysis results."""
    main_keyword: Dict[str, Any] = Field(..., description="Primary keyword detected")
    secondary_keywords: List[Dict[str, Any]] = Field(..., description="Secondary keywords detected")
    keyword_count: int = Field(..., description="Total number of keywords detected")
    pod_relevance: float = Field(..., description="Relevance to POD graphic tees (0.0-1.0)")


def calculate_pod_relevance(keyword: str) -> float:
    """
    Calculate relevance score of a keyword to POD graphic tees.
    
    Args:
        keyword: The keyword to score.
        
    Returns:
        Relevance score between 0.0 and 1.0.
    """
    # Terms relevant to POD graphic tees
    pod_terms = {
        "shirt": 1.0,
        "tee": 1.0,
        "t-shirt": 1.0,
        "graphic": 0.9,
        "print": 0.8,
        "design": 0.8,
        "custom": 0.7,
        "personalized": 0.7,
        "funny": 0.6,
        "gift": 0.5,
        "apparel": 0.8,
        "clothing": 0.7,
        "fashion": 0.5,
        "trendy": 0.4,
        "cool": 0.4,
        "vintage": 0.5
    }
    
    # Check for presence of terms in the keyword
    relevance = 0.0
    keyword_lower = keyword.lower()
    
    # Check each term and add its relevance score if found
    for term, score in pod_terms.items():
        if term in keyword_lower:
            relevance = max(relevance, score)
    
    return relevance


def extract_ngrams(text: str, n_values: List[int] = [1, 2, 3]) -> Dict[str, int]:
    """
    Extract n-grams (phrases of 1-3 words) from text with their frequencies.
    
    Args:
        text: The text to extract n-grams from.
        n_values: The n-gram sizes to extract.
        
    Returns:
        Dictionary of n-grams with their frequencies.
    """
    # Normalize text
    text = text.lower()
    # Remove special characters and excess whitespace
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    words = text.split()
    ngrams = {}
    
    # Generate n-grams for each specified size
    for n in n_values:
        if n <= len(words):
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                if ngram in ngrams:
                    ngrams[ngram] += 1
                else:
                    ngrams[ngram] = 1
                    
    return ngrams


def calculate_relevance(ngram: str, frequency: int, total_ngrams: int, position_weight: float = 1.0) -> float:
    """
    Calculate relevance score for an n-gram.
    
    Args:
        ngram: The n-gram to score.
        frequency: The frequency of the n-gram.
        total_ngrams: Total number of n-grams extracted.
        position_weight: Weight based on position in text (higher for early occurrences).
        
    Returns:
        Relevance score between 0.0 and 1.0.
    """
    # Basic frequency relevance
    frequency_score = min(frequency / (total_ngrams * 0.1), 1.0)
    
    # Length bonus (multi-word phrases are often more specific)
    length_bonus = min(len(ngram.split()) / 3, 1.0) * 0.2
    
    # POD relevance
    pod_score = calculate_pod_relevance(ngram) * 0.5
    
    # Position weight (provided externally)
    position_factor = position_weight * 0.3
    
    # Combined score (capped at 0.95 to leave room for manual adjustments)
    relevance = min((frequency_score * 0.5) + length_bonus + pod_score + position_factor, 0.95)
    
    return relevance


@function_tool
async def analyze_keywords(text: str, max_keywords: int = 5) -> Dict[str, Any]:
    """
    Analyze text to extract and evaluate keywords.
    
    This tool extracts n-grams (word phrases), calculates their frequency,
    and scores their relevance to POD graphic tees.
    
    Args:
        text: The text content to analyze for keywords.
        max_keywords: Maximum number of secondary keywords to return.
        
    Returns:
        Dictionary containing main and secondary keywords with relevance scores.
    """
    try:
        # Extract n-grams (1-3 word phrases)
        ngrams = extract_ngrams(text)
        
        # Filter out very common words if they're single words
        stopwords = {"and", "the", "for", "with", "this", "that", "you", "not", "are", "from"}
        filtered_ngrams = {k: v for k, v in ngrams.items() if not (k in stopwords and len(k.split()) == 1)}
        
        # Calculate total for relative frequency
        total_ngrams = sum(filtered_ngrams.values())
        
        # Sort and convert to list of (ngram, frequency) tuples
        sorted_ngrams = sorted(filtered_ngrams.items(), key=lambda x: x[1], reverse=True)
        
        # Calculate relevance scores for each n-gram
        keywords = []
        for i, (ngram, frequency) in enumerate(sorted_ngrams):
            # Position weight decreases as we go down the list
            position_weight = 1.0 - (i / len(sorted_ngrams)) if sorted_ngrams else 1.0
            
            relevance = calculate_relevance(ngram, frequency, total_ngrams, position_weight)
            
            keywords.append({
                "text": ngram,
                "relevance": relevance,
                "frequency": frequency,
                "pod_relevance": calculate_pod_relevance(ngram)
            })
        
        # Select main keyword (highest relevance)
        main_keyword = keywords[0] if keywords else {
            "text": "",
            "relevance": 0.0,
            "frequency": 0,
            "pod_relevance": 0.0
        }
        
        # Select secondary keywords (next N highest relevance, excluding main)
        secondary_keywords = keywords[1:max_keywords+1] if len(keywords) > 1 else []
        
        # Create response
        result = KeywordAnalysisResult(
            main_keyword=main_keyword,
            secondary_keywords=secondary_keywords,
            keyword_count=len(keywords),
            pod_relevance=max([kw.get("pod_relevance", 0.0) for kw in keywords]) if keywords else 0.0
        )
        
        return result.dict()
    except Exception as e:
        raise ValueError(f"Keyword analysis failed: {str(e)}") 