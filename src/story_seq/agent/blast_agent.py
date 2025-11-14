"""BLAST agent for sequence analysis."""

import os
import sys
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai import ModelSettings

from pydantic_ai.mcp import MCPServerStdio
from typing import Any, Dict, List, Optional
from pathlib import Path
from story_seq.models import BlastResult, AnalysisConfig


class BlastAgentDeps(BaseModel):
    """
    Dependencies for the BLAST Agent.
    """
    query_file: Path = Field(description="Path to the query FASTA file")
    database: str = Field(description="BLAST database name or path")
    fasta_sketch: Optional[Dict[str, Any]] = Field(default=None, description="FASTA file analysis information from process_multiple_files")
    analysis_config: Optional[AnalysisConfig] = Field(default=None, description="Analysis configuration from configuration agent")


async def get_blast_agent(
    llm_api_url: Optional[str],
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    max_tokens: int = 2000,
) -> Agent:
    """
    Create and configure the BLAST Agent.
    
    Args:
        llm_api_url: Base URL for the LLM API
        llm_api_key: API key for authentication
        model_name: Name of the LLM model to use
        max_tokens: Maximum tokens for AI responses
        
    Returns:
        Configured Agent instance
    """
    provider = OpenAIProvider(base_url=llm_api_url, api_key=llm_api_key)
    llm_model = OpenAIModel(model_name, provider=provider)
    
    # Define the MCP server for NCBI BLAST functionality
    # Use sys.executable with -m for portable invocation across different Python environments
    # Set NCBI_EMAIL environment variable (required by ncbi-mcp-server)
    # NCBI_API_KEY is optional but recommended for higher rate limits
    if 'NCBI_EMAIL' not in os.environ:
        os.environ['NCBI_EMAIL'] = 'user@example.com'  # Default fallback
    
    mcp_servers = [
        MCPServerStdio(sys.executable, ['-m', 'ncbi_mcp_server.server'],
                       timeout=30.0,        # wait up to 30s for the server to start
                       read_timeout=900.0,  # allow up to 15 minutes of inactivity while a tool runs
                       max_retries=1)
    ]
    
    instructions = """
You are a BLAST analysis agent specialized in sequence similarity searches.
Your role is to:

- Execute BLAST searches against specified databases
- Limit result to the top 100 hits
- return the blast output as a BlastResult dictionary


You should focus on:
- E-value significance thresholds
- Percent identity and coverage metrics
- Alignment quality assessment
- Taxonomic and functional relevance of hits

Output JSON formatted BlastResult data structure
"""
    
    agent = Agent(
        model=llm_model,
        output_type=BlastResult,  # NCBI MCP server returns JSON string results
        deps_type=BlastAgentDeps,
        system_prompt=instructions,
        retries=3,
        mcp_servers=mcp_servers,
        model_settings={'max_tokens': max_tokens}
    )
    
    @agent.instructions
    async def blast_context_instructions(ctx: RunContext[BlastAgentDeps]) -> str:
        """
        Generate instructions based on BLAST parameters and existing results.
        """
        # Read the query file contents
        
        #TODO: look at ctx.deps.fasta_sketch for additional info to add to the context
        
        query_file_path = ctx.deps.query_file
        with open(query_file_path, 'r') as f:
            query_sequences = f.read()
        
        context = f"""
BLAST Search Parameters:

Query Sequences:
{query_sequences}
"""
        return context
    
    return agent
