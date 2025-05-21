# keyword-analyze

This package contains a minimal framework for analyzing search engine results
pages (SERPs). The `SerpKeywordAnalysisOrchestrator` coordinates multiple
agent functions that process different aspects of the SERP data.

## Example Usage

```python
import asyncio
from ai_serp_keyword_research.orchestration.multi_agent_orchestrator import (
    SerpKeywordAnalysisOrchestrator,
)
from ai_serp_keyword_research.agents.basic_agents import (
    serp_agent,
    intent_agent,
    market_gap_agent,
)

async def main():
    orchestrator = SerpKeywordAnalysisOrchestrator(
        serp_agent=serp_agent,
        intent_agent=intent_agent,
        market_gap_agent=market_gap_agent,
    )

    results = await orchestrator.analyze(
        "python async",
        serp_data={"results": []},
        intent_analysis={"intent": "learning"},
        market_gap={"gap": "tutorials"},
    )
    print(results)

asyncio.run(main())
```
