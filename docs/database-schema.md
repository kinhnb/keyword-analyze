# Database Schema Documentation

This document provides a detailed overview of the database schema for the AI SERP Keyword Research Agent. The system uses a relational database to store analysis results, SERP features, and recommendations.

## Overview

The database is designed to store:
- Search term analysis history and results
- SERP features detected in search results
- Recommendations generated based on analysis
- User feedback on recommendations
- API usage statistics

## Database Tables

### 1. SearchAnalysis

The `search_analyses` table stores the primary analysis results for searched terms.

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
CREATE INDEX idx_intent_type ON search_analyses(intent_type);
CREATE INDEX idx_created_at ON search_analyses(created_at);
```

#### Columns:
- `id`: Unique identifier for the analysis (UUID)
- `search_term`: The original search term submitted by the user
- `main_keyword`: The primary keyword identified in the analysis
- `secondary_keywords`: Array of related keywords found in the SERP results
- `intent_type`: Classified intent type (transactional, informational, exploratory, navigational)
- `has_market_gap`: Boolean flag indicating whether a market gap was detected
- `confidence`: Confidence score for the intent classification (0.0-1.0)
- `created_at`: Timestamp when the analysis was created

### 2. SerpFeatures

The `serp_features` table stores information about special features detected in search results.

```sql
CREATE TABLE serp_features (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES search_analyses(id) ON DELETE CASCADE,
    feature_type VARCHAR(50) NOT NULL,
    feature_position INTEGER,
    feature_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analysis_features ON serp_features(analysis_id);
CREATE INDEX idx_feature_type ON serp_features(feature_type);
```

#### Columns:
- `id`: Unique identifier for the feature (UUID)
- `analysis_id`: Foreign key reference to the related search analysis
- `feature_type`: Type of SERP feature (shopping_ads, featured_snippet, image_pack, etc.)
- `feature_position`: Position of the feature in the SERP results (1-based)
- `feature_data`: JSON data containing details about the feature
- `created_at`: Timestamp when the record was created

### 3. Recommendations

The `recommendations` table stores SEO tactics recommended based on the analysis.

```sql
CREATE TABLE recommendations (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES search_analyses(id) ON DELETE CASCADE,
    tactic_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    priority INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analysis_recommendations ON recommendations(analysis_id);
CREATE INDEX idx_tactic_type ON recommendations(tactic_type);
CREATE INDEX idx_priority ON recommendations(priority);
```

#### Columns:
- `id`: Unique identifier for the recommendation (UUID)
- `analysis_id`: Foreign key reference to the related search analysis
- `tactic_type`: Type of SEO tactic (product_page_optimization, content_creation, etc.)
- `description`: Detailed description of the recommended tactic
- `priority`: Priority level of the recommendation (1 = highest)
- `confidence`: Confidence score for the recommendation (0.0-1.0)
- `created_at`: Timestamp when the record was created

### 4. MarketGaps

The `market_gaps` table stores detailed information about market gaps identified in the analysis.

```sql
CREATE TABLE market_gaps (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES search_analyses(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    opportunity_score FLOAT NOT NULL,
    competition_level FLOAT NOT NULL,
    related_keywords TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analysis_gaps ON market_gaps(analysis_id);
CREATE INDEX idx_opportunity_score ON market_gaps(opportunity_score);
```

#### Columns:
- `id`: Unique identifier for the market gap (UUID)
- `analysis_id`: Foreign key reference to the related search analysis
- `description`: Detailed description of the identified market gap
- `opportunity_score`: Score indicating the potential opportunity (0.0-1.0)
- `competition_level`: Score indicating the level of competition (0.0-1.0)
- `related_keywords`: Array of keywords associated with the gap
- `created_at`: Timestamp when the record was created

### 5. UserFeedback

The `user_feedback` table stores feedback provided by users about analysis results.

```sql
CREATE TABLE user_feedback (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES search_analyses(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL,
    comments TEXT,
    helpful_recommendations UUID[],
    was_market_gap_accurate BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_analysis_feedback ON user_feedback(analysis_id);
CREATE INDEX idx_rating ON user_feedback(rating);
```

#### Columns:
- `id`: Unique identifier for the feedback (UUID)
- `analysis_id`: Foreign key reference to the related search analysis
- `rating`: Overall rating of the analysis (1-5)
- `comments`: Text comments provided by the user
- `helpful_recommendations`: Array of recommendation IDs that were marked as helpful
- `was_market_gap_accurate`: Boolean indicating if the market gap detection was accurate
- `created_at`: Timestamp when the feedback was submitted

### 6. ApiUsage

The `api_usage` table tracks API usage for monitoring and rate limiting.

```sql
CREATE TABLE api_usage (
    id UUID PRIMARY KEY,
    api_key_id VARCHAR(64) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 1,
    last_request_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    first_request_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_api_key_usage ON api_usage(api_key_id);
CREATE INDEX idx_endpoint_usage ON api_usage(endpoint);
CREATE INDEX idx_last_request ON api_usage(last_request_at);
```

#### Columns:
- `id`: Unique identifier for the usage record (UUID)
- `api_key_id`: Identifier for the API key used
- `endpoint`: API endpoint accessed
- `request_count`: Number of requests made
- `last_request_at`: Timestamp of the most recent request
- `first_request_at`: Timestamp of the first request in this record

### 7. ApiKeys

The `api_keys` table stores API keys for authentication and rate limiting.

```sql
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    key_hash VARCHAR(255) NOT NULL,
    user_id UUID NOT NULL,
    name VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    rate_limit_per_hour INTEGER DEFAULT 100,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX idx_key_hash ON api_keys(key_hash);
CREATE INDEX idx_user_id ON api_keys(user_id);
```

#### Columns:
- `id`: Unique identifier for the API key (UUID)
- `key_hash`: Secure hash of the API key
- `user_id`: ID of the user associated with this key
- `name`: Optional friendly name for the key
- `enabled`: Whether the key is currently enabled
- `rate_limit_per_hour`: Maximum requests allowed per hour
- `created_at`: Timestamp when the key was created
- `expires_at`: Optional expiration timestamp

## Database Relationships

The following diagram illustrates the relationships between database tables:

```
+-------------------+      +-------------------+      +-------------------+
|   SearchAnalysis  |      |   SerpFeatures    |      |  Recommendations  |
+-------------------+      +-------------------+      +-------------------+
| id (PK)           | 1    | id (PK)           |      | id (PK)           |
| search_term       +------+ analysis_id (FK)  |      | analysis_id (FK)  |
| main_keyword      |      | feature_type      |      | tactic_type       |
| secondary_keywords|      | feature_position  |      | description       |
| intent_type       |      | feature_data      |      | priority          |
| has_market_gap    |      | created_at        |      | confidence        |
| confidence        |      +-------------------+      | created_at        |
| created_at        |                                 +-------------------+
+--------+----------+                                           ^
         |                                                      |
         |                                                      |
         |                                                      |
         v                                                      |
+-------------------+                                           |
|    MarketGaps     |                                           |
+-------------------+                                           |
| id (PK)           |                                           |
| analysis_id (FK)  +-------------------------------------------+
| description       |
| opportunity_score |
| competition_level |
| related_keywords  |
| created_at        |
+--------+----------+
         |
         |
         v
+-------------------+      +-------------------+      +-------------------+
|   UserFeedback    |      |     ApiUsage      |      |     ApiKeys       |
+-------------------+      +-------------------+      +-------------------+
| id (PK)           |      | id (PK)           |      | id (PK)           |
| analysis_id (FK)  |      | api_key_id        +------+ key_hash          |
| rating            |      | endpoint          |      | user_id           |
| comments          |      | request_count     |      | name              |
| helpful_recomm    |      | last_request_at   |      | enabled           |
| market_gap_accur  |      | first_request_at  |      | rate_limit_per_hr |
| created_at        |      +-------------------+      | created_at        |
+-------------------+                                 | expires_at        |
                                                      +-------------------+
```

## Data Types

The schema uses the following PostgreSQL data types:

- **UUID**: Universally unique identifiers for primary keys
- **VARCHAR**: Variable-length character strings with specified maximum lengths
- **TEXT**: Variable-length character strings without length limit
- **TEXT[]**: Arrays of text values (used for storing collections of strings)
- **FLOAT**: Floating-point numbers (used for scores and confidence values)
- **INTEGER**: Whole numbers (used for counts, positions, and ratings)
- **BOOLEAN**: True/false values
- **TIMESTAMP WITH TIME ZONE**: Date and time values with timezone information
- **JSONB**: Binary JSON format for storing hierarchical data structures

## Indexes

To optimize query performance, the schema includes the following indexes:

- Primary key indexes on all tables
- Foreign key indexes on all reference columns
- Search term index for quick lookup of analysis results
- Intent type index for filtering by classification
- Feature type index for finding specific SERP features
- Priority index for sorting recommendations
- Rating index for filtering feedback by score
- API usage indexes for monitoring and rate limiting

## Migrations

Database migrations are managed using Alembic, a lightweight database migration tool for SQLAlchemy. Migration scripts are stored in the `data/migrations` directory and can be run using the Alembic CLI:

```bash
# Apply all migrations
python -m alembic upgrade head

# Create a new migration
python -m alembic revision -m "description of changes"

# Rollback the last migration
python -m alembic downgrade -1
```

## Repository Pattern Implementation

The system implements the Repository pattern to abstract database operations from business logic:

```python
class SearchAnalysisRepository(BaseRepository[SearchAnalysis]):
    """Repository for managing SearchAnalysis entities."""
    
    async def find_by_search_term(self, search_term: str) -> Optional[SearchAnalysis]:
        """Find analysis by search term."""
        query = select(SearchAnalysis).where(SearchAnalysis.search_term == search_term)
        result = await self.session.execute(query)
        return result.scalars().first()
    
    async def find_with_related_data(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Find analysis with related features, market gaps, and recommendations."""
        # Implementation with joins
        pass
    
    async def create(self, analysis: SearchAnalysisCreate) -> SearchAnalysis:
        """Create a new search analysis record."""
        db_analysis = SearchAnalysis(**analysis.model_dump())
        self.session.add(db_analysis)
        await self.session.commit()
        await self.session.refresh(db_analysis)
        return db_analysis
```

## Database Configuration

Database connection settings are managed through environment variables:

```python
# Database configuration
DATABASE_URL=sqlite:///./data/app.db  # For development
# DATABASE_URL=postgresql://user:password@localhost:5432/keyword_research  # For production

# Connection pool settings
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

For production environments, the system uses PostgreSQL with connection pooling for improved performance.

## Best Practices

When working with the database, follow these best practices:

1. **Use Repositories**: Always access database through repository classes
2. **Validate Input**: Validate all user input before database operations
3. **Use Transactions**: Wrap related operations in transactions
4. **Limit Result Sets**: Use pagination for large result sets
5. **Optimize Queries**: Use appropriate indexes and query optimization
6. **Handle Exceptions**: Properly catch and handle database exceptions
7. **Use Migrations**: Use Alembic migrations for schema changes
8. **Test Repositories**: Create comprehensive tests for repository classes

## Development vs. Production

The system supports different database configurations for development and production environments:

- **Development**: SQLite database for simplicity and ease of setup
- **Production**: PostgreSQL database for performance, scalability, and reliability

Connection settings are automatically detected from the `DATABASE_URL` environment variable. 