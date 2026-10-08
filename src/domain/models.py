from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ConceptRelationType(str, Enum):
    TEACHES = "TEACHES"
    REQUIRES = "REQUIRES"
    PREREQUISITE_OF = "PREREQUISITE_OF"


class VideoSegment(BaseModel):
    segment_id: str
    video_id: Optional[str] = None
    start_time: int = Field(ge=0, description="Start timestamp in seconds")
    end_time: int = Field(ge=0, description="End timestamp in seconds")
    transcript_text: str = ""
    concepts_taught: List[str] = Field(default_factory=list)
    concepts_required: List[str] = Field(default_factory=list)

    @property
    def duration(self) -> int:
        return max(0, self.end_time - self.start_time)

    @property
    def is_foundational(self) -> bool:
        return len(self.concepts_required) == 0


class VideoMetadata(BaseModel):
    id: str
    title: str
    published_at: str
    duration: int
    url: Optional[str] = None
    segments: List[VideoSegment] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        for seg in self.segments:
            if not seg.video_id:
                seg.video_id = self.id


class ChannelCatalog(BaseModel):
    channel_id: str
    channel_title: str
    videos: List[VideoMetadata] = Field(default_factory=list)


class GraphNode(BaseModel):
    id: str
    type: str  # "video_segment" | "concept"
    label: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: ConceptRelationType


class CurriculumGraph(BaseModel):
    channel_id: str
    channel_title: str
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    external_prerequisites: List[str] = Field(default_factory=list)
