"""
Prompts package.
Re-exports all prompt constants and builders for clean access from graph nodes.

Usage:
    from app.prompts import get_system_prompt, TOOL_RESULT_FORMAT
"""

from app.prompts.system_prompt import get_system_prompt
from app.prompts.log_interaction_prompt import build_log_interaction_prompt, LOG_INTERACTION_PROMPT_TEMPLATE
from app.prompts.entity_extraction_prompt import build_entity_extraction_prompt, ENTITY_EXTRACTION_PROMPT_TEMPLATE
from app.prompts.summary_prompt import build_single_summary_prompt, build_rollup_summary_prompt, SINGLE_SUMMARY_PROMPT_TEMPLATE, ROLLUP_SUMMARY_PROMPT_TEMPLATE
from app.prompts.recommendation_prompt import build_recommendation_prompt

from app.prompts.formatting import (
    TOOL_RESULT_FORMAT,
    CONVERSATIONAL_FORMAT,
    ERROR_FORMAT,
)

__all__ = [
    "get_system_prompt",
    "build_log_interaction_prompt",
    "LOG_INTERACTION_PROMPT_TEMPLATE",
    "build_entity_extraction_prompt",
    "ENTITY_EXTRACTION_PROMPT_TEMPLATE",
    "build_single_summary_prompt",
    "build_rollup_summary_prompt",
    "SINGLE_SUMMARY_PROMPT_TEMPLATE",
    "ROLLUP_SUMMARY_PROMPT_TEMPLATE",
    "build_recommendation_prompt",
    "TOOL_RESULT_FORMAT",
    "CONVERSATIONAL_FORMAT",
    "ERROR_FORMAT",
]
