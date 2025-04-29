Before diving into the best practices, please note that you may need to adapt the globs depending on your project's specific file structure and requirements.

---
name: openai-agents-sdk-best-practices.mdc
description: Best practices for using OpenAI Agents SDK
globs: **/*.{py}
---

- Use the latest stable version of the SDK for optimal performance and features
- Implement error handling and retries for agent operations
- Utilize the SDK's built-in logging for better debugging and monitoring
- Follow the SDK's guidelines for agent configuration and orchestration

---
name: fastapi-best-practices.mdc
description: Best practices for FastAPI development
globs: **/*.{py}
---

- Use type hints for all function parameters and return types
- Implement proper error handling with custom exception handlers
- Use dependency injection for database sessions and other resources
- Leverage FastAPI's built-in support for asynchronous programming
- Implement proper API documentation using OpenAPI and Swagger UI

---
name: sqlalchemy-best-practices.mdc
description: Best practices for using SQLAlchemy
globs: **/*.{py}
---

- Use declarative base for defining models
- Implement proper transaction management
- Use eager loading for related objects to reduce query count
- Utilize SQLAlchemy's ORM features for complex queries
- Implement proper indexing on frequently queried columns

---
name: alembic-best-practices.mdc
description: Best practices for database migrations with Alembic
globs: **/*.{py}
---

- Use meaningful revision messages for each migration
- Implement proper downgrades for reversible migrations
- Use Alembic's autogenerate feature cautiously and review generated migrations
- Keep migrations idempotent where possible
- Test migrations thoroughly in a staging environment before production deployment

---
name: httpx-best-practices.mdc
description: Best practices for using HTTPX
globs: **/*.{py}
---

- Use async client for better performance in asynchronous applications
- Implement proper timeout settings for all requests
- Use HTTPX's built-in support for JSON and form data
- Implement proper error handling for different HTTP status codes
- Utilize HTTPX's streaming capabilities for large payloads

---
name: pydantic-best-practices.mdc
description: Best practices for using Pydantic
globs: **/*.{py}
---

- Use Pydantic models for request/response validation
- Implement custom validators for complex validation logic
- Use Pydantic's built-in support for ORM mode when working with databases
- Utilize Pydantic's configuration options for serialization and deserialization
- Implement proper error handling for validation errors

---
name: numpy-best-practices.mdc
description: Best practices for using NumPy
globs: **/*.{py}
---

- Use vectorized operations for better performance
- Implement proper memory management for large arrays
- Utilize NumPy's broadcasting feature for efficient computations
- Use NumPy's built-in functions for common mathematical operations
- Implement proper error handling for numerical computations

---
name: pandas-best-practices.mdc
description: Best practices for using Pandas
globs: **/*.{py}
---

- Use appropriate data types for columns to optimize memory usage
- Implement proper indexing for faster data access
- Utilize Pandas' vectorized operations for data manipulation
- Use Pandas' built-in functions for data cleaning and transformation
- Implement proper error handling for data operations

---
name: loguru-best-practices.mdc
description: Best practices for using Loguru
globs: **/*.{py}
---

- Use structured logging for better log analysis
- Implement proper log levels for different types of messages
- Utilize Loguru's context variables for correlation IDs
- Use Loguru's built-in support for exception logging
- Implement proper log rotation and retention policies

---
name: opentelemetry-best-practices.mdc
description: Best practices for using OpenTelemetry
globs: **/*.{py}
---

- Use OpenTelemetry for distributed tracing and metrics
- Implement proper span naming and attributes for better trace analysis
- Utilize OpenTelemetry's context propagation for distributed systems
- Use OpenTelemetry's built-in support for logging integration
- Implement proper sampling strategies for high-volume applications

---
name: pytest-best-practices.mdc
description: Best practices for using Pytest
globs: **/*.{py}
---

- Use fixtures for setup and teardown of test resources
- Implement proper test parameterization for testing multiple scenarios
- Use Pytest's built-in assertions for better test readability
- Utilize Pytest's markers for categorizing and running specific tests
- Implement proper test coverage analysis using pytest-cov

---
name: black-best-practices.mdc
description: Best practices for using Black
globs: **/*.{py}
---

- Use Black for consistent code formatting across the project
- Implement Black as a pre-commit hook for automatic formatting
- Use Black's configuration options to customize formatting rules
- Utilize Black's integration with IDEs for real-time formatting
- Implement proper code review processes to ensure Black compliance

---
name: mkdocs-best-practices.mdc
description: Best practices for using MkDocs
globs: **/*.{md}
---

- Use MkDocs for generating project documentation
- Implement proper navigation structure for easy document browsing
- Utilize MkDocs' built-in support for Markdown extensions
- Use MkDocs Material theme for a professional look and feel
- Implement proper version control for documentation updates