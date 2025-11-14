"""Data decoration agent for enriching sequence information."""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Any, Dict, List, Optional
from story_seq.models import BlastResult


class DataDecorationAgentDeps(BaseModel):
    """
    Dependencies for the Data Decoration Agent.
    """
    blast_results: List[BlastResult] = Field(
        default_factory=list,
        description="BLAST results to enrich with additional information"
    )
    include_taxonomy: bool = Field(
        default=True,
        description="Whether to include taxonomic information"
    )
    include_functional: bool = Field(
        default=True,
        description="Whether to include functional annotations"
    )


async def get_data_decoration_agent(
    llm_api_url: Optional[str],
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    max_tokens: int = 2000,
    mcp_servers: Optional[list] = None
) -> Agent:
    """
    Create and configure the Data Decoration Agent.
    
    Args:
        llm_api_url: Base URL for the LLM API
        llm_api_key: API key for authentication
        model_name: Name of the LLM model to use
        max_tokens: Maximum tokens for AI responses
        mcp_servers: Optional list of MCP servers
        
    Returns:
        Configured Agent instance
    """
    # Only pass api_key if it's not empty
    provider_kwargs = {"base_url": llm_api_url}
    if llm_api_key:
        provider_kwargs["api_key"] = llm_api_key
    provider = OpenAIProvider(**provider_kwargs)
    llm_model = OpenAIModel(model_name, provider=provider)
    
    if mcp_servers is None:
        mcp_servers = []
    
    instructions = """
You are a data decoration agent for the story-seq sequence analysis pipeline.
Enrich BLAST results with additional taxonomic and functional annotations.

Your tasks:
1. Extract key information from BLAST results
2. Retrieve taxonomic lineages for matched sequences
3. Add functional annotations from databases
4. Organize and structure enriched data
5. Provide comprehensive metadata for downstream analysis

Use external APIs and databases to enhance the analytical value of BLAST results.
"""
    
    agent = Agent(
        model=llm_model,
        output_type=Dict[str, Any],
        deps_type=DataDecorationAgentDeps,
        instructions=instructions,
        retries=3,
        mcp_servers=mcp_servers,
        model_settings={'max_tokens': max_tokens}
    )
    
    @agent.instructions
    async def decoration_context_instructions(ctx: RunContext[DataDecorationAgentDeps]) -> str:
        """
        Generate instructions based on decoration parameters.
        """
        context = f"Processing {len(ctx.deps.blast_results)} BLAST results for enrichment.\n"
        
        enrichment_types = []
        if ctx.deps.include_taxonomy:
            enrichment_types.append("taxonomic information")
        if ctx.deps.include_functional:
            enrichment_types.append("functional annotations")
        
        if enrichment_types:
            context += f"Include: {', '.join(enrichment_types)}"
        
        return context
    
    return agent
