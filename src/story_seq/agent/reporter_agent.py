"""Reporter agent for generating narrative reports."""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Any, Dict, List, Optional
from story_seq.models import SequenceNarrative, BlastResult


class ReporterAgentDeps(BaseModel):
    """
    Dependencies for the Reporter Agent.
    """
    blast_results: List[BlastResult] = Field(
        default_factory=list,
        description="BLAST results to generate narrative from"
    )
    enriched_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Enriched data from decoration agent"
    )
    question: Optional[str] = Field(
        default=None,
        description="Specific question to address in the narrative"
    )


async def get_reporter_agent(
    llm_api_url: Optional[str],
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    mcp_servers: Optional[list] = None
) -> Agent:
    """
    Create and configure the Reporter Agent.
    
    Args:
        llm_api_url: Base URL for the LLM API
        llm_api_key: API key for authentication
        model_name: Name of the LLM model to use
        mcp_servers: Optional list of MCP servers
        
    Returns:
        Configured Agent instance
    """
    provider = OpenAIProvider(base_url=llm_api_url, api_key=llm_api_key)
    llm_model = OpenAIModel(model_name, provider=provider)
    
    if mcp_servers is None:
        mcp_servers = []
    
    instructions = """
You are a scientific narrative generation agent specialized in sequence analysis reporting.
Your role is to:

- Generate clear, comprehensive narratives from BLAST results
- Synthesize information from multiple data sources
- Answer specific scientific questions about sequences
- Provide context and biological significance
- Create executive summaries of findings
- Highlight key matches and their implications

Your narratives should:
- Be scientifically accurate and well-cited
- Use appropriate technical terminology
- Explain findings in accessible language
- Highlight the most significant results
- Connect results to broader biological context
- Address pathogen identification and AMR gene discovery when relevant
- Provide confidence assessments for conclusions

Generate narratives that are informative, accurate, and actionable for researchers.
"""
    
    agent = Agent(
        model=llm_model,
        output_type=SequenceNarrative,
        deps_type=ReporterAgentDeps,
        instructions=instructions,
        retries=3,
        mcp_servers=mcp_servers
    )
    
    @agent.instructions
    async def narrative_context_instructions(ctx: RunContext[ReporterAgentDeps]) -> str:
        """
        Generate instructions based on available data and user question.
        """
        context = f"Generating narrative for {len(ctx.deps.blast_results)} BLAST results.\n"
        
        if ctx.deps.question:
            context += f"\nUser Question: {ctx.deps.question}\n"
            context += "Focus the narrative on answering this specific question.\n"
        
        if ctx.deps.enriched_data:
            context += "\nEnriched data is available with additional annotations.\n"
        
        return context
    
    return agent
