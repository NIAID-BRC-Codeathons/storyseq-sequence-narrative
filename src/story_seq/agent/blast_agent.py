"""BLAST agent for sequence analysis."""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Any, Dict, List, Optional
from pathlib import Path
from story_seq.models import BlastResult


class BlastAgentDeps(BaseModel):
    """
    Dependencies for the BLAST Agent.
    """
    query_file: Path = Field(description="Path to the query FASTA file")
    database: str = Field(description="BLAST database name or path")
    evalue: float = Field(default=0.001, description="E-value threshold")
    existing_results: Optional[List[BlastResult]] = Field(
        default=None,
        description="Previously obtained BLAST results"
    )


async def get_blast_agent(
    llm_api_url: Optional[str],
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    mcp_servers: Optional[list] = None
) -> Agent:
    """
    Create and configure the BLAST Agent.
    
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
You are a BLAST analysis agent specialized in sequence similarity searches.
Your role is to:

- Execute BLAST searches against specified databases
- Parse and interpret BLAST output
- Filter and rank results based on biological significance
- Identify the most relevant sequence matches
- Provide context about the quality and reliability of matches

You should focus on:
- E-value significance thresholds
- Percent identity and coverage metrics
- Alignment quality assessment
- Taxonomic and functional relevance of hits

Provide clear, scientifically accurate interpretations of BLAST results.
"""
    
    agent = Agent(
        model=llm_model,
        output_type=List[BlastResult],
        deps_type=BlastAgentDeps,
        instructions=instructions,
        retries=3,
        mcp_servers=mcp_servers
    )
    
    @agent.instructions
    async def blast_context_instructions(ctx: RunContext[BlastAgentDeps]) -> str:
        """
        Generate instructions based on BLAST parameters and existing results.
        """
        context = f"""
BLAST Search Parameters:
- Query File: {ctx.deps.query_file}
- Database: {ctx.deps.database}
- E-value Threshold: {ctx.deps.evalue}
"""
        
        if ctx.deps.existing_results and len(ctx.deps.existing_results) > 0:
            context += f"\nPrevious BLAST search returned {len(ctx.deps.existing_results)} results."
        
        return context
    
    return agent
