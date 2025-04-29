"""
Shared test fixtures for the AI SERP Keyword Research Agent.

This module contains shared test fixtures that can be used across multiple test files.
These fixtures represent common test data structures and mock objects that may be
needed in various tests.
"""
import json
import uuid
from typing import Dict, Any, List

# SERP test data
SERP_RESULT_TRANSACTIONAL = {
    "search_term": "buy graphic tees",
    "organic_results": [
        {
            "position": 1,
            "title": "Buy Funny Graphic Tees Online - 20% Off Today",
            "url": "https://www.example-shop.com/graphic-tees",
            "domain": "example-shop.com",
            "snippet": "Shop our collection of funny graphic tees. Free shipping on orders over $50. Sizes S-3XL available."
        },
        {
            "position": 2,
            "title": "Graphic T-Shirts - Amazon.com",
            "url": "https://www.amazon.com/graphic-tshirts",
            "domain": "amazon.com",
            "snippet": "Results 1-48 of 100000+ results for graphic t-shirts. Price: $15.99. Free shipping available."
        },
        {
            "position": 3,
            "title": "Graphic Tees for Men and Women - Buy Online | Etsy",
            "url": "https://www.etsy.com/c/clothing/mens-clothing/shirts-and-tees/t-shirts",
            "domain": "etsy.com",
            "snippet": "Shop for unique graphic tees on Etsy. Thousands of designs available. Support independent sellers."
        }
    ],
    "features": [
        {
            "type": "shopping_ads",
            "position": 1,
            "data": {
                "products": 4
            }
        }
    ]
}

SERP_RESULT_INFORMATIONAL = {
    "search_term": "how to style graphic tees",
    "organic_results": [
        {
            "position": 1,
            "title": "10 Ways to Style Graphic Tees - Fashion Blog",
            "url": "https://www.fashion-blog.com/how-to-style-graphic-tees",
            "domain": "fashion-blog.com",
            "snippet": "Learn how to style graphic tees for any occasion. From casual to dressy, these tips will help you create the perfect outfit."
        },
        {
            "position": 2,
            "title": "The Ultimate Guide to Styling Graphic T-Shirts - Style Tips",
            "url": "https://www.styletips.com/guides/graphic-tshirts",
            "domain": "styletips.com",
            "snippet": "Our comprehensive guide to styling graphic tees. Learn what works and what doesn't with this essential wardrobe item."
        },
        {
            "position": 3,
            "title": "How to Wear Graphic Tees: A Complete Guide - Reddit",
            "url": "https://www.reddit.com/r/fashion/comments/graphic-tees-guide",
            "domain": "reddit.com",
            "snippet": "Read community advice on how to style graphic tees for different body types and occasions. Tips and example outfits included."
        }
    ],
    "features": [
        {
            "type": "featured_snippet",
            "position": 0,
            "data": {
                "snippet": "1. Pair with jeans for a casual look\n2. Layer under a blazer for business casual\n3. Tuck into a skirt for feminine style"
            }
        },
        {
            "type": "people_also_ask",
            "position": 3,
            "data": {
                "questions": [
                    "How to style an oversized graphic tee?",
                    "Can you wear graphic tees to work?",
                    "How to style vintage graphic tees?"
                ]
            }
        }
    ]
}

SERP_RESULT_NAVIGATIONAL = {
    "search_term": "threadless official site",
    "organic_results": [
        {
            "position": 1,
            "title": "Threadless | Artist Shop | Homepage",
            "url": "https://www.threadless.com/",
            "domain": "threadless.com",
            "snippet": "The official home of Threadless. Shop graphic t-shirts designed by artists. Discover new art and artists from our global community."
        },
        {
            "position": 2,
            "title": "Login - Threadless",
            "url": "https://www.threadless.com/login",
            "domain": "threadless.com",
            "snippet": "Sign in to your Threadless account. Access your orders, designs, and artist shop."
        },
        {
            "position": 3,
            "title": "Threadless - About Us",
            "url": "https://www.threadless.com/about",
            "domain": "threadless.com",
            "snippet": "Learn about Threadless, our mission, and how we support artists worldwide. Official information about our company."
        }
    ],
    "features": []
}

SERP_RESULT_EXPLORATORY = {
    "search_term": "graphic tee ideas",
    "organic_results": [
        {
            "position": 1,
            "title": "50 Best Graphic Tee Ideas You'll Love in 2023",
            "url": "https://www.designinspo.com/graphic-tee-ideas-2023",
            "domain": "designinspo.com",
            "snippet": "Browse our collection of 50 creative graphic tee designs. From retro to modern, find inspiration for your next favorite shirt."
        },
        {
            "position": 2,
            "title": "Trending Graphic Tee Designs - Pinterest",
            "url": "https://www.pinterest.com/explore/graphic-tee-designs",
            "domain": "pinterest.com",
            "snippet": "Discover graphic tee ideas, designs, and inspiration on Pinterest. Save your favorites and get inspired."
        },
        {
            "position": 3,
            "title": "Graphic Tee Collections - Summer 2023 | Inspiration Gallery",
            "url": "https://www.teeinspo.com/collections/summer-2023",
            "domain": "teeinspo.com",
            "snippet": "Explore our curated collections of graphic tees for Summer 2023. Find unique designs across various styles and themes."
        }
    ],
    "features": [
        {
            "type": "image_pack",
            "position": 2,
            "data": {
                "images": 12
            }
        },
        {
            "type": "related_searches",
            "position": 8,
            "data": {
                "searches": [
                    "vintage graphic tee ideas",
                    "minimalist graphic tee designs",
                    "funny graphic tee sayings",
                    "custom graphic tee creators"
                ]
            }
        }
    ]
}

# Intent analysis results
INTENT_ANALYSIS_TRANSACTIONAL = {
    "main_keyword": "graphic tees",
    "secondary_keywords": ["buy", "online", "shop", "price", "free shipping"],
    "intent_type": "transactional",
    "confidence": 0.92
}

INTENT_ANALYSIS_INFORMATIONAL = {
    "main_keyword": "style graphic tees",
    "secondary_keywords": ["how to", "ways", "guide", "tips", "outfit"],
    "intent_type": "informational",
    "confidence": 0.89
}

INTENT_ANALYSIS_NAVIGATIONAL = {
    "main_keyword": "threadless",
    "secondary_keywords": ["official", "site", "homepage", "login"],
    "intent_type": "navigational",
    "confidence": 0.95
}

INTENT_ANALYSIS_EXPLORATORY = {
    "main_keyword": "graphic tee ideas",
    "secondary_keywords": ["designs", "inspiration", "collection", "trending"],
    "intent_type": "exploratory",
    "confidence": 0.87
}

# Market gap analysis results
MARKET_GAP_PRESENT = {
    "detected": True,
    "description": "Limited personalized dad shirts with profession themes",
    "opportunity_score": 0.78,
    "competition_level": "medium",
    "supporting_evidence": [
        "No top results focused on profession-specific dad tees",
        "Related searches show interest in personalized options",
        "Shopping ads show generic dad shirts only"
    ]
}

MARKET_GAP_ABSENT = {
    "detected": False,
    "description": "",
    "opportunity_score": 0.12,
    "competition_level": "high",
    "supporting_evidence": [
        "Top results already cover major graphic tee categories",
        "High presence of established e-commerce sites",
        "Diverse product selection visible in shopping results"
    ]
}

# Recommendation examples
RECOMMENDATIONS_TRANSACTIONAL = [
    {
        "tactic_type": "product_page_optimization",
        "description": "Create product pages targeting 'profession + dad shirt' keywords",
        "priority": 1,
        "confidence": 0.85
    },
    {
        "tactic_type": "listing_optimization",
        "description": "Include 'funny' and 'gift' in product titles for dad graphic tees",
        "priority": 2,
        "confidence": 0.82
    },
    {
        "tactic_type": "pricing_strategy",
        "description": "Highlight free shipping offers prominently on product pages",
        "priority": 3,
        "confidence": 0.79
    }
]

RECOMMENDATIONS_INFORMATIONAL = [
    {
        "tactic_type": "content_creation",
        "description": "Create a 'How to Style Dad Graphic Tees' guide with outfit examples",
        "priority": 1,
        "confidence": 0.88
    },
    {
        "tactic_type": "featured_snippet_targeting",
        "description": "Structure content with clear headings and list formats to target featured snippets",
        "priority": 2,
        "confidence": 0.84
    },
    {
        "tactic_type": "related_questions",
        "description": "Create FAQ content addressing 'How to wear dad shirts for different occasions'",
        "priority": 3,
        "confidence": 0.76
    }
]

# API response examples
API_RESPONSE_EXAMPLE = {
    "analysis": {
        "main_keyword": "dad graphic tee",
        "secondary_keywords": ["funny dad shirt", "father's day gift"],
        "intent_type": "transactional",
        "confidence": 0.87,
        "serp_features": ["shopping_ads", "image_pack"]
    },
    "market_gap": {
        "detected": True,
        "description": "Limited personalized dad shirts with profession themes"
    },
    "recommendations": [
        {
            "tactic_type": "product_page_optimization",
            "description": "Create product pages targeting 'profession + dad shirt' keywords",
            "priority": 1,
            "confidence": 0.85
        },
        {
            "tactic_type": "content_creation",
            "description": "Develop gift guide content around 'best gifts for dads'",
            "priority": 2,
            "confidence": 0.78
        }
    ]
}

# Helper functions
def generate_search_analysis_record() -> Dict[str, Any]:
    """Generate a random search analysis record for testing."""
    return {
        "id": str(uuid.uuid4()),
        "search_term": "dad graphic tee",
        "main_keyword": "dad t-shirt",
        "secondary_keywords": ["funny dad shirt", "father's day gift"],
        "intent_type": "transactional",
        "has_market_gap": True,
        "confidence": 0.85,
        "created_at": "2023-04-10T12:34:56Z"
    }

def generate_serp_features(analysis_id: str, count: int = 2) -> List[Dict[str, Any]]:
    """Generate a list of SERP features for testing."""
    feature_types = ["shopping_ads", "image_pack", "featured_snippet", "people_also_ask"]
    features = []
    
    for i in range(count):
        features.append({
            "id": str(uuid.uuid4()),
            "analysis_id": analysis_id,
            "feature_type": feature_types[i % len(feature_types)],
            "feature_position": i + 1,
            "feature_data": json.dumps({"example": "data", "position": i + 1}),
            "created_at": "2023-04-10T12:34:56Z"
        })
    
    return features

def generate_recommendations(analysis_id: str, count: int = 3) -> List[Dict[str, Any]]:
    """Generate a list of recommendations for testing."""
    tactic_types = [
        "product_page_optimization", 
        "content_creation", 
        "keyword_targeting", 
        "listing_optimization"
    ]
    
    recommendations = []
    
    for i in range(count):
        recommendations.append({
            "id": str(uuid.uuid4()),
            "analysis_id": analysis_id,
            "tactic_type": tactic_types[i % len(tactic_types)],
            "description": f"Test recommendation {i+1}",
            "priority": i + 1,
            "confidence": 0.9 - (i * 0.05),
            "created_at": "2023-04-10T12:34:56Z"
        })
    
    return recommendations 