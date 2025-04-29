# Implementation Guide: OpenAI Agents SDK (Python)

This document provides a comprehensive guide for implementing AI agents using the OpenAI Agents SDK in Python, based on the latest official documentation and best practices.

---

## 1. Environment Setup
- Python >= 3.8
- Create a virtual environment:
  ```sh
  mkdir my_agent_project
  cd my_agent_project
  python -m venv venv
  source venv/bin/activate  # or venv\Scripts\activate on Windows
  ```

## 2. Installation
- Install the OpenAI Agents SDK:
  ```sh
  pip install openai-agents
  ```
- For voice capabilities (optional):
  ```sh
  pip install 'openai-agents[voice]'
  ```
- Set up your API key:
  ```sh
  export OPENAI_API_KEY=sk-...  # or set in .env file
  ```

## 3. Project Structure
```
my-agent-project/
├── agents/                    # Agent definitions
│   ├── main_agent.py          # Main orchestration agent
│   ├── specialized_agent_1.py # Specialized agent implementation
│   └── specialized_agent_2.py # Another specialized agent
├── tools/                     # Function tools implementation
│   ├── data_tools.py          # Data manipulation tools
│   ├── external_api_tools.py  # External API integration tools
│   └── utility_tools.py       # Utility function tools
├── guardrails/                # Guardrail implementations
│   ├── input_guardrails.py    # Input validation guardrails
│   └── output_guardrails.py   # Output validation guardrails
├── models/                    # Data models and schemas
│   ├── input_models.py        # Input data structures
│   └── output_models.py       # Output data structures
├── api/                       # API interface (optional)
│   ├── routes.py              # API endpoint definitions
│   └── server.py              # API server setup
├── config/                    # Configuration files
│   └── settings.py            # Application settings
├── utils/                     # Utility functions
│   └── helpers.py             # Helper utilities
├── main.py                    # Application entry point
├── requirements.txt           # Dependencies
└── README.md                  # Project documentation
```

## 4. Defining Basic Agents

### 4.1 Creating a Simple Agent
```python
from agents import Agent, Runner

# Create a simple agent with instructions
agent = Agent(
    name="Math Tutor",
    instructions="You are a helpful math tutor who explains concepts clearly and provides step-by-step solutions.",
    model="o3-mini",  # Optional: specify model
)

# Run the agent synchronously
result = Runner.run_sync(agent, "Can you explain how to solve quadratic equations?")
print(result.final_output)
```

### 4.2 Adding Structured Output
```python
from pydantic import BaseModel
from agents import Agent

# Define structured output model
class MathSolution(BaseModel):
    problem: str
    steps: list[str]
    answer: str
    explanation: str

# Create agent with structured output
solution_agent = Agent(
    name="Math Problem Solver",
    instructions="Solve math problems step by step and provide clear explanations.",
    output_type=MathSolution
)
```

## 5. Implementing Function Tools

### 5.1 Creating Basic Function Tools
```python
from agents import Agent, function_tool

# Define a function tool with type hints
@function_tool
def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle.
    
    Args:
        length: The length of the rectangle in meters.
        width: The width of the rectangle in meters.
        
    Returns:
        The area of the rectangle in square meters.
    """
    return length * width

# Create agent with tool
calculator_agent = Agent(
    name="Geometry Helper",
    instructions="Help users with geometry calculations.",
    tools=[calculate_area]
)
```

### 5.2 Using Context in Tools
```python
from typing import Any, Dict
from agents import Agent, function_tool, RunContextWrapper

# Define a tool that uses context
@function_tool
def get_user_preferences(ctx: RunContextWrapper[Dict[str, Any]], category: str) -> str:
    """Get user preferences for a specific category.
    
    Args:
        category: The preference category to retrieve.
    """
    user_prefs = ctx.context.get("user_preferences", {})
    return str(user_prefs.get(category, "No preference found"))

# Create context-aware agent
personalized_agent = Agent(
    name="Personalized Assistant",
    instructions="Provide personalized recommendations based on user preferences.",
    tools=[get_user_preferences]
)
```

### 5.3 Advanced Tool Configuration
```python
from typing import TypedDict
from agents import Agent, function_tool

# Define complex input type
class LocationData(TypedDict):
    city: str
    country: str
    coordinates: tuple[float, float]

@function_tool(name_override="fetch_weather_data")
def get_weather(location: LocationData) -> dict:
    """Get weather data for a specific location."""
    # Implementation
    return {"temperature": 72, "condition": "Sunny"}

# Create agent with advanced tool
weather_agent = Agent(
    name="Weather Assistant",
    instructions="Provide weather information and forecasts.",
    tools=[get_weather]
)
```

## 6. Multi-Agent Orchestration

### 6.1 Agent Handoffs
```python
from agents import Agent, Runner
import asyncio

# Create specialized agents
math_agent = Agent(
    name="Math Specialist",
    handoff_description="Expert in solving mathematical problems",
    instructions="Solve math problems with detailed explanations."
)

history_agent = Agent(
    name="History Specialist",
    handoff_description="Expert in historical information",
    instructions="Provide accurate historical information and context."
)

# Create main agent with handoffs
main_agent = Agent(
    name="Academic Assistant",
    instructions="""You help students with various subjects. 
    For math questions, hand off to the Math Specialist.
    For history questions, hand off to the History Specialist.""",
    handoffs=[math_agent, history_agent]
)

async def main():
    # The system will automatically handle handoffs to the appropriate specialist
    result = await Runner.run(main_agent, "What is the quadratic formula?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
```

### 6.2 Custom Handoff Behavior
```python
from agents import Agent, handoff, RunContextWrapper
from pydantic import BaseModel

# Define input structure for handoff
class EscalationInfo(BaseModel):
    reason: str
    priority: int

# Define handoff callback
async def on_escalation(ctx: RunContextWrapper[None], input_data: EscalationInfo):
    print(f"Escalation triggered: {input_data.reason} (Priority: {input_data.priority})")
    # Could log to database, notify support team, etc.

# Create support agent
support_agent = Agent(
    name="Support Specialist",
    instructions="Handle complex customer issues with care and attention to detail."
)

# Create main agent with custom handoff
customer_agent = Agent(
    name="Customer Service",
    instructions="""Help customers with basic inquiries.
    For complex issues, escalate to Support Specialist with reason and priority.""",
    handoffs=[
        handoff(
            agent=support_agent,
            on_handoff=on_escalation,
            input_type=EscalationInfo
        )
    ]
)
```

## 7. Implementing Guardrails

### 7.1 Input Guardrails
```python
from pydantic import BaseModel
from agents import (
    Agent, GuardrailFunctionOutput, RunContextWrapper,
    Runner, input_guardrail, InputGuardrailTripwireTriggered
)
import asyncio

# Define validation model
class ContentValidation(BaseModel):
    is_appropriate: bool
    reasoning: str

# Create validation agent
validation_agent = Agent(
    name="Content Validator",
    instructions="Determine if user input is appropriate and safe.",
    output_type=ContentValidation
)

# Define input guardrail
@input_guardrail
async def content_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, input: str
) -> GuardrailFunctionOutput:
    result = await Runner.run(validation_agent, input, context=ctx.context)
    output = result.final_output_as(ContentValidation)
    
    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=not output.is_appropriate
    )

# Create agent with guardrail
safe_agent = Agent(
    name="Safe Assistant",
    instructions="Provide helpful responses to appropriate requests.",
    input_guardrails=[content_guardrail]
)

async def main():
    try:
        result = await Runner.run(safe_agent, "Tell me about renewable energy.")
        print(result.final_output)
    except InputGuardrailTripwireTriggered as e:
        print(f"Input rejected: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 7.2 Output Guardrails
```python
from pydantic import BaseModel
from agents import (
    Agent, GuardrailFunctionOutput, RunContextWrapper,
    Runner, output_guardrail, OutputGuardrailTripwireTriggered
)

# Define output model and validation model
class ResponseOutput(BaseModel):
    content: str

class QualityCheck(BaseModel):
    meets_standards: bool
    reasoning: str

# Create quality checker agent
quality_agent = Agent(
    name="Quality Checker",
    instructions="Evaluate response quality for accuracy, helpfulness, and tone.",
    output_type=QualityCheck
)

# Define output guardrail
@output_guardrail
async def quality_guardrail(
    ctx: RunContextWrapper[None], agent: Agent, output: ResponseOutput
) -> GuardrailFunctionOutput:
    result = await Runner.run(quality_agent, output.content, context=ctx.context)
    check = result.final_output_as(QualityCheck)
    
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.meets_standards
    )

# Create agent with output guardrail
quality_assured_agent = Agent(
    name="Quality Assistant",
    instructions="Provide thoughtful, accurate responses.",
    output_type=ResponseOutput,
    output_guardrails=[quality_guardrail]
)
```

## 8. Integration with External Systems

### 8.1 FastAPI Integration
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from agents import Agent, Runner
import asyncio

# Create FastAPI app
app = FastAPI(title="Agent API")

# Define request/response models
class QueryRequest(BaseModel):
    query: str
    user_id: str

class QueryResponse(BaseModel):
    response: str

# Create agent
assistant_agent = Agent(
    name="API Assistant",
    instructions="Provide helpful responses to user queries via API."
)

# Define API endpoint
@app.post("/ask", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    try:
        # Create user-specific context
        context = {"user_id": request.user_id}
        
        # Run agent with query
        result = await Runner.run(
            assistant_agent, 
            request.query,
            context=context
        )
        
        return QueryResponse(response=result.final_output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 8.2 Streaming Responses
```python
from fastapi import FastAPI, WebSocket
from agents import Agent, Runner
import json

app = FastAPI()
agent = Agent(name="Chat Assistant", instructions="Engage in helpful conversation.")

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Stream agent response
            async for chunk in Runner.stream(agent, message["text"]):
                if chunk.content:
                    await websocket.send_text(json.dumps({
                        "type": "content",
                        "data": chunk.content
                    }))
            
            # Send completion message
            await websocket.send_text(json.dumps({
                "type": "complete",
                "data": ""
            }))
            
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "data": str(e)
        }))
    finally:
        await websocket.close()
```

## 9. Knowledge Integration

### 9.1 File Search Integration
```python
from agents import Agent, FileSearchTool

# Create an agent with file search capabilities
research_agent = Agent(
    name="Research Assistant",
    instructions="Help users find relevant information from documents.",
    tools=[
        FileSearchTool(
            # Connect to your vector store in OpenAI
            vector_store_ids=["your-vector-store-id"],
            max_num_results=5
        )
    ]
)
```

### 9.2 Web Search Integration
```python
from agents import Agent, WebSearchTool

# Create an agent with web search capabilities
web_agent = Agent(
    name="Web Researcher",
    instructions="Help users find current information from the web.",
    tools=[
        WebSearchTool()  # Uses BING search by default
    ]
)
```

## 10. Tracing and Monitoring

### 10.1 Basic Tracing
```python
from agents import Agent, Runner, trace
import asyncio

# Create agent
debug_agent = Agent(
    name="Debug Test Agent",
    instructions="Demonstrate tracing capabilities."
)

async def main():
    # Create a named trace
    with trace("Debugging Workflow"):
        # First agent call
        result1 = await Runner.run(debug_agent, "What is tracing?")
        
        # Second agent call in same trace
        result2 = await Runner.run(
            debug_agent, 
            f"Can you elaborate on: {result1.final_output[:50]}..."
        )
        
        print(f"First response: {result1.final_output}")
        print(f"Second response: {result2.final_output}")

if __name__ == "__main__":
    asyncio.run(main())
    
# View traces in OpenAI dashboard: https://platform.openai.com/traces
```

### 10.2 Custom Tracing
```python
from agents import (
    Agent, Runner, add_trace_processor, 
    TraceProcessor, Trace, Span
)

# Define custom trace processor
class CustomTraceProcessor(TraceProcessor):
    def process_trace(self, trace: Trace):
        print(f"Trace completed: {trace.workflow_name} ({trace.trace_id})")
        for span in trace.spans:
            print(f"  - Span: {span.name} ({span.duration_ms}ms)")
    
    def process_span(self, span: Span):
        print(f"Span created: {span.name}")

# Register custom trace processor
add_trace_processor(CustomTraceProcessor())

# Create and use agent as normal
agent = Agent(name="Monitored Agent", instructions="Test tracing functionality.")
```

## 11. Best Practices

### 11.1 Prompt Engineering
- Be specific and clear in agent instructions
- Structure prompts with examples when needed
- Define explicit boundaries and limitations
- Provide context about the agent's role and purpose

### 11.2 Tool Design
- Create specialized, single-purpose tools
- Use clear type hints and descriptive docstrings
- Handle errors gracefully within tools
- Return structured, consistent responses

### 11.3 Multi-Agent Architecture
- Break complex tasks into specialized agent roles
- Use handoffs for clear separation of concerns
- Implement proper guardrails for each agent
- Consider both LLM-driven and code-driven orchestration

### 11.4 Error Handling
```python
from agents import Agent, Runner, RunConfig
import asyncio

async def run_with_retry(agent, query, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            result = await Runner.run(
                agent, 
                query,
                config=RunConfig(
                    max_turns=5,  # Limit turns to prevent infinite loops
                    timeout_seconds=30  # Set timeout to prevent hanging
                )
            )
            return result
        except Exception as e:
            retries += 1
            print(f"Error occurred (attempt {retries}/{max_retries}): {e}")
            if retries >= max_retries:
                raise
            await asyncio.sleep(1)  # Wait before retry
```

## 12. Security and Compliance

### 12.1 Input Validation
- Implement guardrails for all user inputs
- Validate input formats, lengths, and content
- Use pattern matching for structured inputs
- Apply content moderation where appropriate

### 12.2 Data Privacy
- Use `trace_include_sensitive_data=False` to exclude sensitive data from traces
- Don't log personal or sensitive information
- Implement data minimization principles
- Consider encryption for sensitive context data

### 12.3 Rate Limiting
```python
import time
from functools import wraps

def rate_limit(max_calls, time_frame):
    """Simple rate limiting decorator"""
    calls = []
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_time = time.time()
            # Remove calls older than time_frame
            calls[:] = [call_time for call_time in calls if current_time - call_time <= time_frame]
            
            if len(calls) >= max_calls:
                raise Exception(f"Rate limit exceeded: {max_calls} calls per {time_frame} seconds")
            
            calls.append(current_time)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(max_calls=10, time_frame=60)
async def run_agent_with_limit(agent, query):
    return await Runner.run(agent, query)
```

## 13. References
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [OpenAI Platform Dashboard](https://platform.openai.com/)
- [GitHub Repository](https://github.com/openai/openai-agents-python)
- [Trace Viewer](https://platform.openai.com/traces)

---
> This guide covers the core aspects of implementing the OpenAI Agents SDK. For the most up-to-date information, always refer to the official documentation.
