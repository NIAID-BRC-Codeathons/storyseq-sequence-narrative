from pydantic import BaseModel, Field
from story_seq.config import StorySeqConfig
from pydantic_graph import BaseNode,End,GraphRunContext,Graph
from story_seq.pipeline.tasks import call_config_agent,get_fasta_sketch,call_blast_agent,call_reporter_agent
from story_seq.pipeline.state import PipelineState, PipelineOptions
from pathlib import Path
from typing import Optional
import json

ResearchTaskGraph = Graph(nodes=[get_fasta_sketch,call_config_agent,call_blast_agent,call_reporter_agent])
 
    
def run_pipeline(options: PipelineOptions, state_file: Optional[Path] = None, start_task: Optional[str] = None) -> None:
    """Run the sequence analysis pipeline with the given options.
    
    Args:
        options: Pipeline configuration options
        state_file: Optional path to save/load pipeline state
        start_task: Optional task name to start from (if state_file exists)
    """
    print(f"Running pipeline with query: {options.query}")
    print(f"Question: {options.question}")
    print(f"LLM Model: {options.config.llm_model}")
    print(f"LLM API URL: {options.config.llm_api_url}")
    
    # Initialize or load the pipeline state
    if state_file and state_file.exists() and start_task:
        print(f"Loading state from {state_file}")
        with open(state_file, 'r') as f:
            state_data = json.load(f)
            # Create state without options field from file, then set it
            state = PipelineState(options=options, **state_data)
    else:
        state = PipelineState(options=options)
    
    # Store state_file path in state for tasks to use
    if state_file:
        state.state_file_path = str(state_file)
    
    # Determine starting task
    task_map = {
        "get_fasta_sketch": get_fasta_sketch,
        "call_config_agent": call_config_agent,
        "call_blast_agent": call_blast_agent,
        "call_reporter_agent": call_reporter_agent,
    }
    
    if start_task and start_task in task_map:
        start_node = task_map[start_task]()
        print(f"Starting from task: {start_task}")
    else:
        start_node = get_fasta_sketch()
        print("Starting from beginning: get_fasta_sketch")
    
    # Run the graph
    import asyncio
    result = asyncio.run(ResearchTaskGraph.run(start_node, state=state))
    
    print("\nPipeline execution completed!")
    print(f"\n{result.output.narrative}")
    
    
    