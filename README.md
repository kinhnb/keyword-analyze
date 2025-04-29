# AI SERP Keyword Research Agent

A specialized agent for analyzing Google Search Engine Results Pages (SERPs) for Print-on-Demand graphic tees, extracting key SEO insights, and recommending targeted optimization strategies.

## Project Overview

This system leverages the OpenAI Agents SDK to provide sophisticated SERP analysis capabilities:

- **Multi-Agent Architecture**: Specialized agents for SEO analysis, intent detection, and recommendation generation
- **Pipeline Processing**: Six-stage pipeline for comprehensive SERP analysis
- **Intent Classification**: Advanced search intent detection (transactional, informational, exploratory, navigational)
- **Market Gap Analysis**: Identification of unaddressed needs in search results
- **Actionable Recommendations**: Specific SEO tactics tailored to the Print-on-Demand graphic tees niche

## Project Structure

The project follows a clean architecture with clear separation of concerns:

```
ai_serp_keyword_research/
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
│   ├── routes/               # Route definitions
│   ├── middleware/           # API middleware
│   └── schemas/              # Request/response schemas
├── services/                 # External service integrations
├── orchestration/            # Multi-agent workflow orchestration
├── tracing/                  # Tracing and monitoring
└── utils/                    # Utility functions
```

## Dependency Management

This project uses split requirement files to manage dependencies for different environments:

### Main Requirements

- `requirements.txt`: Contains all dependencies needed for both development and basic production usage
  ```bash
  pip install -r requirements.txt
  ```

### Development Requirements

- `dev-requirements.txt`: Additional dependencies needed for development, testing, and documentation
  ```bash
  pip install -r requirements.txt -r dev-requirements.txt
  ```

### Production Requirements

- `production-requirements.txt`: Optimized dependencies for production environments, including monitoring tools
  ```bash
  pip install -r production-requirements.txt
  ```

## Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-serp-keyword-research
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt -r dev-requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the project root with the following variables:

   ```
   # API Configuration
   API_KEY_SECRET=your_secret_key_for_generating_api_keys

   # Database Configuration
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/serp_analysis
   TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/serp_analysis_test

   # Redis Configuration
   REDIS_URL=redis://localhost:6379/0

   # SERP API Configuration
   SERP_API_KEY=your_serp_api_key
   SERP_API_URL=https://serpapi.com/search.json

   # Observability
   ENABLE_TRACING=true
   TRACING_EXPORTER=console  # Options: console, jaeger, otlp
   TRACING_ENDPOINT=http://localhost:4317  # Only needed for jaeger/otlp

   # Security
   JWT_SECRET=your_jwt_secret
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the application for development**
   ```bash
   uvicorn ai_serp_keyword_research.main:app --reload
   ```

## API Documentation

API documentation is available at `/docs` when the server is running.

## Docker Support

The project includes Docker support for both development and production:

```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up
```

## Testing

Run the test suite with:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=ai_serp_keyword_research
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and delivery:

- **Linting**: Code quality checks with black, isort, flake8, and mypy
- **Testing**: Automated tests with pytest
- **Security**: Security checks with bandit and safety

## License

[MIT License](LICENSE) 