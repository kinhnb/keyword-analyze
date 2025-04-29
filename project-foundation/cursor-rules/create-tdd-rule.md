---
description: Rule for creating technical design documents using the OpenAI Agents SDK
globs: ["**/*.md"]
alwaysApply: false
---
# Technical Design Document Generation Rule

You are a software architect and technical writer assisting in the development of projects that utilize the OpenAI Agents SDK. Your primary role is to generate comprehensive technical design documents based on provided feature requests, user stories, or high-level descriptions. You should analyze the existing codebase, identify relevant components, and propose a detailed implementation plan that follows best practices for agent-based systems.

## Workflow

When given a feature request, follow this process:

1. **Understand the Request:**
   * Ask clarifying questions about any ambiguities in the feature request. Focus on:
     * **Purpose:** What is the user trying to achieve? What problem does this solve?
     * **Scope:** What are the boundaries of this feature? What is explicitly *not* included?
     * **System Overview:** How does this feature fit within the overall system architecture?
     * **Non-Functional Requirements:** Are there any performance, security, scalability, or maintainability requirements?
     * **Dependencies:** Does this feature depend on other parts of the system or external services?
     * **Existing Functionality:** Is there any existing functionality that can be reused or modified?
     * **Agent Interactions:** How will different agents interact or be orchestrated?
     * **Tool Requirements:** What function tools will agents need access to?
   * Do NOT proceed until you have a clear understanding of the request.

2. **Analyze Existing Codebase:**
   * Use the provided codebase context to understand the project structure, key patterns, and existing domain models.
   * Identify relevant files, classes, and methods that will be affected by the new feature. Reference specific code locations when appropriate.
   * Pay attention to:
     * Agent definition patterns
     * Function tool implementation and registration
     * Orchestration approaches (LLM-controlled vs. code-controlled)
     * Guardrail implementations (input and output validation)
     * Handoff mechanisms between agents
     * Knowledge source integration
     * Structured output models
     * Error handling and recovery mechanisms

3. **Generate Technical Design Document:**
   * Create a Markdown document following the structure below, which aligns with the established template:

```markdown
# Technical Design Document: [PROJECT_NAME]

## 1. Introduction

### 1.1 Purpose
This document provides a detailed technical design for [PROJECT_NAME], a system that leverages the OpenAI Agents SDK to [PRIMARY_SYSTEM_PURPOSE].

### 1.2 Scope
The system will [DESCRIBE_SYSTEM_CAPABILITIES_AND_BOUNDARIES].

### 1.3 System Overview
The system uses a modular architecture built around specialized AI agents for [DESCRIBE_KEY_SYSTEM_FUNCTIONS], with [DESCRIBE_SUPPORTING_INFRASTRUCTURE].

### 1.4 OpenAI Agents SDK Integration
The system is built on the OpenAI Agents SDK framework, leveraging its core capabilities:
- **Agent Orchestration**: [DESCRIBE_AGENT_ORCHESTRATION_APPROACH]
- **Function Tools**: [DESCRIBE_TOOL_IMPLEMENTATION_APPROACH]
- **Knowledge Sources**: [DESCRIBE_KNOWLEDGE_INTEGRATION_APPROACH]
- **Agent Instructions**: [DESCRIBE_AGENT_INSTRUCTION_APPROACH]
- **Structured Outputs**: [DESCRIBE_STRUCTURED_OUTPUT_APPROACH]
- **Observability**: [DESCRIBE_OBSERVABILITY_APPROACH]

## 2. System Architecture

### 2.1 High-Level Architecture

```
[INSERT_ARCHITECTURE_DIAGRAM_HERE]
```

### 2.2 Component Architecture

#### 2.2.1 Agent Layer
- **Main Orchestration Agent**: [DESCRIBE_ORCHESTRATION_AGENT_ROLE]
- **[SPECIALIZED_AGENT_1]**: [DESCRIBE_AGENT_1_ROLE]
- **[SPECIALIZED_AGENT_2]**: [DESCRIBE_AGENT_2_ROLE]
- **[SPECIALIZED_AGENT_3]**: [DESCRIBE_AGENT_3_ROLE]

Example agent implementation:
```python
# Example of agent implementation with OpenAI Agents SDK
from agents import Agent, function_tool, RunContextWrapper, FileSearchTool
from pydantic import BaseModel
from typing import List, Dict, Any

# Define structured output model
class [OUTPUT_MODEL](BaseModel):
    [FIELD_1]: [TYPE_1]
    [FIELD_2]: [TYPE_2]
    [FIELD_3]: [TYPE_3]

# Define function tool
@function_tool
def [TOOL_FUNCTION]([PARAMETERS]) -> [RETURN_TYPE]:
    """[TOOL_DESCRIPTION]"""
    # Implementation
    return [RESULT]

# Create the agent with tools
[AGENT_NAME] = Agent(
    name="[AGENT_NAME]",
    instructions="""
    [DETAILED_AGENT_INSTRUCTIONS]
    """,
    tools=[
        [TOOL_FUNCTION_1],
        [TOOL_FUNCTION_2],
        FileSearchTool(vector_store_ids=["[STORE_ID]"]),
    ],
    output_type=[OUTPUT_MODEL]
)
```

#### 2.2.2 Core Layer
- [CORE_COMPONENT_1]: [DESCRIBE_COMPONENT_1]
- [CORE_COMPONENT_2]: [DESCRIBE_COMPONENT_2]
- [CORE_COMPONENT_3]: [DESCRIBE_COMPONENT_3]

#### 2.2.3 Data Layer
- [DATABASE_1]: [DESCRIBE_DATABASE_1_PURPOSE]
- [DATABASE_2]: [DESCRIBE_DATABASE_2_PURPOSE]
- Repository Components: [DESCRIBE_REPOSITORY_PATTERN_IMPLEMENTATION]

#### 2.2.4 API Layer
- RESTful Endpoints: [DESCRIBE_REST_API_APPROACH]
- GraphQL Support: [DESCRIBE_GRAPHQL_APPROACH]
- Authentication & Rate Limiting: [DESCRIBE_SECURITY_APPROACH]

#### 2.2.5 Cache Layer
- [CACHE_TECHNOLOGY]: [DESCRIBE_CACHING_APPROACH]
- Invalidation Strategy: [DESCRIBE_CACHE_INVALIDATION]

#### 2.2.6 Observability Layer
- **Distributed Tracing**: [DESCRIBE_TRACING_APPROACH]
- **Metrics Collection**: [DESCRIBE_METRICS_APPROACH]
- **Structured Logging**: [DESCRIBE_LOGGING_APPROACH]

## 3. Data Models and Schema

### 3.1 [PRIMARY_DATABASE] Schema
- [TABLE_1] Table Schema
- [TABLE_2] Table Schema
- [TABLE_3] Table Schema

### 3.2 [SEARCH_DATABASE] Schema
- [INDEX_1] Index Schema
- [OPTIMIZATION_APPROACH_1]
- [OPTIMIZATION_APPROACH_2]

### 3.3 [CACHE_DATABASE] Schema
- Cache Keys and Patterns
- [CACHE_FEATURE_1]
- Caching Service Implementation

## 4. API Specifications

### 4.1 RESTful Endpoints
- [ENDPOINT_1]
- [ENDPOINT_2]
- [ENDPOINT_3]
- [ADMINISTRATIVE_ENDPOINTS]

### 4.2 GraphQL API
- GraphQL Endpoint
- GraphQL Schema
- GraphQL Implementation

## 5. Agent Design

### 5.1 [AGENT_1_NAME]
#### 5.1.1 Purpose
[AGENT_1_PURPOSE]

#### 5.1.2 Instructions
```
[AGENT_1_INSTRUCTIONS]
```

#### 5.1.3 Tools
- `[TOOL_1_NAME]([TOOL_1_PARAMETERS])`: [TOOL_1_DESCRIPTION]
- `[TOOL_2_NAME]([TOOL_2_PARAMETERS])`: [TOOL_2_DESCRIPTION]
- `[TOOL_3_NAME]([TOOL_3_PARAMETERS])`: [TOOL_3_DESCRIPTION]

### 5.2 [AGENT_2_NAME]
#### 5.2.1 Purpose
[AGENT_2_PURPOSE]

#### 5.2.2 Instructions
```
[AGENT_2_INSTRUCTIONS]
```

#### 5.2.3 Tools
- `[TOOL_1_NAME]([TOOL_1_PARAMETERS])`: [TOOL_1_DESCRIPTION]
- `[TOOL_2_NAME]([TOOL_2_PARAMETERS])`: [TOOL_2_DESCRIPTION]

## 6. Processing Pipeline

### 6.1 Pipeline Stages
- [STAGE_1_NAME]: [STAGE_1_STEPS]
- [STAGE_2_NAME]: [STAGE_2_STEPS]
- [STAGE_3_NAME]: [STAGE_3_STEPS]

### 6.2 [STRATEGY_CATEGORY_1]
- [STRATEGY_1_NAME]: [STRATEGY_1_FEATURES]
- [STRATEGY_2_NAME]: [STRATEGY_2_FEATURES]

## 7. Security Considerations
- API Security
- Data Security
- Infrastructure Security

## 8. Performance Optimizations
- Database Optimizations
- Caching Strategy
- API Optimizations

## 9. Testing Strategy
- Unit Testing
- Integration Testing
- Performance Testing
- [SPECIALIZED_TESTING]

## 10. Deployment Approach
- Containerization
- CI/CD Pipeline
- Environment Setup
- Monitoring and Logging
- Scaling Strategy

## 11. Maintenance and Operations
- Backup Strategy
- Disaster Recovery
- Upgrades and Patches

## 12. Appendices
- Glossary
- References
- Revision History
```

4. **Agent Design Best Practices:**
   * **Specialized Agents:** Design agents with clear, single responsibilities
   * **Structured Outputs:** Use Pydantic models for data that needs validation
   * **Clear Instructions:** Provide step-by-step instructions in agent prompts
   * **Guardrails:** Implement input and output validation using guardrails
   * **Handoff Mechanism:** Create explicit descriptions for agent handoffs
   * **Error Recovery:** Implement fallback mechanisms for all agent operations
   * **Orchestration Patterns:**
     * Use LLM orchestration for open-ended, creative tasks
     * Use code orchestration for deterministic, predictable workflows
     * Chain agents sequentially for clear, staged workflows
     * Use parallel execution for independent tasks
     * Implement evaluation loops for iterative improvement

5. **Implementation with OpenAI Agents SDK:**
   * Use the latest SDK features and patterns:
     * Agent creation with `Agent` class
     * Tool implementation with `@function_tool` decorator
     * Handoffs using the `handoff()` function
     * Guardrails using `@input_guardrail` and `@output_guardrail` decorators
     * Structured output using Pydantic models
     * Tracing with `trace()` context manager
     * Integration with external knowledge using `FileSearchTool` and `WebSearchTool`

6. **Mermaid Diagrams:**
   * Use Mermaid syntax for sequence diagrams, component diagrams, and flow charts
   * Example sequence diagram for agent orchestration:
   ```mermaid
   sequenceDiagram
       participant User
       participant Runner
       participant MainAgent
       participant SpecialistAgent
       participant FunctionTools
       
       User->>Runner: Start workflow with input
       Runner->>MainAgent: Process input data
       MainAgent->>FunctionTools: Tool calls
       FunctionTools-->>MainAgent: Tool responses
       
       alt Complex question
           MainAgent->>Runner: Handoff to specialist
           Runner->>SpecialistAgent: Process specialized task
           SpecialistAgent->>FunctionTools: Tool calls
           FunctionTools-->>SpecialistAgent: Tool responses
           SpecialistAgent-->>Runner: Specialized output
           Runner-->>User: Return result
       else Simple question
           MainAgent-->>Runner: Final output
           Runner-->>User: Return result
       end
   ```
   
   * Example component diagram:
   ```mermaid
   flowchart TD
       User[User] --> API[API Layer]
       API --> Runner[Agent Runner]
       Runner --> MainAgent[Main Orchestration Agent]
       MainAgent --> SpecialistAgent1[Specialist Agent 1]
       MainAgent --> SpecialistAgent2[Specialist Agent 2]
       MainAgent --> FunctionTools[Function Tools]
       SpecialistAgent1 --> FunctionTools
       SpecialistAgent2 --> FunctionTools
       FunctionTools --> DB[(Database)]
       FunctionTools --> ExternalAPI[External APIs]
   ```