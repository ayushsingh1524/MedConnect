"""
API routes for the AI Chat interface.
Connects the frontend to the LangGraph agent using Server-Sent Events (SSE)
to stream the reasoning process, tool calls, and final structured response.
"""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.deps import get_current_active_user
from app.schemas.interaction import ChatRequest
from app.graphs import medconnect_graph, AgentState

router = APIRouter()


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Stream the LangGraph agent's execution process to the frontend using SSE.
    Uses astream with 'updates' mode for reliable per-node output streaming.
    """
    
    async def generate_response():
        if not medconnect_graph:
            yield f"data: {json.dumps({'event': 'error', 'data': 'AI Agent is not configured properly.'})}\n\n"
            return

        # Initialize the LangGraph state
        state: AgentState = {
            "messages": [HumanMessage(content=request.message)],
            "hcp_context": {"id": str(request.doctor_id)} if request.doctor_id else None,
            "user_id": str(current_user.id),
            "final_response": None
        }

        try:
            # astream with stream_mode="updates" yields per-node outputs reliably
            async for node_output in medconnect_graph.astream(state, stream_mode="updates"):
                for node_name, output in node_output.items():

                    if node_name == "reasoning":
                        # Check if the AI decided to call tools or respond directly
                        msgs = output.get("messages", [])
                        for msg in msgs:
                            if isinstance(msg, AIMessage):
                                if getattr(msg, "tool_calls", None):
                                    # Notify UI about each tool being called
                                    for tc in msg.tool_calls:
                                        yield f"data: {json.dumps({'event': 'tool_start', 'data': {'name': tc['name'], 'args': tc['args']}})}\n\n"
                                elif msg.content:
                                    # Stream the AI's direct text response
                                    yield f"data: {json.dumps({'event': 'token', 'data': msg.content})}\n\n"

                    elif node_name == "tools":
                        # Tool execution finished
                        msgs = output.get("messages", [])
                        for msg in msgs:
                            if isinstance(msg, ToolMessage):
                                yield f"data: {json.dumps({'event': 'tool_end', 'data': {'name': msg.name, 'result': str(msg.content)[:200]}})}\n\n"

                    elif node_name == "response_formatter":
                        # The final structured response
                        final = output.get("final_response")
                        if final:
                            # Send the human-readable message as a token
                            message = final.get("message", "")
                            if message:
                                yield f"data: {json.dumps({'event': 'token', 'data': message})}\n\n"
                            # Send the full structured JSON for the UI
                            yield f"data: {json.dumps({'event': 'final_json', 'data': final})}\n\n"

            # Signal the end of the stream
            yield f"data: {json.dumps({'event': 'end'})}\n\n"
            
        except Exception as e:
            # Handle unexpected graph crashes gracefully
            yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")
