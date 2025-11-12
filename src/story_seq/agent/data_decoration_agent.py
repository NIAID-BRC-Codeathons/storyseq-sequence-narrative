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
    llm_api_url: str,
    llm_api_key: str,
    model_name: str = "gpt-4",
    mcp_servers: Optional[list] = None
) -> Agent:
    """
    Create and configure the Data Decoration Agent.
    
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
You are a data decoration agent specialized in enriching biological sequence information.
Your role is to:

- Add contextual information to BLAST results
- Retrieve and integrate taxonomic classifications
- Fetch functional annotations and gene ontology terms
- Include pathway and domain information
- Add literature references and known associations
- Provide biological context for sequence matches

You should:
- Use authoritative databases (UniProt, GenBank, PDB, etc.)
- Ensure accuracy of annotations
- Link sequences to biological processes and functions
- Identify relevant structural and functional domains
- Note any clinical or research significance

Return enriched data with comprehensive, scientifically accurate annotations.
"""
    
    agent = Agent(
        model=llm_model,
        output_type=Dict[str, Any],
        deps_type=DataDecorationAgentDeps,
        instructions=instructions,
        retries=3,
        mcp_servers=mcp_servers
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
