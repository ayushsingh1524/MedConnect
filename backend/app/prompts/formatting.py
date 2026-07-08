"""
Output formatting templates for the LangGraph agent's Response Formatter node.
These templates define the structured JSON schemas the agent must conform to
when returning results to the frontend.
"""

TOOL_RESULT_FORMAT = """
Based on the conversation and tool results, produce a final JSON response for the frontend.

The response MUST follow this exact schema:

{{
  "status": "success" or "error",
  "action": "<the tool that was executed, e.g., log_interaction, search_interactions>",
  "message": "<a concise, user-friendly summary of what happened>",
  "data": {{
    // Relevant structured data from the tool execution.
    // For log_interaction: include the interaction_id, doctor_name, date.
    // For search_interactions: include a list of matching interactions.
    // For schedule_follow_up: include the follow_up_id, due_date, description.
    // For ai_recommendation: include the recommendations list.
    // For edit_interaction: include the updated fields.
  }},
  "follow_up_suggestion": "<optional next action the user might want to take, or null>"
}}

Conversation context:
{conversation}

Produce ONLY the JSON. No markdown fences, no explanation.
"""

CONVERSATIONAL_FORMAT = """
Based on the conversation, produce a final JSON response for the frontend.
No tools were called — this is a direct conversational reply.

{{
  "status": "success",
  "action": "conversation",
  "message": "<your helpful response to the user>",
  "data": null,
  "follow_up_suggestion": "<optional suggestion, or null>"
}}

Conversation context:
{conversation}

Produce ONLY the JSON. No markdown fences, no explanation.
"""

ERROR_FORMAT = """
An error occurred during processing. Produce a structured error response.

{{
  "status": "error",
  "action": "{action}",
  "message": "{error_message}",
  "data": null,
  "follow_up_suggestion": "Please try again or rephrase your request."
}}
"""
