"""
Unit tests for the input models in the AI SERP Keyword Research Agent.
"""

import pytest
from pydantic import ValidationError

from ai_serp_keyword_research.core.models.input import SearchTerm


class TestSearchTermModel:
    """Test suite for the SearchTerm model."""
    
    def test_valid_search_term(self):
        """Test creating a SearchTerm with valid data."""
        # Valid search term with default max_results
        term = SearchTerm(term="funny dad graphic tee")
        assert term.term == "funny dad graphic tee"
        assert term.max_results == 10
        
        # Valid search term with custom max_results
        term = SearchTerm(term="vintage graphic t-shirt", max_results=20)
        assert term.term == "vintage graphic t-shirt"
        assert term.max_results == 20
        
    def test_term_whitespace_handling(self):
        """Test that whitespace is properly handled in search terms."""
        # Term with leading/trailing whitespace
        term = SearchTerm(term="  dad shirt  ")
        assert term.term == "dad shirt"  # Whitespace should be stripped
        
    def test_term_validation_pod_related(self):
        """Test that search terms must be related to POD graphic tees."""
        # Valid terms (contain POD-related keywords)
        valid_terms = [
            "funny dad shirt",
            "vintage graphic tee",
            "custom t-shirt design",
            "print on demand apparel",
            "graphic design for shirts"
        ]
        
        for valid_term in valid_terms:
            term = SearchTerm(term=valid_term)
            assert term.term == valid_term
            
        # Invalid terms (not related to POD)
        invalid_terms = [
            "best smartphone 2023",
            "italian restaurant near me",
            "car insurance quotes",
            "funny memes"
        ]
        
        for invalid_term in invalid_terms:
            with pytest.raises(ValidationError) as excinfo:
                SearchTerm(term=invalid_term)
            assert "Search term should be related to Print-on-Demand graphic tees" in str(excinfo.value)
            
    def test_term_min_length(self):
        """Test that search terms have a minimum length."""
        # Term too short
        with pytest.raises(ValidationError) as excinfo:
            SearchTerm(term="t")
        assert "ensure this value has at least 3 characters" in str(excinfo.value)
        
    def test_term_max_length(self):
        """Test that search terms have a maximum length."""
        # Term too long
        with pytest.raises(ValidationError) as excinfo:
            SearchTerm(term="t" * 260)
        assert "ensure this value has at most 255 characters" in str(excinfo.value)
        
    def test_max_results_bounds(self):
        """Test bounds for max_results parameter."""
        # Valid bounds
        term = SearchTerm(term="dad shirt", max_results=1)
        assert term.max_results == 1
        
        term = SearchTerm(term="dad shirt", max_results=100)
        assert term.max_results == 100
        
        # Invalid bounds (too low)
        with pytest.raises(ValidationError) as excinfo:
            SearchTerm(term="dad shirt", max_results=0)
        assert "greater than or equal to 1" in str(excinfo.value)
        
        # Invalid bounds (too high)
        with pytest.raises(ValidationError) as excinfo:
            SearchTerm(term="dad shirt", max_results=101)
        assert "less than or equal to 100" in str(excinfo.value) 