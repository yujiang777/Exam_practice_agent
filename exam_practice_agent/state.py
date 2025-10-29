from typing import List, Optional
import operator

from langchain.messages import AnyMessage
from pydantic import BaseModel, Field
from typing_extensions import Annotated, Literal, TypedDict


class ConversationState(TypedDict, total=False):
    """Shared conversation state passed between LangGraph nodes."""

    # LangGraph message history (automatically accumulated).
    history: Annotated[list[AnyMessage], operator.add]

    # User input.
    user_message: str

    # Repeated question detection.
    last_question: Optional[str]

    # Metadata about the current question being processed.
    current_question: Optional[str]
    current_question_type: Optional[str]
    current_question_option: Optional[str]
    current_question_answer: Optional[str]

    # Global execution metadata.
    current_state: str
    problem_solver_model: str
    retrieved_time: int

    # Model reasoning artifacts.
    model_think: Optional[str]
    model_think_confidence: Optional[int]
    knowledge_gap: Optional[str]
    suggested_queries: Optional[List[str]]
    retrieved_context: Optional[str]

    # Routing metadata.
    current_route: Optional[str]
    current_route_reason: Optional[str]


class RouteDecision(BaseModel):
    """Structured decision returned by the routing model."""

    reasoning: str = Field(description="Reasoning behind the routing decision.")
    next_state: Literal["problem_solving", "direct_answer", "analyze", "quiz", "unknow"] = Field(
        description="The next step in the routing process."
    )


class InternalKnowledgeAnalysisStructure(BaseModel):
    """
    Represents the analysis result based solely on the model's internal knowledge.
    Determines whether to answer directly or to trigger retrieval for knowledge enrichment.
    """

    model_think: str = Field(
        description="The complete reasoning process or preliminary answer based on internal knowledge."
    )
    model_think_confidence: int = Field(
        description="Confidence score for the answer, ranging from 0 to 10.", ge=0, le=10
    )
    knowledge_gap: Optional[str] = Field(
        default=None,
        description="Missing information if confidence is low; null when confidence >= 8.",
    )
    suggested_queries: Optional[List[str]] = Field(
        default=None,
        description="Suggested search queries when additional retrieval is required.",
    )
