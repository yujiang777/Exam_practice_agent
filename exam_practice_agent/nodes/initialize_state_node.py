from __future__ import annotations

from typing import Dict

from langchain.messages import HumanMessage, SystemMessage

from exam_practice_agent.prompts.router import ROUTER_PROMPT
from exam_practice_agent.state import ConversationState, RouteDecision


def make_initialize_state_node(route_llm) -> callable:
    """
    Build the initialization node responsible for resetting transient state
    and routing the next step in the LangGraph workflow.
    """

    def initialize_state(state: ConversationState) -> Dict[str, object]:
        updates: Dict[str, object] = {}

        if state.get("last_question") != state.get("current_question"):
            updates.update(
                {
                    "model_think": None,
                    "model_think_confidence": None,
                    "retrieved_context": None,
                    "suggested_queries": None,
                    "knowledge_gap": None,
                    "analysis_summary": None,
                    "quiz_tasks": None,
                    "final_report": None,
                    "last_response": None,
                }
            )

        analyze_content = (
            f"User Message: {state.get('user_message', '')}\n\n"
            "=== Context Info ===\n"
            f"Current Question: {state.get('current_question', 'None')}\n"
            f"Internal Knowledge: {state.get('model_think', 'None')}\n"
            f"Retrieved Context: {state.get('retrieved_context', 'None')}"
        )

        messages = [
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=analyze_content),
        ]

        next_route: RouteDecision = route_llm.invoke(messages)

        updates["last_question"] = state.get("current_question")
        updates["current_route"] = next_route.next_state
        updates["current_route_reason"] = next_route.reasoning

        return updates

    return initialize_state
