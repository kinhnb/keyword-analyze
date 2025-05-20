class SerpKeywordAnalysisOrchestrator:
    """Orchestrates calls to individual SERP keyword analysis agents."""

    def __init__(self, serp_agent=None, intent_agent=None, market_gap_agent=None):
        """Store dependencies for later use.

        Parameters
        ----------
        serp_agent: callable, optional
            Async callable handling the raw SERP data.
        intent_agent: callable, optional
            Async callable providing intent analysis.
        market_gap_agent: callable, optional
            Async callable providing market gap analysis.
        """
        self.serp_agent = serp_agent
        self.intent_agent = intent_agent
        self.market_gap_agent = market_gap_agent

    async def analyze(self, search_term, serp_data, intent_analysis, market_gap):
        """Run each agent and return a dictionary with their results."""
        results = {"search_term": search_term}

        if self.serp_agent is not None:
            results["serp"] = await self.serp_agent(search_term, serp_data)

        if self.intent_agent is not None:
            results["intent"] = await self.intent_agent(search_term, intent_analysis)

        if self.market_gap_agent is not None:
            results["market_gap"] = await self.market_gap_agent(search_term, market_gap)

        return results
