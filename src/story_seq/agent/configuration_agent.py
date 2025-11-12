"""Configuration agent for managing story-seq settings."""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Any, Dict, Optional
from story_seq.config import StorySeqConfig


class ConfigurationAgentDeps(BaseModel):
    """
    Dependencies for the Configuration Agent.
    """
    current_config: Optional[StorySeqConfig] = Field(
        default=None,
        description="Current configuration to validate or enhance"
    )


async def get_configuration_agent(
    llm_api_url: str,
    llm_api_key: str,
    model_name: str = "gpt-4",
    mcp_servers: Optional[list] = None
) -> Agent:
    """
    Create and configure the Configuration Agent.
    
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
You are a configuration management agent for the story-seq sequence narrative analysis pipeline.
Your role is to help validate, optimize, and suggest configuration parameters.

You should:
- Validate configuration parameters for correctness and compatibility
- Suggest optimal settings based on the analysis context
- Identify potential configuration issues or conflicts
- Recommend best practices for BLAST and LLM settings

Provide clear, actionable recommendations for configuration improvements.
"""
    
    agent = Agent(
        model=llm_model,
        output_type=Dict[str, Any],
        deps_type=ConfigurationAgentDeps,
        instructions=instructions,
        retries=3,
        mcp_servers=mcp_servers
    )
    
    @agent.instructions
    async def current_config_instructions(ctx: RunContext[ConfigurationAgentDeps]) -> str:
        """
        Generate instructions based on current configuration.
        """
        if ctx.deps.current_config is None:
            return "No current configuration provided."
        
        return f"""
Current Configuration:
- LLM Model: {ctx.deps.current_config.llm_model}
- BLAST E-value: {ctx.deps.current_config.blast_evalue}
- Max Tokens: {ctx.deps.current_config.max_tokens}
"""
    
    return agent
