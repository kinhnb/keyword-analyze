# Developer Setup Guide

This guide provides step-by-step instructions for setting up the AI SERP Keyword Research Agent development environment.

## System Requirements

- **Operating System**: Linux (Ubuntu 20.04+), macOS (11+), or Windows 10/11 with WSL2
- **Memory**: 4GB RAM minimum, 8GB+ recommended
- **Disk Space**: At least 2GB free space
- **Python**: Version 3.10+ required

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-serp-keyword-research.git
cd ai-serp-keyword-research
```

### 2. Set Up a Virtual Environment

#### For Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```

#### For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

The project uses separate requirement files for different environments:

```bash
# For development environment (includes testing tools)
pip install -r requirements/dev.txt

# For production environment only
# pip install -r requirements/prod.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# SERP API Configuration (choose one provider)
SERP_API_PROVIDER=serpapi  # Options: serpapi, scrapingbee, serpstack, custom
SERP_API_KEY=your_serp_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///./data/app.db  # For development
# DATABASE_URL=postgresql://user:password@localhost:5432/keyword_research  # For production

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_ENABLED=true
API_HOST=localhost
API_PORT=8000
API_WORKERS=1
API_LOG_LEVEL=info

# Tracing Configuration
TRACING_ENABLED=true
TRACING_EXPORTER=console  # Options: console, file, jaeger
TRACING_SAMPLE_RATE=1.0
```

### 5. Set Up Local Services

#### Using Docker Compose (Recommended)

The project includes a `docker-compose.yml` file to set up local services:

```bash
# Start all services (PostgreSQL, Redis, etc.)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Manual Setup (Alternative)

If not using Docker, install the following services manually:

- **Redis**: For caching and rate limiting
  - [Redis Installation Guide](https://redis.io/docs/getting-started/)

- **PostgreSQL** (Optional for production-like environment):
  - [PostgreSQL Installation Guide](https://www.postgresql.org/download/)
  - Create a database: `createdb keyword_research`

### 6. Initialize the Database

Run database migrations to create the necessary tables:

```bash
# Apply all migrations
python -m alembic upgrade head
```

### 7. Run the Application

#### Development Server

```bash
# Start the FastAPI development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Using the CLI (for development and testing)

```bash
# Run individual analysis from the command line
python -m cli.analyze "best dad ever shirt"
```

## Testing

### Running Tests

The project uses pytest for testing:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app

# Run specific test modules
pytest tests/unit/
pytest tests/integration/
pytest tests/agents/

# Run specific test file
pytest tests/unit/test_intent_analyzer.py
```

### Running Linters and Formatters

The project uses several linting and formatting tools:

```bash
# Run linting
flake8 app tests

# Run type checking
mypy app

# Run code formatting
black app tests
isort app tests
```

## API Documentation

Once the server is running, access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Workflow

### 1. Create a New Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes and Run Tests

```bash
# Make your changes
# ...

# Run tests to ensure everything works
pytest

# Run linting and formatting
flake8 app tests
black app tests
```

### 3. Commit Changes

```bash
git add .
git commit -m "feat: Add your feature description"
```

### 4. Push Changes

```bash
git push origin feature/your-feature-name
```

### 5. Create a Pull Request

Create a pull request on GitHub to merge your changes into the main branch.

## Project Structure

```
ai-serp-keyword-research/
├── agents/                   # AI agents powered by OpenAI Agents SDK
│   ├── main_agent.py         # SEO Expert agent that orchestrates the analysis
│   ├── intent_analyzer.py    # Agent specialized in intent detection
│   ├── recommender.py        # Agent for generating recommendations
│   └── base.py               # Base agent abstract class
├── api/                      # API endpoints
│   ├── routes/               # API route definitions
│   ├── middleware/           # API middleware components
│   ├── schemas/              # API request/response schemas
│   └── main.py               # FastAPI application entry point
├── core/                     # Core business logic
│   ├── pipeline/             # SERP analysis workflow pipeline
│   ├── strategies/           # Intent analysis strategies
│   └── serp/                 # SERP processing modules
├── data/                     # Data access layer
│   ├── repositories/         # Repository pattern implementations
│   ├── models/               # Data models
│   └── migrations/           # Database migrations
├── tools/                    # Function tools for agents
│   ├── serp_api.py           # SERP API integration
│   ├── keyword_analysis.py   # Keyword extraction and analysis
│   └── market_gap.py         # Market gap detection
├── guardrails/               # Safety and validation mechanisms
│   ├── input_guardrails.py   # Input validation guardrails
│   └── output_guardrails.py  # Output validation guardrails
├── services/                 # External service integrations
│   ├── serp_provider/        # SERP API service integration
│   └── cache/                # Caching service
├── tracing/                  # Tracing and monitoring
│   ├── processors/           # Custom trace processors
│   └── exporters/            # Trace export integrations
├── utils/                    # Utility functions
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── agents/               # Agent-specific tests
├── cli/                      # Command-line interface
├── docker/                   # Docker configuration
│   ├── Dockerfile            # Main application Dockerfile
│   └── docker-compose.yml    # Local development services
├── kubernetes/               # Kubernetes deployment manifests
├── docs/                     # Documentation
├── .env.example              # Example environment variables
├── requirements/             # Dependency management
│   ├── base.txt              # Base requirements
│   ├── dev.txt               # Development requirements
│   └── prod.txt              # Production requirements
├── pyproject.toml            # Python project configuration
├── setup.py                  # Package setup file
└── README.md                 # Project overview
```

## Common Issues and Solutions

### OpenAI API Key Issues

**Issue**: `AuthenticationError: Incorrect API key provided`

**Solution**: Ensure the `OPENAI_API_KEY` in your `.env` file is correct and has sufficient permissions.

### SERP API Rate Limiting

**Issue**: `RateLimitError: SERP API rate limit exceeded`

**Solution**: 
- Implement caching for development to reduce API calls
- Use the mock SERP data provider for testing
- Consider upgrading your SERP API plan

### Database Connection Issues

**Issue**: `OperationalError: Could not connect to the database`

**Solution**:
- Check if your database is running (`docker-compose ps`)
- Verify the `DATABASE_URL` environment variable is correct
- For PostgreSQL, ensure the database exists and user has proper permissions

### Redis Connection Issues

**Issue**: `ConnectionError: Error connecting to Redis`

**Solution**:
- Check if Redis is running (`docker-compose ps`)
- Verify the `REDIS_URL` environment variable is correct
- Try pinging Redis directly: `redis-cli ping`

## Debugging Tips

### Enable Debug Logging

Set `API_LOG_LEVEL=debug` in your `.env` file to enable detailed logging.

### Trace Agents Interaction

Set `TRACING_ENABLED=true` and `TRACING_EXPORTER=console` to see agent interactions in the console.

### Database Debugging

Use a database client like DBeaver or pgAdmin to directly inspect the database state.

### API Request Debugging

Use the Swagger UI at `/docs` to test API endpoints interactively.

## Adding New Components

### Creating a New Agent

1. Create a new file in the `agents/` directory
2. Extend the `BaseAgent` class
3. Register appropriate tools
4. Add comprehensive tests

Example:
```python
from agents.base import BaseAgent
from agents import function_tool

class YourNewAgent(BaseAgent):
    """A specialized agent for a specific task."""
    
    def __init__(self):
        super().__init__(
            name="Your Agent",
            description="Specialized agent for your task",
            instructions="""
            Detailed instructions for the agent...
            """
        )
        self.register_tools([your_tool])
        
@function_tool
def your_tool(param1: str, param2: int) -> dict:
    """Tool description.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Dictionary with results
    """
    # Implementation
    return {"result": "value"}
```

### Adding a New Pipeline Stage

1. Create a new file in the `core/pipeline/` directory
2. Implement the `PipelineStage` interface
3. Add the stage to the pipeline
4. Add comprehensive tests

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to the project.

## Support

For support or questions, please:
1. Check the documentation first
2. Search existing issues on GitHub
3. Create a new issue with detailed information about your problem

## Additional Resources

- [OpenAI Agents SDK Documentation](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/) 