# System Patterns

## System Architecture

The AI SERP Keyword Research Agent is built around a multi-agent architecture powered by the OpenAI Agents SDK. The system follows a clean architecture approach with clear separation of concerns:

```
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                         Client/API Layer                       │
│                                                                │
└────────────────┬───────────────────────────┬──────────────────┘
                 │                           │
                 ▼                           ▼
┌────────────────────────────┐   ┌────────────────────────────┐
│                            │   │                            │
│  Input/Output Guardrails   │   │      Health Endpoints      │
│                            │   │                            │
└─────────────┬──────────────┘   └────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│                   Orchestrator Agent (SEO Expert)              │
│                                                                │
└────────┬──────────────────────────────────────────────┬───────┘
         │                                              │
         │                                              │
         ▼                                              ▼
┌─────────────────────┐                        ┌─────────────────────┐
│                     │                        │                     │
│  Intent Analyzer    │                        │ Recommendation      │
│  Agent              │                        │ Agent               │
│                     │                        │                     │
└────────┬────────────┘                        └──────────┬──────────┘
         │                                                │
         │                                                │
         ▼                                                ▼
┌─────────────────────┐                        ┌─────────────────────┐
│                     │                        │                     │
│   SERP API Tool     │                        │   Market Gap Tool   │
│                     │                        │                     │
└─────────────────────┘                        └─────────────────────┘
```

## Key Technical Decisions

### 1. Multi-Agent Approach
- **Decision**: Use specialized agents rather than a single monolithic agent
- **Rationale**: Enables focused expertise in each domain (SEO analysis, intent detection, recommendations)
- **Implementation**: Each agent has tailored instructions, focused tools, and specialized knowledge

### 2. Pipeline Processing Pattern
- **Decision**: Process search terms through a sequential pipeline of stages
- **Rationale**: Enables clean separation of concerns and modular processing
- **Implementation**: Pipeline stages for input validation, SERP retrieval, intent analysis, market gap analysis, recommendation generation, and output formatting

### 3. Repository Pattern for Data Access
- **Decision**: Abstract data access through repository interfaces
- **Rationale**: Enables flexibility in storage implementations and testing
- **Implementation**: Repository interfaces for search analysis, SERP features, and recommendations

### 4. Comprehensive Guardrails
- **Decision**: Implement robust input and output guardrails
- **Rationale**: Ensures system security, prevents misuse, validates inputs/outputs
- **Implementation**: Input validation, content safety checks, recommendation quality checks

### 5. Tracing and Observability
- **Decision**: Implement comprehensive tracing throughout the system
- **Rationale**: Enables debugging, monitoring, and performance optimization
- **Implementation**: Custom trace processors and exporters for agent interactions

### 6. Security Measures
- **Decision**: Implement a multi-layered security approach 
- **Rationale**: Ensures robust protection against common security vulnerabilities
- **Implementation**:
  - Security middleware for input validation and sanitization
  - Environment variable validation with type checking
  - Credential manager for secure API key handling
  - Security review tool for identifying security issues
  - Proper error handling throughout the application

## Agent Design

### 1. SEO Expert Agent (Orchestrator)

#### Purpose
Primary orchestration agent responsible for coordinating the SERP analysis workflow and generating the final analysis.

#### Instructions
```
You are an SEO expert specializing in Print on Demand (POD) graphic tees.
Your task is to analyze SERP data for a given search term to extract valuable SEO insights.

Follow these steps for each analysis:
1. Receive a search term from the user
2. Fetch SERP data using the fetch_serp_data tool
3. Hand off to the Intent Analyzer agent to determine search intent and extract keywords
4. Based on intent analysis, identify if there's a market gap opportunity
5. Hand off to the Recommendation agent to generate SEO tactics
6. Compile all insights into a comprehensive analysis
7. Ensure recommendations are specific to the POD graphic tees niche
8. Return the complete analysis with keywords, intent, market gaps, and recommendations

Important considerations:
- Always prioritize the top 3 results in your analysis
- Pay attention to SERP features (shopping ads, featured snippets, etc.)
- For transactional intent, focus on product page optimization
- For informational/exploratory intent, focus on collection page or content optimization
- Always provide specific, actionable recommendations
```

#### Tools
- `fetch_serp_data(search_term: str, result_count: int = 10)`: Fetches SERP data for a given search term
- `detect_market_gap(serp_results: dict, intent_type: str)`: Analyzes SERP results to detect market gaps
- `extract_serp_features(serp_results: dict)`: Extracts and categorizes SERP features

### 2. Intent Analyzer Agent

#### Purpose
Specialized agent that analyzes SERP data to determine search intent and extract relevant keywords.

#### Instructions
```
You are an Intent Analyzer specializing in POD graphic tee search patterns.
Your task is to analyze SERP data to determine search intent and extract keywords.

Follow these steps for your analysis:
1. Review the complete SERP data (titles, descriptions, URLs)
2. Identify patterns in the top 3 results (prioritize these heavily)
3. Extract the main keyword that best represents the search theme
4. Extract secondary keywords that appear frequently in results
5. Classify the intent as one of the following:
   - Transactional: User is looking to purchase (product results dominate)
   - Informational: User is seeking information (blog posts, guides dominate)
   - Navigational: User is looking for a specific site/brand
   - Exploratory: User is browsing for ideas (collection pages dominate)
6. Look for specific POD indicators (terms like "shirt", "tee", "gift")
7. Analyze SERP features to support your intent classification
8. Assign a confidence score to your classification
9. Return a structured analysis with your findings

Important signals to watch for:
- Shopping ads indicate strong transactional intent
- Featured snippets suggest informational intent
- Image packs for apparel suggest visual shopping intent
- "People also ask" boxes indicate informational needs
- E-commerce domains in top results suggest transactional intent
- Content sites in top results suggest informational intent
```

#### Tools
- `analyze_keywords(text: str)`: Extracts and analyzes keywords from text
- `classify_intent(serp_results: dict)`: Classifies search intent based on SERP patterns
- `detect_serp_patterns(serp_results: dict)`: Identifies common patterns across SERP results

### 3. Recommendation Agent

#### Purpose
Specialized agent that generates SEO tactic recommendations based on intent analysis and market gaps.

#### Instructions
```
You are a Recommendation Agent specializing in SEO tactics for POD graphic tees.
Your task is to generate targeted SEO recommendations based on SERP analysis.

Follow these steps to create your recommendations:
1. Review the intent analysis and market gap findings
2. Consider the specific POD graphic tee niche context
3. For transactional intent:
   - Recommend product page optimization tactics
   - Suggest listing optimization for marketplaces
   - Provide advice on product title/description optimization
4. For informational/exploratory intent:
   - Recommend collection page or content tactics
   - Suggest blog posts, guides, or gift lists
   - Provide advice on category structure
5. When market gaps are detected:
   - Recommend specific ways to address the gap
   - Suggest content or product ideas that fill the gap
   - Prioritize these opportunities
6. Consider SERP features in your recommendations:
   - For featured snippets, recommend Q&A content
   - For shopping ads, suggest PPC strategies
   - For image packs, recommend visual optimization
7. Prioritize your recommendations (1 = highest priority)
8. Assign confidence scores to each recommendation
9. Provide specific, actionable tactics (not generic advice)

Always ensure recommendations are specific to the POD graphic tee niche and the exact search term analyzed.
```

#### Tools
- `generate_recommendations(intent_analysis: dict, market_gap: dict)`: Generates SEO recommendations based on analysis
- `prioritize_tactics(recommendations: list, intent_type: str)`: Prioritizes SEO tactics based on intent
- `format_recommendations(recommendations: list)`: Formats recommendations for presentation

## Processing Pipeline

### Pipeline Stages

We have implemented the core pipeline stages with the following responsibilities:

#### 1. Input Validation Stage
- Validates search term format and content
- Normalizes search term (lowercase, trim whitespace)
- Checks for offensive content
- Integrates with cache service to check for existing analysis

```python
class InputValidationStage(PipelineStage[SearchTerm, SearchTerm]):
    """First stage of the SERP analysis pipeline."""
    
    async def process(self, input_data: SearchTerm, context: Optional[PipelineContext] = None) -> SearchTerm:
        # Normalize search term
        normalized_term = self._normalize_search_term(input_data.term)
        
        # Create normalized SearchTerm
        normalized_input = SearchTerm(term=normalized_term, max_results=input_data.max_results)
        
        # Check cache for existing results
        # Store context values for later stages
        
        return normalized_input
```

#### 2. SERP Retrieval Stage
- Calls external SERP API with retry/backoff logic
- Parses and normalizes response
- Extracts core SERP elements (titles, descriptions, URLs)
- Identifies SERP features (shopping, featured snippets, etc.)
- Handles caching of SERP data

```python
class SerpRetrievalStage(PipelineStage[SearchTerm, Dict[str, Any]]):
    """Second stage of the SERP analysis pipeline."""
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def _fetch_serp_data(self, search_term: str, max_results: int) -> Dict[str, Any]:
        # Fetch SERP data with exponential backoff retry
        return await self._serp_provider.fetch_results(search_term, max_results)
    
    async def process(self, input_data: SearchTerm, context: Optional[PipelineContext] = None) -> Dict[str, Any]:
        # Check cache first
        # Fetch SERP data from API if not cached
        # Extract SERP features
        # Store results in context
        
        return serp_data
```

#### 3. Intent Analysis Stage
- Extracts main and secondary keywords
- Analyzes result patterns to determine intent
- Classifies as transactional, informational, navigational, or exploratory
- Assigns confidence score to classification
- Supports both basic and strategy-based intent classification

```python
class IntentAnalysisStage(PipelineStage[Dict[str, Any], IntentAnalysis]):
    """Third stage of the SERP analysis pipeline."""
    
    async def process(self, input_data: Dict[str, Any], context: Optional[PipelineContext] = None) -> IntentAnalysis:
        # Extract keywords from SERP data
        main_keyword, secondary_keywords = await self._extract_keywords(serp_data, search_term)
        
        # Determine intent type and confidence
        # Either use strategy factory or basic classification
        
        # Create and return the intent analysis
        intent_analysis = IntentAnalysis(
            intent_type=intent_type,
            confidence=confidence,
            main_keyword=main_keyword,
            secondary_keywords=secondary_keywords,
            signals=signals
        )
        
        return intent_analysis
```

#### 4. Market Gap Analysis Stage
- Compares top results for content similarity
- Identifies unaddressed intents or underserved themes
- Detects opportunity gaps for POD graphic tees
- Assesses competition level for various intent types
- Generates gap-specific keywords

```python
class MarketGapAnalysisStage(PipelineStage[IntentAnalysis, MarketGap]):
    """Fourth stage of the SERP analysis pipeline."""
    
    async def process(self, input_data: IntentAnalysis, context: Optional[PipelineContext] = None) -> MarketGap:
        # Analyze SERP data for market gaps based on intent
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
        
        return market_gap
```

#### 5. Recommendation Generation Stage
- Generates SEO tactics based on intent and gaps
- Prioritizes recommendations by potential impact
- Tailors recommendations to POD graphic tee niche
- Assigns confidence scores to recommendations
- Handles both intent-based and gap-based recommendations

```python
class RecommendationGenerationStage(PipelineStage[MarketGap, RecommendationSet]):
    """Fifth stage of the SERP analysis pipeline."""
    
    async def process(self, input_data: MarketGap, context: Optional[PipelineContext] = None) -> RecommendationSet:
        # Generate recommendations based on intent type
        intent_recommendations = self._generate_intent_recommendations(intent_analysis, serp_features)
        
        # Generate recommendations based on market gap (if detected)
        gap_recommendations = []
        if market_gap.detected:
            gap_recommendations = self._generate_gap_recommendations(market_gap, intent_analysis)
            
        # Combine and prioritize recommendations
        prioritized_recommendations = self._prioritize_recommendations(
            all_recommendations, intent_analysis, market_gap
        )
        
        # Create recommendation set
        recommendation_set = RecommendationSet(
            recommendations=prioritized_recommendations,
            intent_based=len(intent_recommendations) > 0,
            market_gap_based=len(gap_recommendations) > 0
        )
        
        return recommendation_set
```

#### 6. Output Formatting Stage (To Be Implemented)
- Will compile analysis components into structured output
- Will apply output validation
- Will format for API response
- Will cache results for future reference

### Pipeline Stage Interface

We've implemented a generic pipeline stage interface that provides consistency across all stages:

```python
class PipelineStage(Generic[InputType, OutputType], ABC):
    """Abstract base class for pipeline stages."""
    
    @abstractmethod
    async def process(self, input_data: InputType) -> OutputType:
        """Process the input data and return the output."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this pipeline stage."""
        pass
```

### Pipeline Context

We've implemented a context object for sharing state between pipeline stages:

```python
class PipelineContext:
    """Context object for sharing state between pipeline stages."""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        
    def set(self, key: str, value: Any) -> None:
        """Store a value in the context."""
        self._data[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the context."""
        return self._data.get(key, default)
    
    def contains(self, key: str) -> bool:
        """Check if a key exists in the context."""
        return key in self._data
        
    def remove(self, key: str) -> None:
        """Remove a key from the context."""
        if key in self._data:
            del self._data[key]
```

## Data Flow

### User Input Flow
```