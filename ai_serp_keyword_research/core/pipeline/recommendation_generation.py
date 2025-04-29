"""
Recommendation generation stage for the SERP analysis pipeline.

This module implements the fifth stage of the pipeline, which generates
SEO tactic recommendations based on intent analysis and market gap detection.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

from ai_serp_keyword_research.core.models.analysis import IntentAnalysis, MarketGap, SerpFeature
from ai_serp_keyword_research.core.models.recommendations import RecommendationSet, Recommendation, TacticType
from ai_serp_keyword_research.core.pipeline.base import PipelineContext, PipelineStage

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationGenerationStage(PipelineStage[MarketGap, RecommendationSet]):
    """
    Fifth stage of the SERP analysis pipeline.
    
    This stage is responsible for:
    1. Generating SEO tactic recommendations based on intent and gaps
    2. Prioritizing recommendations by potential impact
    3. Assigning confidence scores to recommendations
    """
    
    @property
    def name(self) -> str:
        return "Recommendation Generation Stage"
        
    async def process(self, input_data: MarketGap, context: Optional[PipelineContext] = None) -> RecommendationSet:
        """
        Generate SEO recommendations based on analysis.
        
        Args:
            input_data: The market gap analysis from previous stage.
            context: Optional pipeline context for sharing state.
            
        Returns:
            A set of prioritized recommendations.
        """
        if context is None:
            context = PipelineContext()
            
        market_gap = input_data
        intent_analysis = context.get("intent_analysis")
        serp_features = context.get("serp_features", [])
        search_term = context.get("normalized_term", "")
        
        logger.info(f"Generating recommendations for search term: {search_term}")
        
        # Generate recommendations based on intent type
        intent_recommendations = self._generate_intent_recommendations(
            intent_analysis, serp_features
        )
        
        # Generate recommendations based on market gap (if detected)
        gap_recommendations = []
        if market_gap.detected:
            gap_recommendations = self._generate_gap_recommendations(
                market_gap, intent_analysis
            )
            
        # Combine recommendations
        all_recommendations = intent_recommendations + gap_recommendations
        
        # Prioritize and score recommendations
        prioritized_recommendations = self._prioritize_recommendations(
            all_recommendations, intent_analysis, market_gap
        )
        
        # Create recommendation set
        recommendation_set = RecommendationSet(
            recommendations=prioritized_recommendations,
            intent_based=len(intent_recommendations) > 0,
            market_gap_based=len(gap_recommendations) > 0
        )
        
        # Store in context
        context.set("recommendations", recommendation_set)
        
        return recommendation_set
        
    def _generate_intent_recommendations(
        self, intent_analysis: IntentAnalysis, serp_features: List[SerpFeature]
    ) -> List[Recommendation]:
        """
        Generate recommendations based on search intent.
        
        Args:
            intent_analysis: The intent analysis results.
            serp_features: The SERP features detected.
            
        Returns:
            List of recommendations based on intent.
        """
        recommendations = []
        
        if not intent_analysis:
            return recommendations
            
        intent_type = intent_analysis.intent_type
        main_keyword = intent_analysis.main_keyword.text
        secondary_keywords = [k.text for k in intent_analysis.secondary_keywords]
        
        # Generate intent-specific recommendations
        if intent_type == "transactional":
            # Product-focused recommendations for transactional intent
            
            # Recommendation 1: Product page optimization
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description=f"Create optimized product pages targeting '{main_keyword}' as the primary keyword",
                    priority=1,  # Highest priority
                    confidence=0.9,
                    supporting_evidence=[
                        f"Transactional intent detected with {intent_analysis.confidence:.0%} confidence",
                        "Product pages perform best for transactional searches",
                    ]
                )
            )
            
            # Recommendation 2: Secondary keyword usage
            if secondary_keywords:
                recommendations.append(
                    Recommendation(
                        tactic_type=TacticType.KEYWORD_TARGETING,
                        description=f"Include secondary keywords ({', '.join(secondary_keywords[:3])}) in product descriptions",
                        priority=2,
                        confidence=0.85,
                        supporting_evidence=[
                            f"Secondary keywords appear in {len(secondary_keywords)} SERP results"
                        ]
                    )
                )
                
            # Recommendation 3: Marketplace optimization
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.MARKETPLACE_OPTIMIZATION,
                    description=f"Optimize POD marketplace listings with '{main_keyword}' in titles and tags",
                    priority=3,
                    confidence=0.8,
                    supporting_evidence=[
                        "Marketplace presence important for transactional searches"
                    ]
                )
            )
            
            # Check for shopping ads
            has_shopping_ads = any(feature.feature_type == "shopping_ads" for feature in serp_features)
            if has_shopping_ads:
                recommendations.append(
                    Recommendation(
                        tactic_type=TacticType.PPC_STRATEGY,
                        description=f"Set up Google Shopping campaigns targeting '{main_keyword}'",
                        priority=2,
                        confidence=0.75,
                        supporting_evidence=[
                            "Shopping ads present in search results"
                        ]
                    )
                )
                
        elif intent_type == "informational":
            # Content-focused recommendations for informational intent
            
            # Recommendation 1: Content creation
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.CONTENT_CREATION,
                    description=f"Create a comprehensive guide about '{main_keyword}' with focus on POD graphic tees",
                    priority=1,
                    confidence=0.9,
                    supporting_evidence=[
                        f"Informational intent detected with {intent_analysis.confidence:.0%} confidence",
                        "Content-rich pages perform best for informational searches"
                    ]
                )
            )
            
            # Recommendation 2: Featured snippet optimization
            has_featured_snippet = any(feature.feature_type == "featured_snippet" for feature in serp_features)
            if has_featured_snippet:
                recommendations.append(
                    Recommendation(
                        tactic_type=TacticType.SNIPPET_OPTIMIZATION,
                        description=f"Create Q&A content for '{main_keyword}' that targets the featured snippet",
                        priority=2,
                        confidence=0.85,
                        supporting_evidence=[
                            "Featured snippet present in search results"
                        ]
                    )
                )
                
            # Recommendation 3: Secondary topic coverage
            if secondary_keywords:
                recommendations.append(
                    Recommendation(
                        tactic_type=TacticType.CONTENT_CREATION,
                        description=f"Create subtopic sections covering related themes: {', '.join(secondary_keywords[:3])}",
                        priority=3,
                        confidence=0.8,
                        supporting_evidence=[
                            f"Related topics appear in {len(secondary_keywords)} SERP results"
                        ]
                    )
                )
                
        elif intent_type == "exploratory":
            # Inspiration/collection recommendations for exploratory intent
            
            # Recommendation 1: Collection page
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.COLLECTION_PAGE_OPTIMIZATION,
                    description=f"Create a visually rich collection page for '{main_keyword}' graphic tees",
                    priority=1,
                    confidence=0.9,
                    supporting_evidence=[
                        f"Exploratory intent detected with {intent_analysis.confidence:.0%} confidence",
                        "Collection pages perform best for exploratory searches"
                    ]
                )
            )
            
            # Recommendation 2: Image optimization
            has_image_pack = any(feature.feature_type == "image_pack" for feature in serp_features)
            if has_image_pack:
                recommendations.append(
                    Recommendation(
                        tactic_type=TacticType.IMAGE_OPTIMIZATION,
                        description=f"Optimize product images to appear in image results for '{main_keyword}'",
                        priority=2,
                        confidence=0.85,
                        supporting_evidence=[
                            "Image pack present in search results"
                        ]
                    )
                )
                
            # Recommendation 3: Design variety
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.PRODUCT_PAGE_OPTIMIZATION,
                    description=f"Create diverse design variations for '{main_keyword}' to appeal to exploratory searchers",
                    priority=3,
                    confidence=0.8,
                    supporting_evidence=[
                        "Exploratory searchers are looking for variety and inspiration"
                    ]
                )
            )
            
        elif intent_type == "navigational":
            # Brand/navigational recommendations
            
            # Recommendation 1: Brand awareness
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.TECHNICAL_SEO,
                    description=f"Ensure your brand appears for '{main_keyword}' by strengthening brand association",
                    priority=1,
                    confidence=0.85,
                    supporting_evidence=[
                        f"Navigational intent detected with {intent_analysis.confidence:.0%} confidence"
                    ]
                )
            )
            
            # Recommendation 2: Link building
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.LINK_BUILDING,
                    description=f"Develop backlinks from POD and graphic tee communities related to '{main_keyword}'",
                    priority=2,
                    confidence=0.75,
                    supporting_evidence=[
                        "Link strength important for navigational visibility"
                    ]
                )
            )
            
        return recommendations
        
    def _generate_gap_recommendations(
        self, market_gap: MarketGap, intent_analysis: IntentAnalysis
    ) -> List[Recommendation]:
        """
        Generate recommendations based on market gaps.
        
        Args:
            market_gap: The market gap analysis.
            intent_analysis: The intent analysis results.
            
        Returns:
            List of recommendations based on market gaps.
        """
        recommendations = []
        
        if not market_gap.detected:
            return recommendations
            
        gap_description = market_gap.description
        opportunity_score = market_gap.opportunity_score
        related_keywords = market_gap.related_keywords or []
        
        # Generate base recommendation for the identified gap
        # Prioritize higher for higher opportunity scores
        priority = max(1, int(10 * (1 - opportunity_score))) if opportunity_score else 1
        confidence = opportunity_score if opportunity_score else 0.7
        
        # Base recommendation from gap description
        base_recommendation = Recommendation(
            tactic_type=self._determine_gap_tactic_type(intent_analysis.intent_type),
            description=f"Target the market gap: {gap_description}",
            priority=priority,
            confidence=confidence,
            supporting_evidence=[
                f"Market gap detected with {opportunity_score:.0%} opportunity score",
                f"Competition level: {market_gap.competition_level:.0%}"
            ]
        )
        recommendations.append(base_recommendation)
        
        # Add specific keyword recommendations if available
        if related_keywords:
            keyword_texts = [k.text for k in related_keywords[:3]]
            
            recommendations.append(
                Recommendation(
                    tactic_type=TacticType.KEYWORD_TARGETING,
                    description=f"Target gap-specific keywords: {', '.join(keyword_texts)}",
                    priority=priority + 1,
                    confidence=confidence - 0.05,
                    supporting_evidence=[
                        "Keywords generated based on identified market gap"
                    ]
                )
            )
            
        return recommendations
        
    def _determine_gap_tactic_type(self, intent_type: str) -> TacticType:
        """
        Determine the most appropriate tactic type for a gap based on intent.
        
        Args:
            intent_type: The search intent type.
            
        Returns:
            The most appropriate tactic type for the gap.
        """
        if intent_type == "transactional":
            return TacticType.PRODUCT_PAGE_OPTIMIZATION
        elif intent_type == "informational":
            return TacticType.CONTENT_CREATION
        elif intent_type == "exploratory":
            return TacticType.COLLECTION_PAGE_OPTIMIZATION
        else:
            return TacticType.KEYWORD_TARGETING
            
    def _prioritize_recommendations(
        self, recommendations: List[Recommendation], 
        intent_analysis: IntentAnalysis, 
        market_gap: MarketGap
    ) -> List[Recommendation]:
        """
        Prioritize and refine recommendation scores.
        
        Args:
            recommendations: The list of recommendations to prioritize.
            intent_analysis: The intent analysis results.
            market_gap: The market gap analysis.
            
        Returns:
            Prioritized list of recommendations.
        """
        # Check for empty recommendations list
        if not recommendations:
            return []
            
        # Get the base priority and confidence values
        intent_confidence = intent_analysis.confidence if intent_analysis else 0.0
        
        # If we detected a high-opportunity market gap, prioritize those recommendations
        market_gap_priority = False
        if market_gap and market_gap.detected and market_gap.opportunity_score and market_gap.opportunity_score > 0.7:
            market_gap_priority = True
            
        # Adjust priorities based on our findings
        adjusted_recommendations = []
        
        for rec in recommendations:
            # Start with the recommendation's current values
            priority = rec.priority
            confidence = rec.confidence
            
            # Adjust based on intent confidence
            confidence = min(confidence, intent_confidence + 0.1)
            
            # If this is a market gap recommendation and we have high opportunity, increase priority
            if market_gap_priority and "market gap" in rec.description.lower():
                priority = max(1, priority - 1)  # Lower priority number = higher priority
                
            # Create a new recommendation with adjusted values
            adjusted_rec = Recommendation(
                tactic_type=rec.tactic_type,
                description=rec.description,
                priority=priority,
                confidence=confidence,
                supporting_evidence=rec.supporting_evidence,
                estimated_effort=rec.estimated_effort
            )
            
            adjusted_recommendations.append(adjusted_rec)
            
        # The RecommendationSet model will automatically sort by priority
        return adjusted_recommendations 