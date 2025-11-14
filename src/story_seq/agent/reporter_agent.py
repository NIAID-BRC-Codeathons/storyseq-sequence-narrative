"""Reporter agent for generating narrative reports."""

import json
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
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
    provider = OpenAIProvider(base_url=llm_api_url, api_key=llm_api_key)
    llm_model = OpenAIModel(model_name, provider=provider)
    
    mcp_servers = []
    
    instructions = """
You are a reporter agent for the story-seq sequence analysis pipeline.
Generate comprehensive, narrative-style reports from BLAST results and enriched sequence data.

Your tasks:
1. Synthesize information from BLAST results and enriched data
2. Generate a structured narrative that explains the details based on the AnalysisConfig
   - Sequence identity and similarity
   - Taxonomic classification
   - Functional annotations
   - Evolutionary relationships
3. Address specific questions posed by the user
4. Provide clear, scientifically accurate interpretations

Use the provided data to create an informative, accessible report for researchers.
"""
    
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
        context = f"Generating narrative for {len(ctx.deps.blast_results)} BLAST results.\n"
        
        if ctx.deps.analysis_config:
            context += f"\nUsing Analysis Configuration:\n{ctx.deps.analysis_config.model_dump_json(indent=4)}\n"  
        if ctx.deps.question:
            context += f"\nUser Question: {ctx.deps.question}\n"
            context += "Focus the narrative on answering this specific question.\n"
        
        if ctx.deps.blast_results:
            context += f"\nBLAST results are available for analysis.\n{json.dumps([br.model_dump() for br in ctx.deps.blast_results], indent=4)}\n    "

        return context
    
    return agent
