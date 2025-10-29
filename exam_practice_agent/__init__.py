"""
Exam Practice Agent package.

This package reorganizes the logic originally found in `all_code.py`
into focused modules for state definitions, prompt management,
node implementations, and graph construction utilities.
"""

from .graph import build_agent

__all__ = ["build_agent"]
