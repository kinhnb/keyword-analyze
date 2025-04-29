"""
Tests for input guardrails.
"""

import pytest
import asyncio
from unittest.mock import MagicMock

from ai_serp_keyword_research.guardrails.input_guardrails import (
    validate_search_term,
    normalize_search_term,
    check_search_term_safety,
    search_term_guardrail,
    SearchTermValidationError,
    SearchTermSafetyError,
)


class TestSearchTermValidation:
    """Tests for search term validation functions."""
    
    def test_valid_search_term(self):
        """Test that valid search terms pass validation."""
        valid_terms = [
            "dad graphic tee",
            "funny t-shirt",
            "mother's day gift shirt",
            "programmer tee",
            "graphic t-shirt for women",
            "Star Wars t-shirt",
            "I love cats shirt",
            "Best dad ever t-shirt",
            "coffee lover shirt",
        ]
        
        for term in valid_terms:
            assert validate_search_term(term) == term
    
    def test_invalid_search_term_empty(self):
        """Test that empty search terms fail validation."""
        with pytest.raises(SearchTermValidationError):
            validate_search_term("")
    
    def test_invalid_search_term_too_short(self):
        """Test that search terms that are too short fail validation."""
        with pytest.raises(SearchTermValidationError):
            validate_search_term("a")
    
    def test_invalid_search_term_too_long(self):
        """Test that search terms that are too long fail validation."""
        with pytest.raises(SearchTermValidationError):
            validate_search_term("a" * 101)
    
    def test_invalid_search_term_invalid_chars(self):
        """Test that search terms with invalid characters fail validation."""
        invalid_terms = [
            "shirt <script>alert(1)</script>",
            "t-shirt | grep password",
            "SELECT * FROM shirts",
            "shirt; DROP TABLE users",
            "shirt\nline break",
        ]
        
        for term in invalid_terms:
            with pytest.raises(SearchTermValidationError):
                validate_search_term(term)


class TestSearchTermNormalization:
    """Tests for search term normalization."""
    
    def test_normalization(self):
        """Test search term normalization."""
        test_cases = [
            ("  Dad Graphic Tee  ", "dad graphic tee"),
            ("T-SHIRT", "t-shirt"),
            ("funny    shirt", "funny shirt"),
            ("Best,Dad,Ever,Shirt", "best,dad,ever,shirt"),
            ("!!!graphic tee!!!", "graphic tee"),
            ("  coffee   lover  ", "coffee lover"),
        ]
        
        for input_term, expected_output in test_cases:
            assert normalize_search_term(input_term) == expected_output


class TestSearchTermSafety:
    """Tests for search term safety checks."""
    
    def test_safe_search_terms(self):
        """Test that safe search terms pass safety checks."""
        safe_terms = [
            "dad graphic tee",
            "funny t-shirt",
            "mother's day gift shirt",
            "programmer tee",
            "graphic t-shirt for women",
            "Star Wars t-shirt",
        ]
        
        for term in safe_terms:
            is_safe, reason, category = check_search_term_safety(term)
            assert is_safe is True
            assert reason is None
            assert category is None
    
    def test_unsafe_search_terms(self):
        """Test that unsafe search terms fail safety checks."""
        unsafe_terms = [
            "porn t-shirt",
            "gambling shirt",
            "illegal drugs tee",
            "xxx graphic tee",
            "hacking tools shirt",
        ]
        
        for term in unsafe_terms:
            is_safe, reason, category = check_search_term_safety(term)
            assert is_safe is False
            assert reason is not None
            assert category is not None
    
    def test_allowed_override_terms(self):
        """Test that allowed override terms pass safety checks."""
        override_terms = [
            "adult size t-shirt",
            "adult fit graphic tee",
            "sex education awareness shirt",
            "crack of dawn morning person shirt",
        ]
        
        for term in override_terms:
            is_safe, reason, category = check_search_term_safety(term)
            assert is_safe is True
            assert reason is None
            assert category is None


class TestSearchTermGuardrail:
    """Tests for the search term guardrail function."""
    
    @pytest.mark.asyncio
    async def test_guardrail_safe_term(self):
        """Test that the guardrail passes safe terms."""
        ctx = MagicMock()
        agent = MagicMock()
        
        result = await search_term_guardrail(ctx, agent, "dad graphic tee")
        
        assert result.tripwire_triggered is False
    
    @pytest.mark.asyncio
    async def test_guardrail_invalid_term(self):
        """Test that the guardrail blocks invalid terms."""
        ctx = MagicMock()
        agent = MagicMock()
        
        result = await search_term_guardrail(ctx, agent, "")
        
        assert result.tripwire_triggered is True
        assert "category" in result.output_info
        assert result.output_info["category"] == "validation"
    
    @pytest.mark.asyncio
    async def test_guardrail_unsafe_term(self):
        """Test that the guardrail blocks unsafe terms."""
        ctx = MagicMock()
        agent = MagicMock()
        
        result = await search_term_guardrail(ctx, agent, "porn t-shirt")
        
        assert result.tripwire_triggered is True
        assert "category" in result.output_info 