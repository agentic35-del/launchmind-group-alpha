from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


MessageType = Literal["task", "result", "revision_request", "confirmation"]


class AgentMessage(BaseModel):
    message_id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: str
    parent_message_id: Optional[str] = None


class Persona(BaseModel):
    name: str
    role: str
    pain_point: str


class Feature(BaseModel):
    name: str
    description: str
    priority: int = Field(ge=1, le=5)


class ProductSpec(BaseModel):
    startup_name: str
    value_proposition: str
    personas: List[Persona]
    features: List[Feature]
    user_stories: List[str]
    success_metrics: List[str]