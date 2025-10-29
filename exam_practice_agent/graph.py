from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from exam_practice_agent.llm import build_llm, with_structured_output
from exam_practice_agent.nodes import (
    answer_retrieval_orchestrator,
    fallback_handler,
    make_initialize_state_node,
    make_internal_solver_node,
    profile_retrieval_orchestrator,
    quiz_generator,
    report_generator,
    solution_responder,
)
from exam_practice_agent.routing import should_continue, task_router, user_info_decider, user_intent_checker
from exam_practice_agent.state import (
    ConversationState,
    InternalKnowledgeAnalysisStructure,
    RouteDecision,
)


def build_agent():
    """
    Construct the LangGraph agent with reorganized node wiring.
    """

    base_llm = build_llm()
    route_llm = with_structured_output(base_llm, RouteDecision)
    internal_solver_llm = with_structured_output(build_llm(), InternalKnowledgeAnalysisStructure)

    initialize_state = make_initialize_state_node(route_llm)
    internal_solver = make_internal_solver_node(internal_solver_llm)

    agent = StateGraph(ConversationState)

    agent.add_node("initialize_state", initialize_state)
    agent.add_node("model_internal_solver", internal_solver)
    agent.add_node("solution_responder", solution_responder)
    agent.add_node("answer_retrieval_orchestrator", answer_retrieval_orchestrator)
    agent.add_node("profile_retrieval_orchestrator", profile_retrieval_orchestrator)
    agent.add_node("quiz_generator", quiz_generator)
    agent.add_node("report_generator", report_generator)
    agent.add_node("fallback_handler", fallback_handler)

    agent.add_edge(START, "initialize_state")
    agent.add_conditional_edges(
        "initialize_state",
        task_router,
        {
            "problem_solving": "model_internal_solver",
            "direct_answer": "solution_responder",
            "analyze": "report_generator",
            "quiz": "quiz_generator",
            "unknow": "fallback_handler",
        },
    )

    agent.add_edge("model_internal_solver", "solution_responder")
    agent.add_conditional_edges(
        "solution_responder",
        should_continue,
        {"YES": "answer_retrieval_orchestrator", "NO": END},
    )
    agent.add_edge("answer_retrieval_orchestrator", "solution_responder")

    agent.add_conditional_edges(
        "quiz_generator",
        user_info_decider,
        {"YES": "profile_retrieval_orchestrator", "NO": END},
    )

    agent.add_conditional_edges(
        "report_generator",
        user_info_decider,
        {"YES": "profile_retrieval_orchestrator", "NO": END},
    )

    agent.add_conditional_edges(
        "profile_retrieval_orchestrator",
        user_intent_checker,
        {"analyze": "report_generator", "quiz": "quiz_generator"},
    )
    agent.add_edge("fallback_handler", END)

    return agent.compile()
