import os
from typing import Optional, Type

from langchain_anthropic import ChatAnthropic

DEFAULT_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")


def build_llm(model: Optional[str] = None) -> ChatAnthropic:
    """
    Construct the base Anthropic chat model.

    Parameters
    ----------
    model:
        Optional override for the Anthropics model name. Defaults to
        the `ANTHROPIC_MODEL` environment variable or `claude-sonnet-4-5`.
    """

    return ChatAnthropic(model=model or DEFAULT_MODEL)


def with_structured_output(llm: ChatAnthropic, schema: Type) -> ChatAnthropic:
    """
    Convenience helper to attach a structured output schema to the LLM.
    """

    return llm.with_structured_output(schema)
