# Technical Context

## Technologies Used

### Core Framework
- **OpenAI Agents SDK**: Foundation framework for creating and orchestrating AI agents
- **Python 3.10+**: Primary programming language
- **FastAPI**: Web framework for API endpoints
- **Pydantic**: Data validation and settings management
- **asyncio**: Asynchronous I/O for concurrent operations

### Data Storage
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database for persistent storage
- **SQLite**: Alternative database for development environment
- **Alembic**: Database migration tool
- **Redis**: Cache for storing temporary results and rate limiting

### External Services
- **SERP API Provider**: External service for fetching Google search results
  - Potential providers: SerpAPI, ScrapingBee, or custom implementation
- **OpenAI API**: For agent operations and LLM capabilities

### Monitoring and Observability
- **OpenTelemetry**: Tracing and metrics collection
- **Prometheus**: Metrics and alerting
- **Grafana**: Visualization dashboards
- **Sentry**: Error tracking and performance monitoring

### Testing and CI/CD
- **pytest**: Test framework
- **pytest-asyncio**: Async support for pytest
- **GitHub Actions**: CI/CD pipeline
- **Docker**: Containerization
- **Kubernetes**: Container orchestration (for production)

## Data Models and Schema

### Database Schema

#### SearchAnalysis Table
```sql
CREATE TABLE search_analyses (
    id UUID PRIMARY KEY,
    search_term VARCHAR(255) NOT NULL,
    main_keyword VARCHAR(255) NOT NULL,
    secondary_keywords TEXT[] NOT NULL,
    intent_type VARCHAR(50) NOT NULL,
    has_market_gap BOOLEAN DEFAULT FALSE,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(search_term)
);
CREATE INDEX idx_search_term ON search_analyses(search_term);
```

#### SerpFeatures Table
```sql
CREATE TABLE serp_features (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES search_analyses(id),
    feature_type VARCHAR(50) NOT NULL,
    feature_position INTEGER,
    feature_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_analysis_features ON serp_features(analysis_id);
```

#### Recommendations Table
```sql
CREATE TABLE recommendations (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES search_analyses(id),
    tactic_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_analysis_recommendations ON recommendations(analysis_id);
```

### Redis Cache Schema

#### Cache Keys
- `serp::{search_term}` - Caches SERP results for a search term (TTL: 24 hours)
- `analysis::{search_term}` - Caches complete analysis results
- `recommendations::{search_term}` - Caches recommendation results

## API Specifications

### RESTful Endpoints

#### Analyze Keyword Endpoint
- **URL**: `/api/v1/analyze`
- **Method**: `POST`
- **Authentication**: API Key (X-API-Key header)
- **Request Body**:
```json
{
  "search_term": "best dad ever shirt",
  "max_results": 10
}
```
- **Success Response** (Code: 200):
```json
{
  "analysis": {
    "main_keyword": "dad graphic tee",
    "secondary_keywords": ["funny dad shirt", "father's day gift"],
    "intent_type": "transactional",
    "confidence": 0.87,
    "serp_features": ["shopping_ads", "image_pack"]
  },
  "market_gap": {
    "detected": true,
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
```
- **Error Responses**:
  - Code 400: Invalid search term
  - Code 401: Unauthorized (invalid API key)
  - Code 429: Rate limit exceeded
  - Code 500: Server error

#### Feedback Endpoint
- **URL**: `/api/v1/feedback`
- **Method**: `POST`
- **Authentication**: API Key (X-API-Key header)
- **Request Body**:
```json
{
  "analysis_id": "uuid-of-analysis",
  "rating": 4,
  "comments": "Good recommendations but missed some keywords",
  "was_recommendation_helpful": true
}
```
- **Success Response** (Code: 200):
```json
{
  "status": "success",
  "message": "Feedback recorded successfully"
}
```

#### Health Check Endpoint
- **URL**: `/health`
- **Method**: `GET`
- **Authentication**: None
- **Success Response** (Code: 200):
```json
{
  "status": "healthy",
  "timestamp": "2025-04-10T12:34:56Z",
  "dependencies": {
    "database": "connected",
    "redis": "connected",
    "serp_api": "operational"
  }
}
```

## Development Setup

### Local Development Environment
1. **Python Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   - Create a `.env` file with required configuration:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERP_API_KEY=your_serp_api_key
   DATABASE_URL=postgresql://user:password@localhost:5432/keyword_research
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Database Setup**:
   ```bash
   # Start PostgreSQL (via Docker for simplicity)
   docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_USER=user -e POSTGRES_DB=keyword_research postgres:14

   # Apply migrations
   python -m alembic upgrade head
   ```

4. **Running the Service**:
   ```bash
   uvicorn api.main:app --reload
   ```

### Development Tools
- **VS Code** with Python, FastAPI, and SQLAlchemy extensions
- **Insomnia/Postman** for API testing
- **pgAdmin** for database management
- **Docker Desktop** for container management

### Project Structure
```
ai-serp-keyword-research/
├── agents/                   # AI agents powered by OpenAI Agents SDK
├── guardrails/               # Safety and validation mechanisms
├── core/                     # Core business logic
│   ├── pipeline/             # SERP analysis workflow pipeline
│   ├── strategies/           # Intent analysis strategies
│   └── serp/                 # SERP processing modules
├── tools/                    # Function tools for agents
├── data/                     # Data access layer
│   ├── repositories/         # Repository pattern implementations
│   ├── models/               # Data models
│   └── migrations/           # Database migrations
├── api/                      # API endpoints
│   ├── middleware/           # API middleware (auth, rate limiting, security)
│   ├── routes/               # API route definitions
│   └── schemas/              # API request/response schemas
├── services/                 # External service integrations
├── orchestration/            # Multi-agent workflow orchestration
├── tracing/                  # Tracing and monitoring
├── security/                 # Security components
│   ├── credentials.py        # Credential management for external APIs
│   └── security_review.py    # Security review tools
├── utils/                    # Utility functions
│   ├── logging.py            # Logging utilities
│   └── env_validator.py      # Environment variable validation
├── metrics/                  # Metrics collection and exporters
└── tests/                    # Test suite
```

## Technical Constraints

### Performance Requirements
- **Latency**: Analysis results should be returned within 30 seconds
- **Throughput**: System should handle at least 10 concurrent requests
- **Availability**: 99.9% uptime for API endpoints

### Security Constraints
- **API Authentication**: All API endpoints must use API key authentication
- **Rate Limiting**: Implement per-user rate limiting to prevent abuse
- **Input Validation**: All user inputs must be validated and sanitized
- **Sensitive Data**: API keys and credentials must be stored securely using environment variables or secrets management

### Implemented Security Measures
- **SecurityMiddleware**: Validates and sanitizes input data to prevent injection attacks
- **Environment Validator**: Validates environment variables with type checking and constraints
- **Credential Manager**: Securely manages API keys and connection strings
- **Security Review Tool**: Identifies potential security issues in the codebase
- **Error Handling**: Properly catches and handles errors without exposing sensitive information

### Scalability Considerations
- **Horizontal Scaling**: API layer should be stateless to enable horizontal scaling
- **Database Indexing**: Proper indexes for frequent query patterns
- **Caching Strategy**: Cache common search terms to reduce API calls
- **Asynchronous Processing**: Long-running analysis tasks should be processed asynchronously

### External API Limitations
- **SERP API Rate Limits**: Most SERP API providers have strict rate limits and usage quotas
- **Cost Optimization**: SERP API calls should be optimized to minimize costs
- **Retry Strategy**: Implement exponential backoff for API failures
- **Result Caching**: Cache SERP results to avoid redundant API calls

### LLM Considerations
- **Token Limits**: Manage context windows for LLM interactions
- **Prompt Engineering**: Carefully design agent instructions and prompts
- **Response Validation**: Validate LLM outputs for format and content quality
- **Fallback Mechanisms**: Implement fallbacks for when LLM responses don't meet requirements

## Testing Strategy

### Unit Testing
- Test individual components in isolation
- Mock external dependencies
- Focus on core business logic
- Aim for high code coverage
- Test edge cases thoroughly

### Integration Testing
- Test component interactions
- Verify database operations
- Test API endpoints
- Validate authentication and authorization
- Test error handling paths

### Performance Testing
- Benchmark response times
- Test under various load conditions
- Identify bottlenecks
- Validate caching effectiveness
- Monitor resource utilization

### Agent Testing
- Test agent instructions with various inputs
- Verify agent output quality and format
- Test agent handoffs and collaboration
- Validate agent decision-making
- Test error recovery mechanisms

## Deployment Approach

### Containerization
- Docker containers for all services
- Docker Compose for local development
- Kubernetes for production deployment
- Container health checks
- Resource limits and requests

### CI/CD Pipeline
- Automated testing on commit
- Linting and static analysis
- Build and tag Docker images
- Deployment to staging environment
- Production deployment with approval

### Environment Setup
- Development: Local containers with SQLite
- Staging: Cloud deployment with isolated database
- Production: Fully scaled deployment with PostgreSQL
- Test: Isolated environment for integration tests
- CI: Ephemeral environment for continuous integration

### Monitoring and Logging
- Centralized logging with structured format
- Metrics collection for performance monitoring
- Health check endpoints
- Alert rules for critical issues
- Dashboard for system overview

## Core Model Structure

### Domain Models (Implemented)

The core domain models have been implemented using Pydantic for validation, serialization, and deserialization:

#### Input Models
```python
class SearchTerm(BaseModel):
    """Model representing a search term for SERP analysis."""
    term: str = Field(..., min_length=3, max_length=255, description="The search term to analyze")
    max_results: Optional[int] = Field(10, ge=1, le=100, description="Maximum number of SERP results to analyze")
    
    @validator('term')
    def validate_term(cls, v):
        """Validate that the search term contains no harmful content and is related to POD graphic tees."""
        # Implementation includes checking for POD-related terms and normalization
```

#### Analysis Models
```python
class IntentType(str, Enum):
    """Enumeration of possible search intent types."""
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    EXPLORATORY = "exploratory"
    NAVIGATIONAL = "navigational"

class Keyword(BaseModel):
    """Model representing a keyword with relevance score."""
    text: str
    relevance: float = Field(..., ge=0.0, le=1.0)
    frequency: int = Field(..., ge=0)

class IntentAnalysis(BaseModel):
    """Model representing the intent analysis for a search term."""
    intent_type: IntentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    main_keyword: Keyword
    secondary_keywords: List[Keyword] = Field(..., min_items=0, max_items=20)
    
    # Validators ensure secondary keywords are sorted by relevance
    # and that main_keyword has higher relevance than secondary_keywords

class MarketGap(BaseModel):
    """Model representing a market gap opportunity identified in SERP analysis."""
    detected: bool
    description: Optional[str] = None
    opportunity_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    competition_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Validators ensure required fields are present when gap is detected
```

#### Recommendation Models
```python
class TacticType(str, Enum):
    """Enumeration of possible SEO tactic types."""
    PRODUCT_PAGE_OPTIMIZATION = "product_page_optimization"
    CONTENT_CREATION = "content_creation"
    # Additional tactic types...

class Recommendation(BaseModel):
    """Model representing an SEO recommendation or tactic."""
    tactic_type: TacticType
    description: str = Field(..., min_length=10, max_length=1000)
    priority: int = Field(..., ge=1, le=10)
    confidence: float = Field(..., ge=0.0, le=1.0)
    
    # Validators ensure description is actionable and specific

class RecommendationSet(BaseModel):
    """Model representing a set of prioritized SEO recommendations."""
    recommendations: List[Recommendation] = Field(..., min_items=1)
    intent_based: bool
    market_gap_based: bool
    
    # Validators sort recommendations by priority and confidence
```

#### Result Model
```python
class AnalysisResult(BaseModel):
    """Model representing the complete analysis result for a search term."""
    search_term: str
    analysis_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    intent_analysis: IntentAnalysis
    market_gap: MarketGap
    serp_features: List[SerpFeature]
    recommendations: RecommendationSet
    
    # Validators ensure consistency between components and sort features by position
```

### Data Access Models

The SQLAlchemy models have been implemented for database persistence:

```python
class SearchAnalysis(Base):
    """Model representing a search term analysis result."""
    __tablename__ = "search_analyses"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    search_term = Column(String(255), nullable=False, unique=True)
    main_keyword = Column(String(255), nullable=False)
    secondary_keywords = Column(JSON, nullable=False)
    intent_type = Column(String(50), nullable=False)
    has_market_gap = Column(Boolean, default=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    
    # Relationships
    serp_features = relationship("SerpFeature", back_populates="search_analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="search_analysis", cascade="all, delete-orphan")
```

### Repository Pattern

The repository pattern has been implemented to abstract database operations:

```python
class SearchAnalysisRepository(BaseRepository[SearchAnalysis]):
    """Repository for managing SearchAnalysis entities."""
    
    async def find_by_search_term(self, search_term: str) -> Optional[SearchAnalysis]:
        """Find analysis by search term."""
        query = select(SearchAnalysis).where(SearchAnalysis.search_term == search_term)
        result = await self.session.execute(query)
        return result.scalars().first()
``` 