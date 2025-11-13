from typing import List,Union,Dict,Any
from pydantic import BaseModel,Field
from pydantic_ai import Agent
from story_seq.pipeline.pipeline import PipelineOptions
from story_seq.config import StorySeqConfig
class PipelineState(BaseModel):
    """
        State of the pipeline
    """
    config: StorySeqConfig = Field(default_factory=None, exclude=True)
    options: PipelineOptions = Field(default_factory=PipelineOptions, exclude=True)
