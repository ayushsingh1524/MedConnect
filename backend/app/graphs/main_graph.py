"""
Main graph definition.
Compiles the state, nodes, and edges into the executable LangGraph.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from app.graphs.state import AgentState
from app.graphs.nodes import reasoning_node, response_formatter_node
from app.tools import ALL_TOOLS


def should_continue(state: AgentState) -> Literal["tools", "response_formatter"]:
    """
    Conditional routing edge from the reasoning node.
    If the LLM invoked a tool, route to the tools node.
    Otherwise, route to the response formatter to output the final JSON.
    """
    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM returned a ToolCall, go execute the tools
    if getattr(last_message, "tool_calls", None):
        return "tools"

    # Otherwise, it has finished reasoning and is ready to respond
    return "response_formatter"


def create_agent_graph():
    """
    Builds and compiles the StateGraph for the MedConnect agent.
    """
    workflow = StateGraph(AgentState)

    # Add the core nodes
    workflow.add_node("reasoning", reasoning_node)
    
    # ToolNode is a pre-built LangGraph node that automatically executes the 
    # bound python functions when given a ToolCall message.
    workflow.add_node("tools", ToolNode(ALL_TOOLS))
    
    workflow.add_node("response_formatter", response_formatter_node)

    # Define the topology (edges)
    workflow.add_edge(START, "reasoning")
    
    # Conditional logic based on LLM output
    workflow.add_conditional_edges(
        "reasoning",
        should_continue,
        {
            "tools": "tools",
            "response_formatter": "response_formatter"
        }
    )
    
    # Tools always return their results back to the reasoning engine
    workflow.add_edge("tools", "reasoning")
    
    # The formatter is the final step
    workflow.add_edge("response_formatter", END)

    # Compile the graph into a runnable construct
    return workflow.compile()


# Create a singleton instance of the graph
try:
    medconnect_graph = create_agent_graph()
except Exception:
    medconnect_graph = None
