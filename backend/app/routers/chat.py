"""
API routes for the AI Chat interface.
Connects the frontend to the LangGraph agent using Server-Sent Events (SSE)
to stream the reasoning process, tool calls, and final structured response.
"""

import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
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
    Streams tokens, tool executions, and the final structured JSON.
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
            # astream_events yields every discrete step the graph takes (v2 API)
            async for event in medconnect_graph.astream_events(state, version="v2"):
                kind = event["event"]
                
                # 1. Stream raw LLM text tokens (for typing effect)
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    if chunk.content:
                        yield f"data: {json.dumps({'event': 'token', 'data': chunk.content})}\n\n"
                        
                # 2. Notify UI when a tool starts executing
                elif kind == "on_tool_start":
                    yield f"data: {json.dumps({'event': 'tool_start', 'data': {'name': event['name'], 'args': event['data'].get('input')}})}\n\n"
                    
                # 3. Notify UI when a tool finishes and return the result
                elif kind == "on_tool_end":
                    yield f"data: {json.dumps({'event': 'tool_end', 'data': {'name': event['name'], 'result': str(event['data'].get('output'))}})}\n\n"
                
                # 4. Stream the final structured JSON from the response_formatter_node
                elif kind == "on_chain_end" and event["name"] == "response_formatter":
                    final_state = event["data"].get("output", {})
                    if "final_response" in final_state:
                        yield f"data: {json.dumps({'event': 'final_json', 'data': final_state['final_response']})}\n\n"

            # Signal the end of the stream
            yield f"data: {json.dumps({'event': 'end'})}\n\n"
            
        except Exception as e:
            # Handle unexpected graph crashes gracefully
            yield f"data: {json.dumps({'event': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(generate_response(), media_type="text/event-stream")
