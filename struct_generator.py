from __future__ import annotations

from exam_practice_agent import build_agent


def generate_structure(
    output_path: str = "langgraph_structure.png", mermaid_path: str = "langgraph_structure.mmd"
):
    """Render the LangGraph structure for the Exam Practice Agent."""

    agent = build_agent()
    graph = agent.get_graph(xray=True)

    try:
        from langchain_core.runnables.graph_mermaid import MermaidDrawMethod  # type: ignore
        png_bytes = graph.draw_mermaid_png(max_retries=5, retry_delay=2.0, draw_method=MermaidDrawMethod.API)
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        print(f"Exam Practice Agent graph compiled. Saved visualization to {output_path}")

        try:
            from IPython.display import Image, display  # type: ignore

            display(Image(png_bytes))
        except ImportError:
            print("IPython not available; skipped inline display.")
    except Exception as exc:  # noqa: BLE001
        mermaid = graph.draw_mermaid()
        with open(mermaid_path, "w", encoding="utf-8") as f:
            f.write(mermaid)
        print(
            "Exam Practice Agent graph compiled. PNG rendering failed, "
            f"saved Mermaid markup to {mermaid_path}. Reason: {exc}"
        )

    return agent


if __name__ == "__main__":
    generate_structure()
