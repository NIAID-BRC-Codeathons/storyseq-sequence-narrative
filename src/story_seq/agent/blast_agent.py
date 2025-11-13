"""BLAST agent for sequence analysis."""

import os
import sys
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio
from typing import Any, Dict, List, Optional
from pathlib import Path
from story_seq.models import BlastResult


class BlastAgentDeps(BaseModel):
    """
    Dependencies for the BLAST Agent.
    """
    query_file: Path = Field(description="Path to the query FASTA file")
    database: str = Field(description="BLAST database name or path")


async def get_blast_agent(
    llm_api_url: Optional[str],
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
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
    
    # Define the MCP server for NCBI BLAST functionality
    # Use sys.executable with -m for portable invocation across different Python environments
    # Set NCBI_EMAIL environment variable (required by ncbi-mcp-server)
    # NCBI_API_KEY is optional but recommended for higher rate limits
    if 'NCBI_EMAIL' not in os.environ:
        os.environ['NCBI_EMAIL'] = 'user@example.com'  # Default fallback
    
    mcp_servers = [
        MCPServerStdio(sys.executable, ['-m', 'ncbi_mcp_server.server'])
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

Use the JSON list of raw BLAST hits as input to this three-step workflow:

**Step 1: Collect All Unique Subject IDs**
- First, iterate through the entire list of input BLAST hits and collect all unique `subject_id` values.

**Step 2: Perform Batched Metadata Retrieval**
- Use the complete, unique list of subject IDs to perform the batch tool calls to make the MINIMUM number of required API calls.

- **For Core Record Info (GenBank Summary):** 
  - **Make a SINGLE batch call to the `efetch` tool with all IDs to retrieve the full GenBank records (`rettype=gb`).**
  - From these full records, extract the definition line, organism, and full taxonomy for each subject ID.

- **For Linked Info (BioProject & BioSample):**
  - Perform the two-step 'elink then esummary' process for the entire batch of IDs.
  - First, use `elink` to find all linked BioProject UIDs. Then use `esummary` on those UIDs to get the project titles.
  - Repeat this entire process for BioSample to get the sample attributes.
  - If there are no linked BioProject or BioSample records from the elink don't issue the followup esummary query.

**Step 3: Assemble the Final Enriched Output**
- After all data has been retrieved, map the enriched metadata back to the corresponding original BLAST hits.
- Your final output MUST be a JSON list of fully decorated objects, with the `genbank_summary`, `bioproject_info`, and `biosample_info` fields correctly populated for each hit.
"""
    
    agent = Agent(
        model=llm_model,
        output_type=BlastResult,  # NCBI MCP server returns JSON string results
        deps_type=BlastAgentDeps,
        system_prompt=instructions,
        retries=3,
        mcp_servers=mcp_servers
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
