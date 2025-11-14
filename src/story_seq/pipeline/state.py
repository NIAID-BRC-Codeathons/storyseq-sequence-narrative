from typing import List,Union,Dict,Any,Optional
from pydantic import BaseModel,Field
from pydantic_ai import Agent
from story_seq.config import StorySeqConfig
from story_seq.models import AnalysisConfig, BlastResult, SequenceNarrative
import json
from pathlib import Path

class PipelineOptions(BaseModel):
    """Options for the pipeline."""
    config: StorySeqConfig = Field(default_factory=StorySeqConfig)
    query: str
    question: str

class PipelineState(BaseModel):
    """
        State of the pipeline
    """
    options: PipelineOptions = Field(default_factory=PipelineOptions, exclude=True)
    fasta_sketch: Optional[Dict[str, Any]] = Field(default=None, description="FASTA file sketch information")
    analysis_config: Union[None,AnalysisConfig] = Field(default=None, description="Analysis configuration determined by the configuration agent")   
    blast_results: Optional[BlastResult] = Field(default=None, description="BLAST results from the BLAST agent")
    narrative: Union[None, str, SequenceNarrative] = Field(default=None, description="Narrative report from the reporter agent")
    state_file_path: Optional[str] = Field(default=None, exclude=True, description="Path to state file for persistence")
    
    def save_to_file(self, task_name: str) -> None:
        """Save current state to file if state_file_path is set."""
        if self.state_file_path:
            state_path = Path(self.state_file_path)
            # Create parent directories if needed
            state_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(state_path, 'w') as f:
                json.dump(self.model_dump(mode='json'), f, indent=2)
            print(f"[{task_name}] State saved to {self.state_file_path}")
    
    
