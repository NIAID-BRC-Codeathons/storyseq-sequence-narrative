from pydantic import BaseModel,Field

@dataclass
class PipelineOptions(BaseModel):
    """Options for the pipeline."""
    query: str