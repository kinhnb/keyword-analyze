# Project Overview

## Project Summary
[PROJECT_NAME] is built on the OpenAI Agents SDK framework. This project leverages the power of AI agents to [DESCRIBE_PRIMARY_FUNCTIONALITY_AND_PURPOSE]. The system architecture is designed around the OpenAI Agents SDK core concepts:

- **Multi-Agent Orchestration**: [DESCRIBE_HOW_AGENTS_COLLABORATE]
- **Tool-Based Capabilities**: [DESCRIBE_KEY_FUNCTION_TOOLS]
- **Knowledge-Driven Intelligence**: [DESCRIBE_KNOWLEDGE_SOURCES]
- **API-First Design**: [DESCRIBE_INTEGRATION_APPROACH]

## OpenAI Agents Architecture
```
[INSERT_ARCHITECTURE_DIAGRAM_HERE]
```

## Project Structure
The project follows Clean Architecture principles with clear separation of concerns:

```
[PROJECT_NAME]/
├── agents/                   # AI agents powered by OpenAI Agents SDK
│   ├── main_agent.py         # [DESCRIBE_MAIN_AGENT]
│   ├── [AGENT_1].py          # [DESCRIBE_AGENT_1]
│   ├── [AGENT_2].py          # [DESCRIBE_AGENT_2]
│   └── [AGENT_3].py          # [DESCRIBE_AGENT_3]
├── guardrails/               # Safety and validation mechanisms
│   ├── input_guardrails.py   # Input validation guardrails
│   └── output_guardrails.py  # Output validation guardrails
├── core/                     # Core business logic
│   ├── pipeline/             # [DESCRIBE_PIPELINE]
│   │   ├── [STAGE_1].py      # [DESCRIBE_STAGE_1]
│   │   ├── [STAGE_2].py      # [DESCRIBE_STAGE_2]
│   │   └── [STAGE_3].py      # [DESCRIBE_STAGE_3]
│   ├── strategies/           # [DESCRIBE_STRATEGIES]
│   │   ├── [STRATEGY_1].py   # [DESCRIBE_STRATEGY_1]
│   │   └── [STRATEGY_2].py   # [DESCRIBE_STRATEGY_2]
│   └── [OTHER_CORE_MODULES]/ # [DESCRIBE_OTHER_MODULES]
├── tools/                    # Function tools for agents
│   ├── [TOOL_1].py           # [DESCRIBE_TOOL_1]
│   ├── [TOOL_2].py           # [DESCRIBE_TOOL_2]
│   └── [TOOL_3].py           # [DESCRIBE_TOOL_3]
├── data/                     # Data access layer
│   ├── repositories/         # Repository pattern implementations
│   │   ├── [REPO_1].py       # [DESCRIBE_REPO_1]
│   │   └── [REPO_2].py       # [DESCRIBE_REPO_2]
│   ├── models/               # Data models
│   │   ├── [MODEL_1].py      # [DESCRIBE_MODEL_1]
│   │   └── [MODEL_2].py      # [DESCRIBE_MODEL_2]
│   └── migrations/           # Database migrations
├── api/                      # API endpoints
│   ├── routes/               # Route definitions
│   │   ├── [ROUTE_1].py      # [DESCRIBE_ROUTE_1]
│   │   └── [ROUTE_2].py      # [DESCRIBE_ROUTE_2]
│   ├── middleware/           # API middleware
│   └── schemas/              # Request/response schemas
├── services/                 # External service integrations
│   ├── [SERVICE_1]/          # [DESCRIBE_SERVICE_1]
│   └── [SERVICE_2].py        # [DESCRIBE_SERVICE_2]
├── orchestration/            # Multi-agent workflow orchestration
│   ├── workflows/            # Defined agent workflows
│   ├── handoffs/             # Agent handoff definitions
│   └── evaluators/           # Output evaluation components
├── tracing/                  # Tracing and monitoring
│   ├── processors/           # Custom trace processors
│   └── exporters/            # Trace export integrations 
├── utils/                    # Utility functions
│   ├── [UTIL_1]/             # [DESCRIBE_UTIL_1]
│   └── [UTIL_2]/             # [DESCRIBE_UTIL_2]
└── tests/                    # Test suite (pytest)
    ├── unit/                 # Unit tests
    ├── agents/               # Agent-specific tests
    └── integration/          # Integration tests
```

## Key Patterns & Concepts

1. **Agent Pattern**:
   - [DESCRIBE_AGENT_RESPONSIBILITIES]
   - [DESCRIBE_AGENT_INTERACTIONS]
   - [DESCRIBE_TOOL_APPROACH]
   
```python
# Example agent implementation
from openai_agents_sdk import Agent, Tool, KnowledgeSource

def [TOOL_FUNCTION_NAME]([PARAMETERS]):
    """[TOOL_DESCRIPTION]"""
    # Implementation
    return [RESULT]

# Define knowledge source
[KNOWLEDGE_NAME] = KnowledgeSource(
    name="[NAME]",
    description="[DESCRIPTION]",
    loader=[LOADER_FUNCTION]
)

# Create the agent
[AGENT_NAME] = Agent(
    name="[NAME]",
    description="[DESCRIPTION]",
    instructions="""
    [DETAILED_INSTRUCTIONS]
    """,
    tools=[
        Tool(
            name="[TOOL_NAME]",
            description="[TOOL_DESCRIPTION]",
            function=[FUNCTION_REFERENCE]
        ),
        # Additional tools...
    ],
    knowledge=[KNOWLEDGE_SOURCES]
)
```

2. **Pipeline Pattern**:
   - [DESCRIBE_PIPELINE_APPROACH]
   - [DESCRIBE_PIPELINE_STAGES]
   - [DESCRIBE_DATA_FLOW]
   
```python
# Example pipeline implementation
class [PIPELINE_NAME]:
    def __init__(self):
        self.stages = [
            [STAGE_1](),
            [STAGE_2](),
            [STAGE_3]()
        ]
    
    async def process(self, [INPUT_DATA]):
        context = {"data": [INPUT_DATA]}
        
        for stage in self.stages:
            context = await stage.process(context)
            
            # Exit conditions if needed
            if context.get("error"):
                return context
                
        return context
```

3. **Repository Pattern**:
   - [DESCRIBE_REPOSITORY_APPROACH]
   - [DESCRIBE_DATA_ACCESS]
   - [DESCRIBE_PERSISTENCE_LAYER]
   
```python
# Example repository implementation
class [REPOSITORY_NAME]:
    def __init__(self, [DEPENDENCIES]):
        self.[DEPENDENCY] = [DEPENDENCY]
    
    async def find_by_[CRITERIA](self, [PARAMETERS]):
        """[METHOD_DESCRIPTION]"""
        # Implementation
        return [RESULT]
    
    async def save(self, [ENTITY]):
        """[METHOD_DESCRIPTION]"""
        # Implementation
        return [RESULT]
```

4. **Guardrails Pattern**:
   - [DESCRIBE_GUARDRAIL_APPROACH]
   - [DESCRIBE_INPUT_VALIDATION]
   - [DESCRIBE_OUTPUT_VALIDATION]
   
```python
# Example guardrail implementation
from openai_agents_sdk import Agent, GuardrailFunctionOutput, input_guardrail, RunContextWrapper
from pydantic import BaseModel

class [VALIDATION_OUTPUT](BaseModel):
    is_valid: bool
    reasoning: str

@input_guardrail
async def [GUARDRAIL_NAME](
    ctx: RunContextWrapper, 
    agent: Agent, 
    input: str
) -> GuardrailFunctionOutput:
    """[GUARDRAIL_DESCRIPTION]"""
    # Implementation to validate input
    return GuardrailFunctionOutput(
        output_info=[VALIDATION_RESULT],
        tripwire_triggered=[CONDITION]
    )
```

5. **Multi-Agent Orchestration**:
   - [DESCRIBE_ORCHESTRATION_APPROACH]
   - [DESCRIBE_AGENT_HANDOFFS]
   - [DESCRIBE_WORKFLOW_MANAGEMENT]
   
```python
# Example orchestration implementation
from openai_agents_sdk import Agent, Runner

# Define specialized agents
[AGENT_1] = Agent(
    name="[NAME]",
    instructions="[INSTRUCTIONS]",
    tools=[...]
)

[AGENT_2] = Agent(
    name="[NAME]",
    instructions="[INSTRUCTIONS]",
    tools=[...]
)

# Define orchestration agent with handoffs
[ORCHESTRATOR] = Agent(
    name="[NAME]",
    instructions="[INSTRUCTIONS]",
    handoffs=[[AGENT_1], [AGENT_2]]
)

async def [WORKFLOW_FUNCTION]([INPUT]):
    """[WORKFLOW_DESCRIPTION]"""
    result = await Runner.run([ORCHESTRATOR], [INPUT])
    return result.final_output
```

## Core Domain Models

1. **[DOMAIN_MODEL_1]**:
   - [DESCRIBE_MODEL_CHARACTERISTICS]
   - [DESCRIBE_MODEL_RELATIONSHIPS]
   
```python
# Example domain model
class [MODEL_NAME](Base):
    __tablename__ = "[TABLE_NAME]"
    
    id = Column([ID_TYPE], primary_key=True, default=[DEFAULT_FUNCTION])
    [FIELD_1] = Column([TYPE], [CONSTRAINTS])
    [FIELD_2] = Column([TYPE], [CONSTRAINTS])
    
    # Relationships
    [RELATIONSHIP_1] = relationship("[RELATED_MODEL]", back_populates="[BACKREF]")
```

2. **[DOMAIN_MODEL_2]**:
   - [DESCRIBE_MODEL_CHARACTERISTICS]
   - [DESCRIBE_MODEL_RELATIONSHIPS]
   
```python
# Example domain model
class [MODEL_NAME](Base):
    __tablename__ = "[TABLE_NAME]"
    
    id = Column([ID_TYPE], primary_key=True, default=[DEFAULT_FUNCTION])
    [FIELD_1] = Column([TYPE], [CONSTRAINTS])
    [FIELD_2] = Column([TYPE], [CONSTRAINTS])
    
    # Relationships
    [RELATIONSHIP_1] = relationship("[RELATED_MODEL]", back_populates="[BACKREF]")
```

## Infrastructure Highlights

1. **Database Layer**:
   - [DESCRIBE_DATABASE_TECHNOLOGIES]
   - [DESCRIBE_ORM_APPROACH]
   - [DESCRIBE_DATA_ACCESS_PATTERNS]
   
```python
# Example database setup
async def init_db():
    # Database setup
    [DB_ENGINE] = create_async_engine(
        settings.[DB_URL], 
        echo=settings.DEBUG
    )
    
    # Session creation
    [SESSION_MAKER] = sessionmaker(
        [DB_ENGINE], 
        expire_on_commit=False, 
        class_=AsyncSession
    )
    
    # Additional setup (indices, migrations, etc.)
    
    return {
        "engine": [DB_ENGINE],
        "session": [SESSION_MAKER],
        # Other DB-related objects
    }
```

2. **Tracing and Monitoring**:
   - [DESCRIBE_TRACING_APPROACH]
   - [DESCRIBE_MONITORING_TOOLS]
   - [DESCRIBE_OBSERVABILITY_STRATEGY]
   
```python
# Example tracing setup
from openai_agents_sdk import configure_tracing
from openai_agents_sdk.tracing import ConsoleExporter

# Configure tracing with custom exporter
configure_tracing(
    service_name="[SERVICE_NAME]",
    exporter=ConsoleExporter(),  # Or custom exporter
    sample_rate=1.0,             # Capture all traces
)

# Custom trace processor example
class [CUSTOM_PROCESSOR]:
    def process_trace(self, trace):
        # Process and export trace data
        pass
```

3. **Streaming Support**:
   - [DESCRIBE_STREAMING_APPROACH]
   - [DESCRIBE_REAL_TIME_PROCESSING]
   
```python
# Example streaming implementation
from openai_agents_sdk import Agent, Runner
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.websocket("/stream")
async def stream_agent(websocket: WebSocket):
    await websocket.accept()
    
    # Get input from client
    data = await websocket.receive_text()
    
    # Create streaming context
    async for chunk in Runner.stream([AGENT], data):
        if chunk.content:
            await websocket.send_text(chunk.content)
    
    await websocket.close()
```

4. **API Layer**:
   - [DESCRIBE_API_FRAMEWORK]
   - [DESCRIBE_API_DOCUMENTATION]
   - [DESCRIBE_REQUEST_VALIDATION]
   
```python
# Example API endpoint
from [WEB_FRAMEWORK] import [COMPONENTS]

router = [ROUTER_SETUP]

class [REQUEST_MODEL](BaseModel):
    [FIELD_1]: [TYPE]
    [FIELD_2]: [TYPE] = [DEFAULT_VALUE]

class [RESPONSE_MODEL](BaseModel):
    [FIELD_1]: [TYPE]
    [FIELD_2]: [TYPE]

@router.[HTTP_METHOD]("[ROUTE_PATH]", response_model=[RESPONSE_MODEL])
async def [ENDPOINT_FUNCTION](
    [REQUEST_PARAMETER]: [REQUEST_MODEL],
    [SERVICE] = Depends([SERVICE_PROVIDER])
):
    try:
        result = await [SERVICE].[METHOD]([PARAMETERS])
        return result
    except [EXCEPTION_1] as e:
        raise [HTTP_EXCEPTION]([STATUS_CODE], detail=str(e))
    except [EXCEPTION_2] as e:
        raise [HTTP_EXCEPTION]([STATUS_CODE], detail=str(e))
```

## Key Flows

1. **[FLOW_1]**:
   ```
   [STEP_1] → [STEP_2] → [STEP_3] → [STEP_4] → [STEP_5]
   ```

2. **[FLOW_2]**:
   ```
   [STEP_1] → [STEP_2] → [STEP_3] → [STEP_4]
   ```

3. **Orchestration Flow**:
   ```
   User Input → Guardrail Validation → Orchestrator Agent → 
   Agent Selection → Specialized Agent Execution → 
   Result Processing → Output Guardrail → Response
   ```
   
   Implementation:
   
```python
# Example flow implementation
class [FLOW_IMPLEMENTATION]:
    def __init__(self, [DEPENDENCIES]):
        self.[DEPENDENCY] = [DEPENDENCY]
    
    async def [PROCESS_METHOD](self, [PARAMETERS]):
        """[METHOD_DESCRIPTION]"""
        # Implementation
        return [RESULT]
```

## Getting Started Tips

1. **Initial Setup**:
   - [SETUP_STEP_1]
   - [SETUP_STEP_2]
   - [SETUP_STEP_3]
   - [SETUP_STEP_4]

2. **Development Workflow**:
   - [WORKFLOW_STEP_1]
   - [WORKFLOW_STEP_2]
   - [WORKFLOW_STEP_3]
   - [WORKFLOW_STEP_4]

3. **Agent Development with OpenAI Agents SDK**:
   - [AGENT_DEV_STEP_1]
   - [AGENT_DEV_STEP_2]
   - [AGENT_DEV_STEP_3]
   - [AGENT_DEV_STEP_4]
   - [AGENT_DEV_STEP_5]
   - [AGENT_DEV_STEP_6]

4. **Guardrail Development**:
   - Define clear validation criteria for inputs and outputs
   - Implement input guardrails to validate and sanitize user inputs
   - Implement output guardrails to ensure responses meet quality standards
   - Test guardrails with edge cases and potentially problematic inputs
   - Configure tripwire mechanisms for handling validation failures

5. **Testing Strategy**:
   - [TEST_STRATEGY_1]
   - [TEST_STRATEGY_2]
   - [TEST_STRATEGY_3]
   - [TEST_STRATEGY_4]
   - [TEST_STRATEGY_5]
   - [TEST_STRATEGY_6]

## Important Dependencies

- **Core**:
  - `openai-agents-sdk`: Core framework for building and orchestrating AI agents
  - `[DEPENDENCY_1]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_2]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_3]`: [DESCRIBE_USAGE]

- **[CATEGORY_1]**:
  - `[DEPENDENCY_1]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_2]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_3]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_4]`: [DESCRIBE_USAGE]

- **Monitoring & Tracing**:
  - `logfire`: Integration for advanced logging and monitoring
  - `agentops`: Agent operations visibility and analysis
  - `braintrust`: Agent evaluation and performance tracking
  - `scorecard`: Scoring agent performance and outputs
  - `keywordsai`: Tracing and analysis tools for LLM-based systems

- **Development**:
  - `[DEPENDENCY_1]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_2]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_3]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_4]`: [DESCRIBE_USAGE]
  - `[DEPENDENCY_5]`: [DESCRIBE_USAGE]

## Orchestration Patterns

1. **LLM-Driven Orchestration**:
   - [DESCRIBE_LLM_ORCHESTRATION]
   - [DESCRIBE_AUTONOMOUS_PLANNING]
   - [DESCRIBE_DYNAMIC_TOOL_SELECTION]

2. **Code-Driven Orchestration**:
   - [DESCRIBE_CODE_ORCHESTRATION]
   - [DESCRIBE_DETERMINISTIC_FLOWS]
   - [DESCRIBE_EXPLICIT_HANDOFFS]

3. **Hybrid Orchestration**:
   - [DESCRIBE_HYBRID_APPROACH]
   - [DESCRIBE_BALANCING_FLEXIBILITY_CONTROL]
   - [DESCRIBE_DECISION_CRITERIA]

This structure provides a robust foundation for building an intelligent [PROJECT_TYPE] system with [KEY_CAPABILITY_1] and [KEY_CAPABILITY_2] capabilities. 