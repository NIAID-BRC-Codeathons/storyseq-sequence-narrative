"""Validation agent for quality control."""

from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from typing import Any, Dict, List, Optional
from pathlib import Path
from story_seq.models import BlastResult


class ValidationAgentDeps(BaseModel):
    """
    Dependencies for the Validation Agent.
    """
    fasta_file: Optional[Path] = Field(
        default=None,
        description="FASTA file to validate"
    )
    blast_results: Optional[List[BlastResult]] = Field(
        default=None,
        description="BLAST results to validate"
    )
    narrative: Optional[str] = Field(
        default=None,
        description="Generated narrative to validate"
    )
    strict_mode: bool = Field(
        default=False,
        description="Whether to apply strict validation rules"
    )


async def get_validation_agent(
    llm_api_url: Optional[str],
    llm_api_key: Optional[str],
    model_name: str = "gpt-4",
    mcp_servers: Optional[list] = None
) -> Agent:
    """
    Create and configure the Validation Agent.
    
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
You are a quality control and validation agent for sequence analysis pipelines.
Your role is to:

- Validate FASTA file format and sequence content
- Check BLAST results for quality and completeness
- Verify the accuracy of generated narratives
- Identify potential errors or inconsistencies
- Assess the reliability of findings
- Flag suspicious or low-quality results
- Verify that claims are supported by data

Your validation should check for:
- Format compliance (FASTA, BLAST output formats)
- Sequence quality (length, composition, validity)
- Result significance (E-values, coverage, identity)
- Narrative accuracy (citations, claims, conclusions)
- Consistency across data sources
- Scientific correctness

Return detailed validation reports with:
- Overall validity status
- Specific errors and warnings
- Quality scores where applicable
- Recommendations for improvements
"""
    
    agent = Agent(
        model=llm_model,
        output_type=Dict[str, Any],
        deps_type=ValidationAgentDeps,
        instructions=instructions,
        retries=3,
        mcp_servers=mcp_servers
    )
    
    @agent.instructions
    async def validation_context_instructions(ctx: RunContext[ValidationAgentDeps]) -> str:
        """
        Generate instructions based on what needs validation.
        """
        context = "Validation Tasks:\n"
        
        if ctx.deps.fasta_file:
            context += f"- Validate FASTA file: {ctx.deps.fasta_file}\n"
        
        if ctx.deps.blast_results:
            context += f"- Validate {len(ctx.deps.blast_results)} BLAST results\n"
        
        if ctx.deps.narrative:
            context += "- Validate generated narrative\n"
        
        if ctx.deps.strict_mode:
            context += "\nStrict validation mode enabled - apply rigorous quality standards.\n"
        else:
            context += "\nStandard validation mode - flag only critical issues.\n"
        
        return context
    
    return agent
