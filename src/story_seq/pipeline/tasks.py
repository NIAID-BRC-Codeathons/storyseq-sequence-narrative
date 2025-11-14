from pydantic_graph import BaseNode,End,GraphRunContext,Edge
from typing import List,Dict,Any,Union,Annotated,TYPE_CHECKING
from dataclasses import dataclass,field
from pydantic_ai.usage import UsageLimits
from pydantic_ai import UsageLimitExceeded,Agent
from story_seq.util import process_multiple_files
from story_seq.pipeline.state import PipelineState

if TYPE_CHECKING:
    from typing import TypeAlias


@dataclass
class get_fasta_sketch(BaseNode[PipelineState]):
    """Process FASTA file(s) to generate sketch information."""
    async def run(self, ctx: GraphRunContext) -> Union['call_config_agent', End]:
        print("[get_fasta_sketch] start")
        opts = ctx.state.options
        
        # Get the query file path from options
        query_files = [opts.query]
        
        # Process the FASTA file(s) to get sketch information
        fasta_sketch = process_multiple_files(query_files)
        
        # Store the fasta_sketch in the state
        ctx.state.fasta_sketch = fasta_sketch
        
        print(f"[get_fasta_sketch] Processed {len(query_files)} file(s)")
        print(f"[get_fasta_sketch] Sketch: {fasta_sketch}")
        
        # Save state if state file is configured
        ctx.state.save_to_file("get_fasta_sketch")
        
        return call_config_agent()

@dataclass
class call_config_agent(BaseNode[PipelineState]):   
    """Call the Configuration Agent to determine analysis configuration."""
    async def run(self, ctx: GraphRunContext) -> "call_blast_agent":
        print("[call_config_agent] start")
        opts = ctx.state.options
        
        # build the dependencies for the configuration agent and then call it
        from story_seq.agent.configuration_agent import get_configuration_agent,ConfigurationAgentDeps
        from story_seq.models import AnalysisConfig

        deps = ConfigurationAgentDeps(
            fasta_sketch=ctx.state.fasta_sketch,
            query=opts.query,
            question=opts.question
        )

        config_agent = await get_configuration_agent(
            llm_api_url=opts.config.llm_api_url,
            llm_api_key=opts.config.llm_api_key,
            model_name=opts.config.llm_model,
            max_tokens=opts.config.max_tokens
        )
        # Pass the user question as message and deps as separate parameter
        result = await config_agent.run(opts.question, deps=deps)
        ctx.state.analysis_config = result.output
        
        # Save state if state file is configured
        ctx.state.save_to_file("call_config_agent")
        
        return call_blast_agent()
    
    #add a task to call the blast agent
@dataclass
class call_blast_agent(BaseNode[PipelineState]):    
    """Call the BLAST Agent to perform sequence alignment."""
    async def run(self, ctx: GraphRunContext) -> "call_reporter_agent":
        print("[call_blast_agent] start")
        opts = ctx.state.options
        
        # build the dependencies for the BLAST agent and then call it
        from story_seq.agent.blast_agent import get_blast_agent,BlastAgentDeps
        from story_seq.models import BlastResult
        from pathlib import Path

        deps = BlastAgentDeps(
            query_file=Path(opts.query),
            database="nt",  # Default to NCBI nt database for now
            fasta_sketch=ctx.state.fasta_sketch,
            analysis_config=ctx.state.analysis_config
        )

        blast_agent = await get_blast_agent(
            llm_api_url=opts.config.llm_api_url,
            llm_api_key=opts.config.llm_api_key,
            model_name=opts.config.llm_model,
            max_tokens=opts.config.max_tokens
        )
        # Pass the user question as message and deps as separate parameter
        result = await blast_agent.run(opts.question, deps=deps)
        ctx.state.blast_results = result.output
        
        # Save state if state file is configured
        ctx.state.save_to_file("call_blast_agent")
        
        return call_reporter_agent()

@dataclass
class call_reporter_agent(BaseNode[PipelineState]):
    """Call the Reporter Agent to generate narrative report."""
    async def run(self, ctx: GraphRunContext) -> End:
        print("[call_reporter_agent] start")
        opts = ctx.state.options
        
        # build the dependencies for the reporter agent and then call it
        from story_seq.agent.reporter_agent import get_reporter_agent, ReporterAgentDeps
        from story_seq.models import SequenceNarrative

        deps = ReporterAgentDeps(
            blast_results=ctx.state.blast_results if ctx.state.blast_results else [],
            analysis_config=ctx.state.analysis_config,
            question=opts.question
        )

        reporter_agent = await get_reporter_agent(
            llm_api_url=opts.config.llm_api_url,
            llm_api_key=opts.config.llm_api_key,
            model_name=opts.config.llm_model,
            max_tokens=opts.config.max_tokens
        )
        # Pass the user question as message and deps as separate parameter
        result = await reporter_agent.run(opts.question, deps=deps)
        ctx.state.narrative = result.output
        
        # Save state if state file is configured
        ctx.state.save_to_file("call_reporter_agent")
        
        return End(data=ctx.state)