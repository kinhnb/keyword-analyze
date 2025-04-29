"""
Market gap analysis stage for the SERP analysis pipeline.

This module implements the fourth stage of the pipeline, which analyzes
SERP results to identify market gaps and opportunities.
"""

import logging
from typing import Dict, List, Optional, Any

from ai_serp_keyword_research.core.models.analysis import IntentAnalysis, Keyword, MarketGap
from ai_serp_keyword_research.core.pipeline.base import PipelineContext, PipelineStage

# Configure logging
logger = logging.getLogger(__name__)


class MarketGapAnalysisStage(PipelineStage[IntentAnalysis, MarketGap]):
    """
    Fourth stage of the SERP analysis pipeline.
    
    This stage is responsible for:
    1. Analyzing SERP similarity among top results
    2. Identifying untapped needs or opportunities
    3. Detecting gaps specific to POD graphic tees
    4. Assessing competition level for identified opportunities
    """
    
    @property
    def name(self) -> str:
        return "Market Gap Analysis Stage"
        
    async def process(self, input_data: IntentAnalysis, context: Optional[PipelineContext] = None) -> MarketGap:
        """
        Process intent analysis to identify market gaps.
        
        Args:
            input_data: The intent analysis from the previous stage.
            context: Optional pipeline context for sharing state.
            
        Returns:
            Market gap analysis.
        """
        if context is None:
            context = PipelineContext()
            
        intent_analysis = input_data
        serp_data = context.get("serp_data", {})
        search_term = context.get("normalized_term", "")
        
        logger.info(f"Analyzing market gaps for search term: {search_term}")
        
        # Analyze SERP data for market gaps
        gap_detected, gap_description, opportunity_score, competition_level, related_keywords = (
            self._analyze_market_gaps(serp_data, intent_analysis)
        )
        
        # Create market gap model
        market_gap = MarketGap(
            detected=gap_detected,
            description=gap_description,
            opportunity_score=opportunity_score,
            competition_level=competition_level,
            related_keywords=related_keywords
        )
        
        # Store in context
        context.set("market_gap", market_gap)
        
        return market_gap
        
    def _analyze_market_gaps(self, serp_data: Dict[str, Any], intent_analysis: IntentAnalysis) -> tuple:
        """
        Analyze SERP data to identify market gaps and opportunities.
        
        Args:
            serp_data: The SERP response data.
            intent_analysis: The intent analysis results.
            
        Returns:
            Tuple of (gap_detected, description, opportunity_score, competition_level, related_keywords).
        """
        # Default values
        gap_detected = False
        gap_description = None
        opportunity_score = None
        competition_level = None
        related_keywords = []
        
        # Get the organic results
        organic_results = serp_data.get("organic_results", [])
        
        # Skip if we don't have enough results to analyze
        if len(organic_results) < 3:
            return gap_detected, gap_description, opportunity_score, competition_level, related_keywords
            
        # Extract titles, snippets, and URLs from top results
        top_results = organic_results[:5] if len(organic_results) >= 5 else organic_results
        
        titles = [result.get("title", "").lower() for result in top_results]
        snippets = [result.get("snippet", "").lower() for result in top_results]
        domains = [result.get("domain", "") for result in top_results]
        
        # Analyze result similarity and domain types
        similarity_score = self._calculate_result_similarity(titles, snippets)
        domain_diversity = len(set(domains)) / len(domains)
        
        # Check for POD-specific terms in the search results
        pod_terms = ["print on demand", "pod", "graphic tee", "t-shirt", "shirt", "apparel", "clothing"]
        pod_presence = sum(any(term in title or term in snippet for term in pod_terms) 
                         for title, snippet in zip(titles, snippets)) / len(titles)
                         
        # Check for niche-specific gaps based on intent type
        intent_type = intent_analysis.intent_type
        
        if intent_type == "transactional":
            # For transactional intent, look for product gaps
            
            # Check if POD shops are prominently represented
            pod_presence_threshold = 0.4  # At least 40% of results should be POD-related
            
            if pod_presence < pod_presence_threshold:
                # Gap: Limited POD representation for this search term
                gap_detected = True
                gap_description = f"Limited POD graphic tee representation for '{intent_analysis.main_keyword.text}'"
                opportunity_score = 0.7 + (0.3 * (1 - pod_presence))  # Higher score for lower representation
                competition_level = 0.3 + (0.6 * similarity_score)  # Higher similarity indicates more competition
                
                # Generate related keywords
                related_keywords = self._generate_gap_related_keywords(intent_analysis, "pod")
                
        elif intent_type == "informational":
            # For informational intent, look for content gaps
            
            # Check if there are POD-specific guides or content
            informational_pod_terms = ["how to", "guide", "tips", "best", "top"]
            informational_pod_presence = sum(
                any(info_term in title and any(pod_term in title or pod_term in snippet) 
                    for info_term in informational_pod_terms for pod_term in pod_terms) 
                for title, snippet in zip(titles, snippets)
            ) / len(titles)
            
            if informational_pod_presence < 0.3:  # Less than 30% have informational POD content
                gap_detected = True
                gap_description = f"Limited informational content about '{intent_analysis.main_keyword.text}' for POD graphic tees"
                opportunity_score = 0.8 + (0.15 * (1 - informational_pod_presence))
                competition_level = 0.2 + (0.3 * similarity_score)
                
                # Generate related keywords
                related_keywords = self._generate_gap_related_keywords(intent_analysis, "informational")
                
        elif intent_type == "exploratory":
            # For exploratory intent, look for inspiration or collection gaps
            
            # Check if there are POD-specific collections or galleries
            exploratory_pod_terms = ["ideas", "inspiration", "collection", "gallery", "designs"]
            exploratory_pod_presence = sum(
                any(exp_term in title and any(pod_term in title or pod_term in snippet) 
                    for exp_term in exploratory_pod_terms for pod_term in pod_terms) 
                for title, snippet in zip(titles, snippets)
            ) / len(titles)
            
            if exploratory_pod_presence < 0.3:
                gap_detected = True
                gap_description = f"Limited inspiration/collection content for '{intent_analysis.main_keyword.text}' POD graphic tees"
                opportunity_score = 0.75 + (0.2 * (1 - exploratory_pod_presence))
                competition_level = 0.25 + (0.4 * similarity_score)
                
                # Generate related keywords
                related_keywords = self._generate_gap_related_keywords(intent_analysis, "exploratory")
                
        # If we detected a gap, log it
        if gap_detected:
            logger.info(f"Market gap detected: {gap_description}")
            logger.info(f"Opportunity score: {opportunity_score}, Competition level: {competition_level}")
            
        return gap_detected, gap_description, opportunity_score, competition_level, related_keywords
        
    def _calculate_result_similarity(self, titles: List[str], snippets: List[str]) -> float:
        """
        Calculate similarity score among search results.
        
        Args:
            titles: List of result titles.
            snippets: List of result snippets.
            
        Returns:
            Similarity score between 0 and 1 (higher means more similar).
        """
        # This is a simplified implementation
        # A more sophisticated approach would use NLP techniques like cosine similarity
        
        # Create sets of words from each title and snippet
        title_words = [set(title.split()) for title in titles]
        snippet_words = [set(snippet.split()) for snippet in snippets]
        
        # Calculate average Jaccard similarity between pairs
        title_similarity = self._average_jaccard_similarity(title_words)
        snippet_similarity = self._average_jaccard_similarity(snippet_words)
        
        # Combine title and snippet similarity (weighted toward titles)
        return (0.6 * title_similarity) + (0.4 * snippet_similarity)
        
    def _average_jaccard_similarity(self, word_sets: List[set]) -> float:
        """
        Calculate average Jaccard similarity between sets of words.
        
        Args:
            word_sets: List of sets containing words.
            
        Returns:
            Average Jaccard similarity.
        """
        if len(word_sets) <= 1:
            return 0.0
            
        total_similarity = 0.0
        pair_count = 0
        
        for i in range(len(word_sets)):
            for j in range(i + 1, len(word_sets)):
                set_i = word_sets[i]
                set_j = word_sets[j]
                
                if not set_i or not set_j:
                    continue
                    
                # Jaccard similarity: size of intersection divided by size of union
                intersection = len(set_i.intersection(set_j))
                union = len(set_i.union(set_j))
                
                similarity = intersection / union if union > 0 else 0.0
                total_similarity += similarity
                pair_count += 1
                
        return total_similarity / pair_count if pair_count > 0 else 0.0
        
    def _generate_gap_related_keywords(self, intent_analysis: IntentAnalysis, gap_type: str) -> List[Keyword]:
        """
        Generate keywords related to the identified market gap.
        
        Args:
            intent_analysis: The intent analysis results.
            gap_type: The type of gap identified ("pod", "informational", "exploratory").
            
        Returns:
            List of keywords related to the gap.
        """
        related_keywords = []
        main_keyword = intent_analysis.main_keyword.text
        
        if gap_type == "pod":
            # For POD product gaps, suggest product-oriented keywords
            pod_suffixes = ["shirt", "t-shirt", "graphic tee", "apparel", "clothing"]
            
            for suffix in pod_suffixes:
                keyword_text = f"{main_keyword} {suffix}"
                related_keywords.append(
                    Keyword(
                        text=keyword_text,
                        relevance=0.85,
                        frequency=1
                    )
                )
                
        elif gap_type == "informational":
            # For informational gaps, suggest content-oriented keywords
            info_prefixes = ["how to", "guide to", "tips for", "best"]
            
            for prefix in info_prefixes:
                keyword_text = f"{prefix} {main_keyword} shirt"
                related_keywords.append(
                    Keyword(
                        text=keyword_text,
                        relevance=0.8,
                        frequency=1
                    )
                )
                
        elif gap_type == "exploratory":
            # For exploratory gaps, suggest inspiration-oriented keywords
            explore_terms = ["ideas", "inspiration", "designs", "collection", "gallery"]
            
            for term in explore_terms:
                keyword_text = f"{main_keyword} {term}"
                related_keywords.append(
                    Keyword(
                        text=keyword_text,
                        relevance=0.75,
                        frequency=1
                    )
                )
                
        # Limit to top 5 keywords
        return related_keywords[:5] 