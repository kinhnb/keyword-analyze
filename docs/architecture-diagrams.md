# Architecture Diagrams

This document provides visual representations of the AI SERP Keyword Research Agent architecture, showcasing its components, interactions, and data flows.

## System Overview

The following diagram illustrates the high-level architecture of the AI SERP Keyword Research Agent:

```mermaid
graph TD
    Client[Client Applications] --> API[API Layer]
    API --> Guardrails[Input/Output Guardrails]
    Guardrails --> Agents[Multi-Agent System]
    Agents --> Pipeline[Analysis Pipeline]
    Agents --> Tools[Function Tools]
    Pipeline --> Repositories[Data Repositories]
    Tools --> ExternalAPIs[External SERP APIs]
    Repositories --> Database[(Database)]
    
    subgraph "Agent Layer"
        Agents
        Tools
    end
    
    subgraph "Core Layer"
        Pipeline
        Strategies[Intent Strategies]
        Pipeline --> Strategies
    end
    
    subgraph "Data Layer"
        Repositories
        CacheService[Cache Service]
        Repositories --> CacheService
        CacheService --> Redis[(Redis Cache)]
    end
    
    subgraph "API Layer"
        API
        Guardrails
        AuthMiddleware[Auth & Rate Limiting]
        API --> AuthMiddleware
    end
    
    subgraph "Observability"
        Tracing[Tracing]
        Metrics[Metrics]
        Logging[Logging]
        Agents --> Tracing
        Pipeline --> Metrics
        API --> Logging
    end
```

## Multi-Agent Architecture

The system uses a specialized multi-agent architecture with distinct responsibilities:

```mermaid
flowchart TD
    User(User) --> API[API Layer]
    API --> SEO[SEO Expert Agent]
    
    SEO --> Intent[Intent Analyzer Agent]
    SEO --> Recommender[Recommendation Agent]
    
    SEO --> FetchTool[fetch_serp_data]
    SEO --> MarketGapTool[detect_market_gap]
    SEO --> FeaturesTool[extract_serp_features]
    
    Intent --> KeywordsTool[analyze_keywords]
    Intent --> ClassifyTool[classify_intent]
    Intent --> PatternsTool[detect_serp_patterns]
    
    Recommender --> GenRecommendationsTool[generate_recommendations]
    Recommender --> PrioritizeTool[prioritize_tactics]
    Recommender --> FormatTool[format_recommendations]
    
    FetchTool --> SERP[SERP API Provider]
    
    subgraph "Orchestrator Agent"
        SEO
    end
    
    subgraph "Specialized Agents"
        Intent
        Recommender
    end
    
    subgraph "External Services"
        SERP
    end
```

## Data Flow Diagram

This diagram illustrates how data flows through the system during a keyword analysis:

```mermaid
sequenceDiagram
    participant User
    participant API as API Layer
    participant SEO as SEO Expert Agent
    participant Intent as Intent Analyzer Agent
    participant Recommend as Recommendation Agent
    participant Pipeline as Analysis Pipeline
    participant DB as Database
    participant Cache as Redis Cache
    participant SERP as SERP API
    
    User->>API: Analyze "funny dad shirt"
    API->>Cache: Check for cached results
    
    alt Results cached
        Cache-->>API: Return cached results
        API-->>User: Return analysis
    else Results not cached
        API->>SEO: Start analysis
        
        SEO->>SERP: fetch_serp_data("funny dad shirt")
        SERP-->>SEO: SERP Results
        
        SEO->>Intent: Hand off for intent analysis
        Intent->>Intent: analyze_keywords()
        Intent->>Intent: classify_intent()
        Intent->>Intent: detect_serp_patterns()
        Intent-->>SEO: Intent Analysis Results
        
        SEO->>SEO: detect_market_gap()
        
        SEO->>Recommend: Hand off for recommendations
        Recommend->>Recommend: generate_recommendations()
        Recommend->>Recommend: prioritize_tactics()
        Recommend->>Recommend: format_recommendations()
        Recommend-->>SEO: Recommendation Results
        
        SEO->>Pipeline: Process through pipeline
        Pipeline->>DB: Store analysis results
        Pipeline->>Cache: Cache analysis results
        Pipeline-->>SEO: Final analysis results
        
        SEO-->>API: Return complete analysis
        API-->>User: Return analysis
    end
```

## Pipeline Architecture

The analysis pipeline processes search terms through a series of stages:

```mermaid
flowchart LR
    Input[Search Term Input] --> Stage1
    
    subgraph "Pipeline Stages"
        Stage1[Input Validation Stage]
        Stage2[SERP Retrieval Stage]
        Stage3[Intent Analysis Stage]
        Stage4[Market Gap Analysis Stage]
        Stage5[Recommendation Generation Stage]
        Stage6[Output Formatting Stage]
        
        Stage1 --> Stage2
        Stage2 --> Stage3
        Stage3 --> Stage4
        Stage4 --> Stage5
        Stage5 --> Stage6
    end
    
    Stage6 --> Output[Analysis Result]
    
    Stage1 -.-> Cache[(Cache Check)]
    Stage2 -.-> SERP[SERP API]
    Stage3 -.-> Strategies[(Intent Strategies)]
    Stage6 -.-> Store[(Store Results)]
    
    class Stage1,Stage2,Stage3,Stage4,Stage5,Stage6 stage;
    classDef stage fill:#f9f,stroke:#333,stroke-width:1px;
```

## Intent Classification Strategies

This diagram shows the strategy pattern implementation for intent classification:

```mermaid
classDiagram
    class IntentStrategy {
        <<interface>>
        +analyze(serp_results) IntentAnalysis
        +calculate_confidence() float
        +extract_signals() List~str~
    }
    
    class TransactionalIntentStrategy {
        +analyze(serp_results) IntentAnalysis
        +calculate_confidence() float
        +extract_signals() List~str~
        -detect_product_pages() bool
        -check_shopping_ads() bool
    }
    
    class InformationalIntentStrategy {
        +analyze(serp_results) IntentAnalysis
        +calculate_confidence() float
        +extract_signals() List~str~
        -detect_articles() bool
        -check_featured_snippets() bool
    }
    
    class NavigationalIntentStrategy {
        +analyze(serp_results) IntentAnalysis
        +calculate_confidence() float
        +extract_signals() List~str~
        -detect_brand_focus() bool
    }
    
    class ExploratoryIntentStrategy {
        +analyze(serp_results) IntentAnalysis
        +calculate_confidence() float
        +extract_signals() List~str~
        -detect_collection_pages() bool
        -check_image_packs() bool
    }
    
    class IntentStrategyFactory {
        +create_strategy(serp_data) IntentStrategy
        -detect_dominant_pattern() str
    }
    
    IntentStrategy <|-- TransactionalIntentStrategy
    IntentStrategy <|-- InformationalIntentStrategy
    IntentStrategy <|-- NavigationalIntentStrategy
    IntentStrategy <|-- ExploratoryIntentStrategy
    IntentStrategyFactory --> IntentStrategy : creates
```

## Deployment Architecture

This diagram illustrates the production deployment architecture using Kubernetes:

```mermaid
flowchart TD
    Client[Client Applications] --> Ingress[Ingress Controller]
    Ingress --> SVC[Service]
    SVC --> Pods[Application Pods]
    
    Pods --> PostgreSQL[(PostgreSQL)]
    Pods --> Redis[(Redis)]
    Pods --> SERPAPI[SERP API]
    Pods --> OpenAI[OpenAI API]
    
    subgraph "Kubernetes Cluster"
        Ingress
        SVC
        Pods
        
        subgraph "Stateful Services"
            PostgreSQL
            Redis
        end
        
        subgraph "Monitoring"
            Prometheus[Prometheus]
            Grafana[Grafana]
            Loki[Loki]
            Pods --> Prometheus
            Prometheus --> Grafana
            Pods --> Loki
            Loki --> Grafana
        end
    end
    
    subgraph "External Services"
        SERPAPI
        OpenAI
    end
```

## Component Hierarchy

The following diagram shows the hierarchical structure of the application components:

```mermaid
graph TD
    App[AI SERP Keyword Research Agent] --> APILayer[API Layer]
    App --> AgentLayer[Agent Layer]
    App --> CoreLayer[Core Layer]
    App --> DataLayer[Data Layer]
    App --> ObservabilityLayer[Observability Layer]
    
    APILayer --> APIRoutes[API Routes]
    APILayer --> APIMiddleware[API Middleware]
    APILayer --> APISchemas[Request/Response Schemas]
    
    AgentLayer --> SEOAgent[SEO Expert Agent]
    AgentLayer --> IntentAgent[Intent Analyzer Agent]
    AgentLayer --> RecommendationAgent[Recommendation Agent]
    AgentLayer --> FunctionTools[Function Tools]
    
    CoreLayer --> Pipeline[Analysis Pipeline]
    CoreLayer --> IntentStrategies[Intent Strategies]
    CoreLayer --> DomainModels[Domain Models]
    CoreLayer --> SERPProcessing[SERP Processing]
    
    DataLayer --> Repositories[Repositories]
    DataLayer --> DataModels[Data Models]
    DataLayer --> CacheService[Cache Service]
    DataLayer --> Migrations[Database Migrations]
    
    ObservabilityLayer --> Tracing[Tracing]
    ObservabilityLayer --> Metrics[Metrics]
    ObservabilityLayer --> Logging[Logging]
```

## Database Schema

This diagram visualizes the database schema and relationships:

```mermaid
erDiagram
    SearchAnalysis ||--o{ SerpFeature : has
    SearchAnalysis ||--o{ Recommendation : generates
    SearchAnalysis ||--o| MarketGap : identifies
    SearchAnalysis ||--o{ UserFeedback : receives
    ApiKey ||--o{ ApiUsage : tracks
    
    SearchAnalysis {
        uuid id PK
        string search_term
        string main_keyword
        string[] secondary_keywords
        string intent_type
        boolean has_market_gap
        float confidence
        timestamp created_at
    }
    
    SerpFeature {
        uuid id PK
        uuid analysis_id FK
        string feature_type
        int feature_position
        jsonb feature_data
        timestamp created_at
    }
    
    Recommendation {
        uuid id PK
        uuid analysis_id FK
        string tactic_type
        string description
        int priority
        float confidence
        timestamp created_at
    }
    
    MarketGap {
        uuid id PK
        uuid analysis_id FK
        string description
        float opportunity_score
        float competition_level
        string[] related_keywords
        timestamp created_at
    }
    
    UserFeedback {
        uuid id PK
        uuid analysis_id FK
        int rating
        string comments
        uuid[] helpful_recommendations
        boolean was_market_gap_accurate
        timestamp created_at
    }
    
    ApiKey {
        uuid id PK
        string key_hash
        uuid user_id
        string name
        boolean enabled
        int rate_limit_per_hour
        timestamp created_at
        timestamp expires_at
    }
    
    ApiUsage {
        uuid id PK
        string api_key_id
        string endpoint
        int request_count
        timestamp last_request_at
        timestamp first_request_at
    }
```

## API Structure

This diagram outlines the structure of the API endpoints:

```mermaid
graph TD
    API[API] --> V1[/api/v1]
    API --> Health[/health]
    API --> Docs[/docs]
    API --> Redoc[/redoc]
    
    V1 --> Analyze[/analyze]
    V1 --> Feedback[/feedback]
    
    subgraph "Authentication"
        Auth[API Key Auth]
        RateLimit[Rate Limiting]
        Analyze --> Auth
        Analyze --> RateLimit
        Feedback --> Auth
        Feedback --> RateLimit
    end
    
    subgraph "Request Processing"
        Validation[Input Validation]
        Sanitization[Input Sanitization]
        Analyze --> Validation
        Analyze --> Sanitization
        Feedback --> Validation
        Feedback --> Sanitization
    end
    
    Analyze --> AnalyzeLogic[Analysis Pipeline]
    Feedback --> FeedbackLogic[Feedback Storage]
    
    style API fill:#f9f,stroke:#333,stroke-width:2px
    style Analyze fill:#bbf,stroke:#333,stroke-width:2px
    style Feedback fill:#bbf,stroke:#333,stroke-width:2px
    style Health fill:#bfb,stroke:#333,stroke-width:1px
```

## Observability Architecture

This diagram shows how tracing, metrics, and logging are implemented:

```mermaid
flowchart TD
    Request[User Request] --> Middleware[Tracing Middleware]
    Middleware --> API[API Endpoint]
    API --> Agents[Agent System]
    
    Agents --> TraceManager[Trace Manager]
    Agents --> MetricsCollector[Metrics Collector]
    Agents --> Logger[Structured Logger]
    
    TraceManager --> TraceProcessors[Trace Processors]
    TraceProcessors --> ConsoleExporter[Console Exporter]
    TraceProcessors --> FileExporter[File Exporter]
    
    MetricsCollector --> PrometheusExporter[Prometheus Exporter]
    MetricsCollector --> LoggingExporter[Logging Exporter]
    
    Logger --> JsonFormatter[JSON Formatter]
    Logger --> LogStorage[Log Storage]
    
    subgraph "Visualization"
        PrometheusExporter --> Grafana[Grafana]
        LogStorage --> Grafana
    end
```

## Guardrails Implementation

This diagram illustrates the guardrails implementation:

```mermaid
flowchart LR
    Input[User Input] --> InputGuardrails
    
    subgraph "Input Guardrails"
        InputGuardrails[Input Guardrail Decorators]
        ValidationGuardrail[Validation Guardrail]
        SafetyGuardrail[Content Safety Guardrail]
        NormalizationGuardrail[Normalization Guardrail]
        
        InputGuardrails --> ValidationGuardrail
        InputGuardrails --> SafetyGuardrail
        InputGuardrails --> NormalizationGuardrail
    end
    
    NormalizationGuardrail --> AgentSystem[Agent System]
    
    AgentSystem --> OutputGuardrails
    
    subgraph "Output Guardrails"
        OutputGuardrails[Output Guardrail Decorators]
        QualityGuardrail[Quality Guardrail]
        CompletenessGuardrail[Completeness Guardrail]
        FormatGuardrail[Format Guardrail]
        
        OutputGuardrails --> QualityGuardrail
        OutputGuardrails --> CompletenessGuardrail
        OutputGuardrails --> FormatGuardrail
    end
    
    FormatGuardrail --> Output[API Response]
```

## Sequence Diagram: API Request

This diagram shows the sequence of operations when an API request is received:

```mermaid
sequenceDiagram
    participant Client
    participant API as API Layer
    participant Auth as Auth Middleware
    participant Rate as Rate Limiter
    participant Guard as Input Guardrails
    participant Runner as Agent Runner
    participant SEO as SEO Expert Agent
    participant DB as Database
    participant Cache as Redis Cache
    
    Client->>API: POST /api/v1/analyze
    
    API->>Auth: Validate API key
    Auth->>API: Authentication result
    
    alt Authentication failed
        API-->>Client: 401 Unauthorized
    else Authentication successful
        API->>Rate: Check rate limit
        
        alt Rate limit exceeded
            Rate-->>API: Limit exceeded
            API-->>Client: 429 Too Many Requests
        else Rate limit ok
            Rate-->>API: Limit ok
            
            API->>Guard: Validate input
            
            alt Input invalid
                Guard-->>API: Validation failed
                API-->>Client: 400 Bad Request
            else Input valid
                Guard-->>API: Input valid
                
                API->>Cache: Check cached results
                
                alt Results cached
                    Cache-->>API: Return cached results
                    API-->>Client: 200 OK with results
                else Results not cached
                    Cache-->>API: No cached results
                    
                    API->>Runner: Run agent analysis
                    Runner->>SEO: Start orchestration
                    SEO-->>Runner: Analysis results
                    Runner-->>API: Complete results
                    
                    API->>DB: Store results
                    API->>Cache: Cache results
                    API-->>Client: 200 OK with results
                end
            end
        end
    end
```

## Agent Interaction Diagram

This diagram illustrates how agents interact during analysis:

```mermaid
sequenceDiagram
    participant Runner as Agent Runner
    participant SEO as SEO Expert Agent
    participant Intent as Intent Analyzer
    participant Recommend as Recommendation Agent
    participant SERP as SERP API
    
    Runner->>SEO: analyze("funny dad shirt")
    
    SEO->>SEO: fetch_serp_data()
    SEO->>SERP: Fetch SERP results
    SERP-->>SEO: SERP data
    
    SEO->>SEO: extract_serp_features()
    
    SEO->>SEO: Determine need for intent analysis
    SEO->>Intent: Hand off for intent analysis
    
    Intent->>Intent: analyze_keywords()
    Intent->>Intent: classify_intent()
    Intent->>Intent: detect_serp_patterns()
    Intent->>Intent: Determine intent type
    Intent-->>SEO: Intent analysis results
    
    SEO->>SEO: detect_market_gap()
    SEO->>SEO: Evaluate market gap
    
    SEO->>SEO: Determine need for recommendations
    SEO->>Recommend: Hand off for recommendations
    
    Recommend->>Recommend: generate_recommendations()
    Recommend->>Recommend: prioritize_tactics()
    Recommend->>Recommend: format_recommendations()
    Recommend-->>SEO: Recommendation results
    
    SEO->>SEO: Compile final analysis
    SEO-->>Runner: Complete analysis result
```

## Tech Stack Overview

This diagram provides an overview of the technology stack used:

```mermaid
graph TD
    Agent[OpenAI Agents SDK] --> Python[Python 3.10+]
    Python --> FastAPI[FastAPI]
    Python --> SQLAlchemy[SQLAlchemy]
    Python --> Pydantic[Pydantic]
    Python --> Redis[Redis-py]
    
    FastAPI --> Uvicorn[Uvicorn]
    SQLAlchemy --> PostgreSQL[PostgreSQL]
    SQLAlchemy --> Alembic[Alembic]
    
    subgraph "Runtime Environment"
        Python
        Uvicorn
        PostgreSQL
        RedisServer[Redis Server]
    end
    
    subgraph "API Framework"
        FastAPI
        Pydantic
    end
    
    subgraph "Data Access"
        SQLAlchemy
        Alembic
        Redis
    end
    
    subgraph "Observability"
        OpenTelemetry[OpenTelemetry]
        Prometheus[Prometheus]
        Grafana[Grafana]
    end
    
    subgraph "Testing"
        Pytest[Pytest]
        Httpx[HTTPX]
    end
    
    subgraph "Deployment"
        Docker[Docker]
        Kubernetes[Kubernetes]
    end
``` 