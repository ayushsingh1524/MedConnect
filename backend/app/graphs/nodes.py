"""
LangGraph Nodes.
These functions represent the discrete steps in the LangGraph state machine.
"""

import json
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from app.config import get_settings
from app.graphs.state import AgentState
from app.tools import ALL_TOOLS
from app.prompts import (
    get_system_prompt,
    TOOL_RESULT_FORMAT,
    CONVERSATIONAL_FORMAT,
)

settings = get_settings()

# Initialize the Groq model
# gemma2-9b-it provides excellent reasoning and tool-calling capabilities
try:
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,  # Zero temperature for deterministic reasoning
        api_key=settings.GROQ_API_KEY or "dummy_key",
    )
    llm_with_tools = llm.bind_tools(ALL_TOOLS)
except Exception:
    llm = None
    llm_with_tools = None


async def reasoning_node(state: AgentState) -> dict:
    """
    The core reasoning engine.
    Analyzes the conversation history, applies the system prompt, and either
    replies directly or decides to invoke one of the bound tools.
    """
    messages = state["messages"]

    # Ensure the system prompt is always at the start of the context window
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=get_system_prompt())] + messages

    # Invoke the LLM
    response = await llm_with_tools.ainvoke(messages)

    # Return the new AIMessage to be appended to the state
    return {"messages": [response]}


async def response_formatter_node(state: AgentState) -> dict:
    """
    The final node in the graph.
    Forces the LLM to output a strictly formatted JSON object based on the
    results of the conversation or tool executions. This JSON is what the
    frontend will consume.
    """
    messages = state["messages"]
    
    # Check if the last action was a tool execution
    was_tool_executed = False
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            was_tool_executed = True
            break
        elif isinstance(msg, HumanMessage):
            break

    # Select the appropriate formatting template
    template = TOOL_RESULT_FORMAT if was_tool_executed else CONVERSATIONAL_FORMAT
    
    # Create a string representation of the conversation for context
    conv_context = "\n".join(
        f"{type(m).__name__}: {m.content}" for m in messages[-5:]
    )
    
    prompt = template.format(conversation=conv_context)

    # Use JSON mode for guaranteed structured output
    formatter_llm = llm.bind(response_format={"type": "json_object"})
    response = await formatter_llm.ainvoke([HumanMessage(content=prompt)])

    try:
        final_json = json.loads(response.content)
    except Exception:
        # Fallback if parsing fails
        final_json = {
            "status": "error",
            "action": "format",
            "message": "Failed to parse AI response into structured JSON.",
            "data": {"raw": response.content},
            "follow_up_suggestion": None
        }

    return {"final_response": final_json}
