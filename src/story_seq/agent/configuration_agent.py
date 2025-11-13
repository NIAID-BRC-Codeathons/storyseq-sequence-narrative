"""Configuration agent for managing story-seq settings."""

from pathlib import Path
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Any, Dict, Optional, Union
from story_seq.config import StorySeqConfig
from story_seq.models import AnalysisConfig
from story_seq.util import process_multiple_files

class ConfigurationAgentDeps(BaseModel):
    """Dependencies for the Configuration Agent."""
    question: str = Field(default="", description="User's question guiding the analysis")
    query: Optional[Path] = Field(default=None, description="The input sequence query file path")
    sequence_type: str = Field(default="", description="Type of the sequence (e.g., DNA, protein)")


async def get_configuration_agent(
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    llm_api_url: Optional[str] = None,
) -> Agent[ConfigurationAgentDeps, AnalysisConfig]:
    """
    Create and configure the Configuration Agent.
    
    Args:
        llm_api_url: Base URL for the LLM API
        llm_api_key: API key for authentication
        model_name: Name of the LLM model to use

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
        mcp_servers=mcp_servers
    )
    
    
    @agent.instructions
    async def add_instructions(ctx: RunContext[ConfigurationAgentDeps]):
        """
        Generate instructions based on the known materials.
        """
        if ctx.deps.query:
            # call fasta sketch
            try:
                fasta_dictionary = process_multiple_files([ctx.deps.query])
                return json.dumps(dispatch_plan, indent=4)
            except Exception as e:
                ctx.deps.question = f"Error processing FASTA files: {e}"
                return ""
            
    return agent
