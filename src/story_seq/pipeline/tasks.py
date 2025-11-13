from pydantic_graph import BaseNode,End,GraphRunContext,Edge
from typing import List,Dict,Any,Union,Annotated
from dataclasses import dataclass,field
from pydantic_ai.usage import UsageLimits
from pydantic_ai import UsageLimitExceeded,Agent


@dataclass
class generate_research_material(BaseNode[PipelineState]):
    """Generate Basic Research Materials based on the research configuration and options."""
    async def run(self, ctx: GraphRunContext) -> Annotated[End, Edge(label="solo")] | 'review_materials' | Annotated['generate_material_processes',Edge(label="skip material generation")]:
        print("[generate_research_material] start")
        opts = ctx.state.options