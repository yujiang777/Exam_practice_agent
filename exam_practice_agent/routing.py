from __future__ import annotations

from typing import Dict, Literal

from exam_practice_agent.state import ConversationState


def task_router(state: ConversationState) -> str:
    """Map the current route into graph edge labels."""

    route = state.get("current_route")
    return route


def should_continue(state: Dict[str, object]) -> Literal["YES", "NO"]:
    """
    Decide whether to keep looping based on the last message containing a tool call.
    """

    messages = state.get("history") or []
    if not messages:
        return "NO"

    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "YES"

    return "NO"





def user_info_decider(state: ConversationState) -> Literal["YES", "NO"]:
    """
    Decide if the flow should branch into user-profile retrieval.
    """

    _ = state  # placeholder until implemented
    return "NO"

def user_intent_checker(state: ConversationState) -> Literal["analyze", "quiz"]:
    """
    Check the user's intent based on the current state.
    """

    _ = state  # placeholder until implemented
    return "analyze"
