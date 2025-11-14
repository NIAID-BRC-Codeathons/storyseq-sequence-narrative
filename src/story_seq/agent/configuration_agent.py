"""Configuration agent for managing story-seq settings."""

import json
from pathlib import Path
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Any, Dict, Optional, Union
from story_seq.config import StorySeqConfig
from story_seq.models import AnalysisConfig

class ConfigurationAgentDeps(BaseModel):
    """Dependencies for the Configuration Agent."""
    question: str = Field(default="", description="User's question guiding the analysis")
    query: Optional[Path] = Field(default=None, description="The input sequence query file path")
    fasta_sketch: Optional[Dict[str, Any]] = Field(default=None, description="FASTA file analysis information from process_multiple_files")


async def get_configuration_agent(
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    llm_api_url: Optional[str] = None,
    max_tokens: int = 2000,
) -> Agent[ConfigurationAgentDeps, AnalysisConfig]:
    """
    Create and configure the Configuration Agent.
    
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
    
    mcp_servers = []
    
    # Read instructions from static markdown file
    prompt_file = Path(__file__).parent / "static_configuration_agent_prompt.md"
    with open(prompt_file, 'r') as f:
        instructions = f.read()
  
    agent = Agent(
        model=llm_model,
        deps_type=ConfigurationAgentDeps,
        output_type=AnalysisConfig,
        system_prompt=instructions,
        retries=3,
        mcp_servers=mcp_servers,
        model_settings={'max_tokens': max_tokens}
    )
    
    
    @agent.instructions
    async def add_instructions(ctx: RunContext[ConfigurationAgentDeps]):
        """
        Generate instructions based on the known materials.
        """
        # Access fasta_sketch from ctx.prompt (the deps passed to run())
        if hasattr(ctx, 'prompt') and ctx.prompt and hasattr(ctx.prompt, 'fasta_sketch') and ctx.prompt.fasta_sketch:
            return f"Here is the FASTA sketch:\n{json.dumps(ctx.prompt.fasta_sketch, indent=4)}"
            
    return agent
