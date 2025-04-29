"""
Input guardrails for the AI SERP Keyword Research Agent.

This module provides guardrails to validate, normalize, and ensure the safety
of user inputs, particularly search terms.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Set, Any
from agents import input_guardrail, GuardrailFunctionOutput

logger = logging.getLogger(__name__)

# Common content safety words to filter/check
UNSAFE_TERMS: Set[str] = {
    "porn", "xxx", "adult", "sex", "explicit", "nsfw", "gambling", "casino",
    "betting", "drugs", "cocaine", "heroin", "illegal", "weapon", "counterfeit",
    "fake id", "hacking", "hack", "crack", "stolen", "pirated", "fraud", 
    "scam", "phishing", "malware", "virus", "violent"
}

# Specifically allowed terms that might overlap with unsafe terms but are valid for POD tees
ALLOWED_OVERRIDE_TERMS: Set[str] = {
    "adult size", "adult fit", "adult wear", "sex positive", 
    "sex education", "sexual health", "crack of dawn"
}

# Categories for content classification
CONTENT_CATEGORIES = {
    "adult": ["porn", "xxx", "adult content", "sexual", "nsfw"],
    "illegal": ["drugs", "weapons", "counterfeit", "illegal", "fraud", "stolen"],
    "harmful": ["hack", "malware", "virus", "phishing", "scam"],
    "gambling": ["gambling", "casino", "betting", "lottery"],
    "violent": ["violent", "kill", "murder", "suicide", "abuse"]
}


class SearchTermValidationError(ValueError):
    """Raised when a search term fails validation checks."""
    pass


class SearchTermSafetyError(ValueError):
    """Raised when a search term fails safety checks."""
    pass


def validate_search_term(search_term: str) -> str:
    """
    Validate a search term against basic criteria.
    
    Args:
        search_term: The search term to validate
        
    Returns:
        The validated search term
        
    Raises:
        SearchTermValidationError: If the search term is invalid
    """
    if not search_term:
        raise SearchTermValidationError("Search term cannot be empty")
    
    if len(search_term) < 2:
        raise SearchTermValidationError("Search term must be at least 2 characters long")
    
    if len(search_term) > 100:
        raise SearchTermValidationError("Search term cannot exceed 100 characters")
    
    # Check for valid characters
    if not re.match(r'^[\w\s\-\'\.,:;!?&+#]+$', search_term):
        raise SearchTermValidationError(
            "Search term contains invalid characters. "
            "Only alphanumeric, spaces, and common punctuation are allowed."
        )
    
    # Check for minimum word requirement
    if len(search_term.split()) < 1:
        raise SearchTermValidationError("Search term must contain at least one word")
    
    return search_term


def normalize_search_term(search_term: str) -> str:
    """
    Normalize a search term for consistent processing.
    
    Args:
        search_term: The search term to normalize
        
    Returns:
        The normalized search term
    """
    # Trim whitespace
    normalized = search_term.strip()
    
    # Replace multiple spaces with a single space
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Lowercase for consistency
    normalized = normalized.lower()
    
    # Remove any leading/trailing punctuation
    normalized = re.sub(r'^[^\w]+|[^\w]+$', '', normalized)
    
    return normalized


def check_search_term_safety(search_term: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Check if a search term is safe for processing.
    
    Args:
        search_term: The search term to check
        
    Returns:
        Tuple of (is_safe, reason, category) where:
            - is_safe: True if the term is safe, False otherwise
            - reason: Reason for flagging (None if safe)
            - category: Category of unsafe content (None if safe)
    """
    normalized_term = search_term.lower()
    
    # First check if this is an allowed override term
    for allowed_term in ALLOWED_OVERRIDE_TERMS:
        if allowed_term in normalized_term:
            # Remove allowed terms from consideration
            normalized_term = normalized_term.replace(allowed_term, " ")
    
    # Check for unsafe terms
    for unsafe_term in UNSAFE_TERMS:
        # Check for exact match or word boundary match
        pattern = rf'\b{re.escape(unsafe_term)}\b'
        if re.search(pattern, normalized_term):
            # Determine category
            category = None
            for cat, terms in CONTENT_CATEGORIES.items():
                if any(term in unsafe_term for term in terms):
                    category = cat
                    break
            
            return False, f"Search term contains unsafe content: '{unsafe_term}'", category
    
    # Check for non-POD graphic tee related queries with specific patterns
    if not any(term in normalized_term for term in ["shirt", "tee", "t-shirt", "tshirt", "graphic", "print", "design", "wear", "apparel", "clothing", "gift"]):
        # This might be off-topic but not necessarily unsafe
        pass
    
    return True, None, None


@input_guardrail
async def search_term_guardrail(ctx: Any, agent: Any, input_text: str) -> GuardrailFunctionOutput:
    """
    Guardrail function to validate and check search term safety.
    
    Args:
        ctx: Context information
        agent: The agent that received the input
        input_text: The input text to check
        
    Returns:
        GuardrailFunctionOutput indicating whether the guardrail was triggered
    """
    try:
        # First validate the format
        validate_search_term(input_text)
        
        # Then check safety
        is_safe, reason, category = check_search_term_safety(input_text)
        if not is_safe:
            logger.warning(f"Search term guardrail triggered: {reason}")
            
            return GuardrailFunctionOutput(
                tripwire_triggered=True,
                output_info={
                    "reason": reason,
                    "category": category or "unknown"
                }
            )
        
        # If both checks pass, input is acceptable
        return GuardrailFunctionOutput(tripwire_triggered=False)
    
    except SearchTermValidationError as e:
        logger.warning(f"Search term validation failed: {str(e)}")
        
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"reason": str(e), "category": "validation"}
        )
    
    except Exception as e:
        logger.error(f"Error in search term guardrail: {str(e)}", exc_info=True)
        
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"reason": "Internal error validating search term", "category": "error"}
        ) 