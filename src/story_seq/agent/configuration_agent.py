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
    sequence_type: str = Field(default="", description="Type of the sequence (e.g., DNA, protein)")
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
    provider = OpenAIProvider(base_url=llm_api_url, api_key=llm_api_key)
    llm_model = OpenAIModel(model_name, provider=provider)
    
    mcp_servers = []
    
    instructions = """
You are a configuration agent for the story-seq sequence analysis pipeline.
Based on the input question, sequence type, and query characteristics, determine the appropriate analysis configuration.
Output an AnalysisConfig object with boolean fields indicating which analyses to perform.

Use the context from the dependencies to understand:
- The user's question/intent
- The query file being analyzed
- The type of sequences involved
"""
  
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
            return f"Include this JSON information about the fasta file(s) in the AnalysisConfig {json.dumps(ctx.prompt.fasta_sketch, indent=4)}"
            
    return agent
