from __future__ import annotations

from typing import Dict

from langchain.messages import HumanMessage, SystemMessage

from exam_practice_agent.prompts.internal_knowledge import MODEL_INTERNAL_KNOWLEDGE_PROMPT
from exam_practice_agent.state import ConversationState, InternalKnowledgeAnalysisStructure


def make_internal_solver_node(internal_llm) -> callable:
    """
    Build the node that captures the model's internal reasoning before optional retrieval.
    """

    def model_internal_solver(state: ConversationState) -> Dict[str, object]:
        question_content = (
            f"User Message: {state.get('user_message', 'None')}\n\n"
            "=== Question Context ===\n"
            f"Current Question: {state.get('current_question', 'None')}\n"
            f"Question Type: {state.get('current_question_type', 'None')}\n"
            f"Question Option: {state.get('current_question_option', 'None')}\n"
            f"Question Answer: {state.get('current_question_answer', 'None')}\n"
        )

        messages = [
            SystemMessage(content=MODEL_INTERNAL_KNOWLEDGE_PROMPT),
            HumanMessage(content=question_content),
        ]

        llm_answer: InternalKnowledgeAnalysisStructure = internal_llm.invoke(messages)

        return {
            "model_think": llm_answer.model_think,
            "model_think_confidence": llm_answer.model_think_confidence,
            "knowledge_gap": llm_answer.knowledge_gap,
            "suggested_queries": llm_answer.suggested_queries,
        }

    return model_internal_solver
