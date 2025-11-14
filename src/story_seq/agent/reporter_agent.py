"""Reporter agent for generating narrative reports."""

import json
from pathlib import Path
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio
import sys

from typing import Any, Dict, List, Optional
from story_seq.models import SequenceNarrative, BlastResult
from story_seq.models import AnalysisConfig

class ReporterAgentDeps(BaseModel):
    """
    Dependencies for the Reporter Agent.
    """
    blast_results: List[BlastResult] = Field(
        default_factory=list,
        description="BLAST results to generate narrative from"
    )
    analysis_config: AnalysisConfig = Field(default=None, description="Analysis configuration from configuration agent" )
    question: Optional[str] = Field(
        default=None,
        description="Specific question to address in the narrative"
    )


async def get_reporter_agent(
    llm_api_url: Optional[str],
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    max_tokens: int = 2000
) -> Agent:
    """
    Create and configure the Reporter Agent.
    
    Args:
        llm_api_url: Base URL for the LLM API
        llm_api_key: API key for authentication
        model_name: Name of the LLM model to use
        max_tokens: Maximum tokens for AI responses
        
    Returns:
        Configured Agent instance
    """
    # Only pass api_key if it's not empty
    provider_kwargs = {"base_url": llm_api_url}
    if llm_api_key:
        provider_kwargs["api_key"] = llm_api_key
    provider = OpenAIProvider(**provider_kwargs)
    llm_model = OpenAIModel(model_name, provider=provider)
    
    mcp_servers = [
        MCPServerStdio(sys.executable, ['-m', 'paper_search_mcp.server'])
    ]
    
    # Read instructions from static markdown file
    prompt_file = Path(__file__).parent / "static_reporter_agent_prompt.md"
    with open(prompt_file, 'r') as f:
        instructions = f.read()
    
    agent = Agent(
        model=llm_model,
        output_type=str,
        deps_type=ReporterAgentDeps,
        instructions=instructions,
        retries=3,
        mcp_servers=mcp_servers,
        model_settings={'max_tokens': max_tokens}
    )
    
    @agent.instructions
    async def narrative_context_instructions(ctx: RunContext[ReporterAgentDeps]) -> str:
        """
        Generate instructions based on available data and user question.
        """
        context = f"Generate narrative for {len(ctx.deps.blast_results)} BLAST results.\n"
        
        if ctx.deps.analysis_config:
            context += f"\nUsing Analysis Configuration:\n{ctx.deps.analysis_config.model_dump_json(indent=4)}\n"  
        if ctx.deps.question:
            context += f"\nUser Question: {ctx.deps.question}\n"
            context += "Focus the narrative on answering this specific question.\n"
        
        if ctx.deps.blast_results:
            context += f"\nBLAST results are available for analysis.\n{json.dumps([br.model_dump() for br in ctx.deps.blast_results], indent=4)}\n    "

        return context
    
    return agent
