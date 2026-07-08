"""
LangGraph agent state definition.
This TypedDict is the shared state object passed between every node in the graph.
"""

from typing import TypedDict, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    The state schema for the MedConnect AI agent graph.

    Attributes:
        messages:
            The full conversation history (Human, AI, Tool messages).
            Uses the `add_messages` reducer so new messages are APPENDED,
            never overwritten. This is the standard LangGraph pattern.

        hcp_context:
            Optional dictionary holding the currently resolved doctor context
            (e.g., {"id": "uuid", "name": "Dr. Smith"}).
            Overwritten when a doctor is resolved during a tool call.

        user_id:
            The UUID string of the authenticated pharmaceutical rep making the request.

        final_response:
            The structured JSON dictionary produced by the Response Formatter node.
            Written only at the end of the graph execution.
    """

    # Append-only message history (LangGraph's built-in reducer)
    messages: Annotated[list[BaseMessage], add_messages]

    # Contextual metadata (overwrite semantics)
    hcp_context: Optional[dict]
    user_id: str
    final_response: Optional[dict]
