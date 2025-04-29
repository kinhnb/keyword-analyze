# Project Overview

## Project Summary
AI SERP Keyword Research Agent for POD Graphic Tees is built on the OpenAI Agents SDK framework. This project leverages the power of AI agents to analyze Google Search Engine Results Pages (SERPs) for search terms related to Print-on-Demand graphic tees, extract key SEO insights, and recommend targeted optimization strategies. The system architecture is designed around the OpenAI Agents SDK core concepts:

- **Multi-Agent Orchestration**: A primary agent specializing in SEO analysis coordinates with specialized intent detection and recommendation agents to comprehensively analyze SERP data
- **Tool-Based Capabilities**: Custom function tools fetch SERP data via external APIs, analyze keyword patterns, detect intent signals, and identify market gaps in search results
- **Knowledge-Driven Intelligence**: The system leverages SEO domain knowledge about transactional vs. exploratory search intent, SERP feature analysis, and POD niche-specific patterns
- **API-First Design**: RESTful endpoints enable seamless integration with existing workflows, marketing tools, and e-commerce platforms

## OpenAI Agents Architecture
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

## Project Structure
The project follows Clean Architecture principles with clear separation of concerns:

```
ai-serp-keyword-research/
├── agents/                   # AI agents powered by OpenAI Agents SDK
│   ├── main_agent.py         # SEO Expert agent that orchestrates the analysis process
│   ├── intent_analyzer.py    # Agent specialized in determining search intent from SERP data
│   ├── keyword_extractor.py  # Agent focused on extracting primary/secondary keywords
│   └── recommender.py        # Agent that recommends SEO tactics based on analysis
├── guardrails/               # Safety and validation mechanisms
│   ├── input_guardrails.py   # Input validation guardrails
│   └── output_guardrails.py  # Output validation guardrails
├── core/                     # Core business logic
│   ├── pipeline/             # SERP analysis workflow pipeline
│   │   ├── fetch_stage.py    # Stage for fetching SERP data
│   │   ├── extract_stage.py  # Stage for extracting keywords and metadata
│   │   └── analyze_stage.py  # Stage for analyzing intent and market gaps
│   ├── strategies/           # Intent analysis strategies
│   │   ├── transaction.py    # Strategy for detecting transactional intent
│   │   └── exploratory.py    # Strategy for detecting exploratory/informational intent
│   └── serp/                 # SERP processing modules
│       ├── features.py       # SERP feature detection (snippets, ads, etc.)
│       └── similarity.py     # SERP result similarity analysis
├── tools/                    # Function tools for agents
│   ├── serp_api.py           # Tool for fetching SERP data from external API
│   ├── keyword_analysis.py   # Tool for keyword extraction and analysis
│   └── market_gap.py         # Tool for detecting market gaps in SERP results
├── data/                     # Data access layer
│   ├── repositories/         # Repository pattern implementations
│   │   ├── search_repo.py    # Repository for search term history
│   │   └── result_repo.py    # Repository for analysis results
│   ├── models/               # Data models
│   │   ├── search.py         # Search term and metadata model
│   │   └── result.py         # Analysis result model
│   └── migrations/           # Database migrations
├── api/                      # API endpoints
│   ├── routes/               # Route definitions
│   │   ├── analyze.py        # Routes for keyword analysis
│   │   └── health.py         # Health check routes
│   ├── middleware/           # API middleware
│   └── schemas/              # Request/response schemas
├── services/                 # External service integrations
│   ├── serp_provider/        # SERP API service integration
│   └── feedback.py           # User feedback collection service
├── orchestration/            # Multi-agent workflow orchestration
│   ├── workflows/            # Defined agent workflows
│   ├── handoffs/             # Agent handoff definitions
│   └── evaluators/           # Output evaluation components
├── tracing/                  # Tracing and monitoring
│   ├── processors/           # Custom trace processors
│   └── exporters/            # Trace export integrations 
├── utils/                    # Utility functions
│   ├── retry/                # Retry/backoff utilities for API calls
│   └── validators/           # Input/output validation utilities
└── tests/                    # Test suite (pytest)
    ├── unit/                 # Unit tests
    ├── agents/               # Agent-specific tests
    └── integration/          # Integration tests
```

## Key Patterns & Concepts

1. **Agent Pattern**:
   - Agents are responsible for specific analysis domains (SEO expertise, intent detection, recommendation)
   - Agents interact through orchestrated workflows with clear handoff points
   - Tools provide domain-specific capabilities like SERP data fetching and keyword analysis
   
```python
# Example agent implementation
from openai_agents_sdk import Agent, Tool, KnowledgeSource

def fetch_serp_data(search_term: str, result_count: int = 10):
    """Fetches SERP data for a given search term with retry/backoff logic."""
    # Implementation with proper error handling and retry logic
    return serp_results

# Define knowledge source
seo_patterns = KnowledgeSource(
    name="SEO Patterns",
    description="Knowledge about SEO patterns for POD graphic tees",
    loader=load_seo_knowledge
)

# Create the agent
seo_expert = Agent(
    name="SEO Expert",
    description="Analyzes SERP data for POD graphic tee keywords",
    instructions="""
    You are an SEO expert specializing in Print on Demand (POD) graphic tees.
    Analyze SERP data for a given search term to:
    1. Extract main and secondary keywords
    2. Identify search intent (transactional vs. exploratory)
    3. Detect market gaps in search results
    4. Recommend SEO tactics based on intent and SERP structure
    
    Always prioritize the top 3 results in your analysis, as they carry more weight.
    Identify SERP features (featured snippets, shopping ads, etc.) and factor them into recommendations.
    """,
    tools=[
        Tool(
            name="fetch_serp_data",
            description="Fetches SERP data for a given search term",
            function=fetch_serp_data
        ),
        # Additional tools...
    ],
    knowledge=[seo_patterns]
)
```

2. **Pipeline Pattern**:
   - Sequential processing of search data through distinct stages
   - Each stage has a specific responsibility in the analysis workflow
   - Data flows through fetch → extract → analyze → recommend stages
   
```python
# Example pipeline implementation
class SerpAnalysisPipeline:
    def __init__(self):
        self.stages = [
            FetchSerpStage(),
            ExtractKeywordsStage(),
            AnalyzeIntentStage(),
            RecommendTacticsStage()
        ]
    
    async def process(self, search_term):
        context = {"search_term": search_term}
        
        for stage in self.stages:
            context = await stage.process(context)
            
            # Exit conditions if needed
            if context.get("error"):
                return context
                
        return context
```

3. **Repository Pattern**:
   - Abstracts data access and persistence mechanisms
   - Provides clean interfaces for storing and retrieving analysis results
   - Supports both in-memory and persistent storage options
   
```python
# Example repository implementation
class ResultRepository:
    def __init__(self, db_session):
        self.db_session = db_session
    
    async def find_by_search_term(self, search_term):
        """Find analysis results by search term."""
        # Implementation
        return results
    
    async def save(self, analysis_result):
        """Save analysis results."""
        # Implementation
        return saved_result
```

4. **Guardrails Pattern**:
   - Enforces input validation to ensure proper search term format
   - Validates output quality to ensure recommendations are actionable
   - Prevents misuse through rate limiting and input sanitization
   
```python
# Example guardrail implementation
from openai_agents_sdk import Agent, GuardrailFunctionOutput, input_guardrail, RunContextWrapper
from pydantic import BaseModel

class SearchTermValidation(BaseModel):
    is_valid: bool
    reasoning: str

@input_guardrail
async def validate_search_term(
    ctx: RunContextWrapper, 
    agent: Agent, 
    input: str
) -> GuardrailFunctionOutput:
    """Validates search term format and content."""
    # Check if input is a valid search term
    is_valid = len(input.strip()) > 0 and len(input) < 100
    
    return GuardrailFunctionOutput(
        output_info=SearchTermValidation(
            is_valid=is_valid,
            reasoning="Search term must be between 1-100 characters" if not is_valid else "Valid search term"
        ),
        tripwire_triggered=not is_valid
    )
```

5. **Multi-Agent Orchestration**:
   - Main SEO agent delegates specialized tasks to intent and recommendation agents
   - Handoffs occur at defined points in the analysis workflow
   - Results are aggregated and refined through agent collaboration
   
```python
# Example orchestration implementation
from openai_agents_sdk import Agent, Runner

# Define specialized agents
intent_analyzer = Agent(
    name="Intent Analyzer",
    instructions="Analyze SERP data to determine search intent (transactional vs. exploratory)",
    tools=[...]
)

recommender = Agent(
    name="Recommendation Agent",
    instructions="Recommend SEO tactics based on search intent and SERP structure",
    tools=[...]
)

# Define orchestration agent with handoffs
seo_orchestrator = Agent(
    name="SEO Orchestrator",
    instructions="Coordinate analysis of SERP data and generate recommendations",
    handoffs=[intent_analyzer, recommender]
)

async def analyze_keyword(search_term):
    """Analyzes a keyword and provides SEO recommendations."""
    result = await Runner.run(seo_orchestrator, search_term)
    return result.final_output
```

## Core Domain Models

1. **SearchAnalysis**:
   - Represents a complete keyword analysis with all extracted insights
   - Links to the original search term and resulting recommendations
   
```python
# Example domain model
class SearchAnalysis(Base):
    __tablename__ = "search_analyses"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    search_term = Column(String, nullable=False, index=True)
    main_keyword = Column(String, nullable=False)
    secondary_keywords = Column(ARRAY(String), nullable=False)
    intent_type = Column(String, nullable=False)
    has_market_gap = Column(Boolean, default=False)
    
    # Relationships
    recommendations = relationship("Recommendation", back_populates="analysis")
```

2. **Recommendation**:
   - Contains specific SEO tactics recommended based on analysis
   - Linked to the parent search analysis
   
```python
# Example domain model
class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    analysis_id = Column(UUID, ForeignKey("search_analyses.id"), nullable=False)
    tactic_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    
    # Relationships
    analysis = relationship("SearchAnalysis", back_populates="recommendations")
```

## Infrastructure Highlights

1. **Database Layer**:
   - SQLite for development and PostgreSQL for production
   - SQLAlchemy ORM with async support for data access
   - Repository pattern for clean separation of concerns
   
```python
# Example database setup
async def init_db():
    # Database setup
    db_engine = create_async_engine(
        settings.DATABASE_URL, 
        echo=settings.DEBUG
    )
    
    # Session creation
    session_maker = sessionmaker(
        db_engine, 
        expire_on_commit=False, 
        class_=AsyncSession
    )
    
    # Additional setup (indices, migrations, etc.)
    
    return {
        "engine": db_engine,
        "session": session_maker,
        # Other DB-related objects
    }
```

2. **Tracing and Monitoring**:
   - Comprehensive tracing of agent interactions and API calls
   - Monitoring of performance metrics and error rates
   - Exporters for popular observability platforms
   
```python
# Example tracing setup
from openai_agents_sdk import configure_tracing
from openai_agents_sdk.tracing import ConsoleExporter

# Configure tracing with custom exporter
configure_tracing(
    service_name="serp-keyword-analyzer",
    exporter=ConsoleExporter(),  # Or custom exporter
    sample_rate=1.0,             # Capture all traces
)

# Custom trace processor example
class FeedbackProcessor:
    def process_trace(self, trace):
        # Process trace data for feedback analysis
        # Store insights for model improvement
        pass
```

3. **Streaming Support**:
   - Real-time streaming of analysis results
   - Progress updates during longer analyses
   
```python
# Example streaming implementation
from openai_agents_sdk import Agent, Runner
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.websocket("/stream-analysis")
async def stream_analysis(websocket: WebSocket):
    await websocket.accept()
    
    # Get search term from client
    search_term = await websocket.receive_text()
    
    # Create streaming context
    async for chunk in Runner.stream(seo_expert, search_term):
        if chunk.content:
            await websocket.send_text(chunk.content)
    
    await websocket.close()
```

4. **API Layer**:
   - FastAPI framework for high-performance API
   - OpenAPI documentation with example requests
   - Pydantic models for request/response validation
   
```python
# Example API endpoint
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1")

class KeywordRequest(BaseModel):
    search_term: str
    max_results: int = 10

class KeywordResponse(BaseModel):
    main_keyword: str
    secondary_keywords: list[str]
    intent: str
    has_market_gap: bool
    recommended_tactics: list[str]

@router.post("/analyze", response_model=KeywordResponse)
async def analyze_keyword(
    request: KeywordRequest,
    keyword_service = Depends(get_keyword_service)
):
    try:
        result = await keyword_service.analyze(request.search_term, request.max_results)
        return result
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))
```

## Key Flows

1. **Search Term Analysis Flow**:
   ```
   User Input → Input Validation → SERP API Call → Keyword Extraction → Intent Analysis → Market Gap Detection → Tactic Recommendation → Output Formatting
   ```

2. **Feedback Collection Flow**:
   ```
   Analysis Result → User Feedback → Feedback Validation → Insight Extraction → Performance Metrics → Model Improvement
   ```

3. **Orchestration Flow**:
   ```
   User Input → Guardrail Validation → Orchestrator Agent → 
   Intent Analyzer Selection → Intent Analysis → 
   Recommender Selection → Tactic Generation → 
   Output Guardrail → Response
   ```
   
   Implementation:
   
```python
# Example flow implementation
class KeywordAnalysisFlow:
    def __init__(self, serp_service, analyzer_service, recommender_service):
        self.serp_service = serp_service
        self.analyzer_service = analyzer_service
        self.recommender_service = recommender_service
    
    async def process(self, search_term):
        """Processes a search term through the complete analysis flow."""
        # Fetch SERP data
        serp_data = await self.serp_service.fetch(search_term)
        
        # Analyze intent and keywords
        analysis = await self.analyzer_service.analyze(serp_data)
        
        # Generate recommendations
        recommendations = await self.recommender_service.recommend(analysis)
        
        return {
            "analysis": analysis,
            "recommendations": recommendations
        }
```

## Getting Started Tips

1. **Initial Setup**:
   - Clone the repository and install dependencies
   - Configure environment variables for API keys
   - Run database migrations
   - Start the development server

2. **Development Workflow**:
   - Implement changes in feature branches
   - Run tests to ensure functionality
   - Submit pull requests for review
   - Deploy after CI validation

3. **Agent Development with OpenAI Agents SDK**:
   - Define clear, concise instructions for each agent
   - Implement specialized tools for specific tasks
   - Use knowledge sources to provide domain expertise
   - Test agents with various input types
   - Implement proper error handling
   - Add logging and tracing for visibility

4. **Guardrail Development**:
   - Define clear validation criteria for inputs and outputs
   - Implement input guardrails to validate and sanitize user inputs
   - Implement output guardrails to ensure responses meet quality standards
   - Test guardrails with edge cases and potentially problematic inputs
   - Configure tripwire mechanisms for handling validation failures

5. **Testing Strategy**:
   - Unit test individual components (tools, repositories)
   - Test agents with mock data
   - Integration test the complete analysis flow
   - Test error handling and recovery
   - Benchmark performance with various input sizes
   - Test guardrails with edge cases

## Important Dependencies

- **Core**:
  - `openai-agents-sdk`: Core framework for building and orchestrating AI agents
  - `pydantic`: Data validation and settings management
  - `requests`: HTTP client for API calls
  - `fastapi`: High-performance API framework

- **Data Handling**:
  - `sqlalchemy`: ORM for database access
  - `alembic`: Database migration tool
  - `asyncpg`: PostgreSQL async driver
  - `pandas`: Data analysis and manipulation

- **Monitoring & Tracing**:
  - `logfire`: Integration for advanced logging and monitoring
  - `agentops`: Agent operations visibility and analysis
  - `braintrust`: Agent evaluation and performance tracking
  - `scorecard`: Scoring agent performance and outputs
  - `keywordsai`: Tracing and analysis tools for LLM-based systems

- **Development**:
  - `pytest`: Testing framework
  - `pytest-asyncio`: Async support for pytest
  - `black`: Code formatting
  - `flake8`: Linting
  - `mypy`: Static type checking

## Orchestration Patterns

1. **LLM-Driven Orchestration**:
   - Main SEO agent determines which specialized agents to use based on input
   - Autonomously plans the analysis workflow based on search term characteristics
   - Dynamically selects tools based on SERP features and data quality

2. **Code-Driven Orchestration**:
   - Predefined workflows for common analysis patterns
   - Deterministic processing pipeline for consistent results
   - Explicit handoffs between agents at well-defined analysis stages

3. **Hybrid Orchestration**:
   - Combines predictable workflow structure with flexible LLM decision-making
   - Balances consistency and adaptability to handle diverse search queries
   - Uses heuristics to determine when to rely on code vs. LLM decisions

This structure provides a robust foundation for building an intelligent SEO analysis system with advanced keyword research and recommendation capabilities for the Print-on-Demand graphic tee market. 