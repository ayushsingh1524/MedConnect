"""
CRM tools for the LangGraph agent.
These tools handle write operations: logging, editing, and scheduling.

IMPORTANT DESIGN NOTE:
These tool functions return string results for the LLM's context.
The actual database writes are executed by the Tool Execution node,
which calls the corresponding service layer functions with a live db session.
The tool functions here define the SCHEMA and DESCRIPTION that the LLM uses
to decide when and how to call them.
"""

from typing import Optional, Literal
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import uuid
import datetime
from app.database import AsyncSessionLocal
from app.services.interaction_service import create_interaction, update_interaction, create_follow_up
from app.schemas.interaction import InteractionCreate, InteractionUpdate, FollowUpCreate


# ==================== Log Interaction ====================

class LogInteractionInput(BaseModel):
    """Input schema for logging a new interaction."""
    doctor_id: str = Field(..., description="The UUID of the doctor.")
    interaction_type: Literal["in-person", "phone", "email", "video", "conference"] = Field(
        ..., description="The method of interaction."
    )
    interaction_date: str = Field(
        ..., description="Date of interaction in YYYY-MM-DD format."
    )
    raw_notes: str = Field(
        ..., description="Summary or detailed notes of the interaction."
    )
    products_discussed: list[str] = Field(
        default_factory=list,
        description="List of pharmaceutical products discussed during the interaction.",
    )
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        "neutral", description="The doctor's sentiment during the interaction."
    )
    follow_up_date: Optional[str] = Field(
        None, description="If a follow-up is needed, the date in YYYY-MM-DD format."
    )
    outcomes: Optional[str] = Field(
        None, description="ALWAYS FILL THIS. Key outcomes, agreements, or decisions from the interaction. Example: 'Doctor requested more efficacy data' or 'Agreed to trial the new medication'."
    )
    follow_up_actions: Optional[str] = Field(
        None, description="ALWAYS FILL THIS. Required follow-up actions, next steps, or reminders. Example: 'Schedule follow-up next Wednesday to provide efficacy data' or 'Send clinical trial results by email'."
    )
    dry_run: bool = Field(
        False, description="If True, only extracts details without saving to database. Use this when the user wants to populate a form manually."
    )


@tool("log_interaction", args_schema=LogInteractionInput)
async def log_interaction(
    doctor_id: str,
    interaction_type: str,
    interaction_date: str,
    raw_notes: str,
    products_discussed: list[str] = [],
    sentiment: str = "neutral",
    follow_up_date: Optional[str] = None,
    outcomes: Optional[str] = None,
    follow_up_actions: Optional[str] = None,
    dry_run: bool = False,
) -> str:
    """
    Log a new interaction with a Healthcare Professional (HCP) into the CRM.
    Use this tool when the user describes a visit, call, email, or meeting with a doctor.
    You MUST extract and provide ALL fields: date, type, products, sentiment, raw_notes, outcomes, and follow_up_actions.
    For outcomes, summarize any agreements, decisions, or requests made during the meeting.
    For follow_up_actions, list any next steps, callbacks, or reminders mentioned.
    """
    if dry_run:
        return (
            f"Extracted interaction details for doctor {doctor_id} "
            f"on {interaction_date} ({interaction_type}). "
            f"Products: {', '.join(products_discussed) if products_discussed else 'None'}. "
            f"Sentiment: {sentiment}. Outcomes: {outcomes}. Follow-up Actions: {follow_up_actions}. (Draft only, not saved)."
        )
    try:
        # Parse the date and combine with current time since AI usually just gives a date
        dt_date = datetime.datetime.strptime(interaction_date, "%Y-%m-%d").date()
        dt = datetime.datetime.combine(dt_date, datetime.datetime.now().time())
        f_dt = datetime.datetime.strptime(follow_up_date, "%Y-%m-%d").date() if follow_up_date else None
        
        # Append outcomes and follow-up actions to raw_notes if they exist
        combined_notes = raw_notes
        if outcomes:
            combined_notes += f"\n\nOutcomes: {outcomes}"
        if follow_up_actions:
            combined_notes += f"\n\nFollow-up Actions: {follow_up_actions}"
            
        interaction_data = InteractionCreate(
            doctor_id=uuid.UUID(doctor_id),
            interaction_type=interaction_type,
            interaction_date=dt,
            raw_notes=combined_notes,
            products_discussed=products_discussed,
            sentiment=sentiment,
            follow_up_date=f_dt
        )
        async with AsyncSessionLocal() as db:
            result = await create_interaction(db, interaction_data)
            await db.commit()
            
        return (
            f"Interaction {result.id} logged successfully for doctor {doctor_id} "
            f"on {interaction_date} ({interaction_type}). "
            f"Products: {', '.join(products_discussed) if products_discussed else 'None'}. "
            f"Sentiment: {sentiment}."
        )
    except Exception as e:
        return f"Error logging interaction: {str(e)}"


# ==================== Edit Interaction ====================

class EditInteractionInput(BaseModel):
    """Input schema for editing an existing interaction."""
    interaction_id: str = Field(..., description="The UUID of the interaction to edit.")
    raw_notes: Optional[str] = Field(None, description="Updated notes.")
    sentiment: Optional[str] = Field(None, description="Updated sentiment.")
    products_discussed: Optional[list[str]] = Field(
        None, description="Updated list of products discussed."
    )
    follow_up_date: Optional[str] = Field(
        None, description="Updated follow-up date in YYYY-MM-DD format."
    )
    status: Optional[str] = Field(None, description="Updated status.")


@tool("edit_interaction", args_schema=EditInteractionInput)
async def edit_interaction(
    interaction_id: str,
    raw_notes: Optional[str] = None,
    sentiment: Optional[str] = None,
    products_discussed: Optional[list[str]] = None,
    follow_up_date: Optional[str] = None,
    status: Optional[str] = None,
) -> str:
    """
    Edit an existing interaction record in the CRM.
    Use this when the user wants to update notes, sentiment, products,
    or status of a previously logged interaction.
    """
    try:
        f_dt = datetime.datetime.strptime(follow_up_date, "%Y-%m-%d").date() if follow_up_date else None
        
        update_data = InteractionUpdate()
        if raw_notes is not None: update_data.raw_notes = raw_notes
        if sentiment is not None: update_data.sentiment = sentiment
        if products_discussed is not None: update_data.products_discussed = products_discussed
        if f_dt is not None: update_data.follow_up_date = f_dt
        if status is not None: update_data.status = status
        
        async with AsyncSessionLocal() as db:
            result = await update_interaction(db, uuid.UUID(interaction_id), update_data)
            if not result:
                return f"Error: Interaction {interaction_id} not found."
            await db.commit()
            
        return (
            f"Interaction {interaction_id} updated successfully. "
        )
    except Exception as e:
        return f"Error editing interaction: {str(e)}"


# ==================== Schedule Follow-up ====================

class ScheduleFollowUpInput(BaseModel):
    """Input schema for scheduling a follow-up."""
    doctor_id: str = Field(..., description="The UUID of the doctor.")
    due_date: str = Field(..., description="Due date in YYYY-MM-DD format.")
    description: str = Field(
        ..., description="What the follow-up action entails."
    )
    priority: Literal["low", "medium", "high", "urgent"] = Field(
        "medium", description="Priority level of the follow-up."
    )
    interaction_id: Optional[str] = Field(
        None, description="Optional UUID of the related interaction."
    )


@tool("schedule_follow_up", args_schema=ScheduleFollowUpInput)
async def schedule_follow_up(
    doctor_id: str,
    due_date: str,
    description: str,
    priority: str = "medium",
    interaction_id: Optional[str] = None,
) -> str:
    """
    Schedule a follow-up task or reminder for a specific doctor.
    Use this when the user says things like 'remind me to send samples next week'
    or 'schedule a follow-up with Dr. X on Friday'.
    """
    try:
        d_dt = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
        
        follow_up_data = FollowUpCreate(
            doctor_id=uuid.UUID(doctor_id),
            due_date=d_dt,
            description=description,
            priority=priority,
            interaction_id=uuid.UUID(interaction_id) if interaction_id else None
        )
        
        async with AsyncSessionLocal() as db:
            result = await create_follow_up(db, follow_up_data)
            await db.commit()
            
        return (
            f"Follow-up {result.id} scheduled for doctor {doctor_id} on {due_date}: "
            f"{description} (Priority: {priority})."
        )
    except Exception as e:
        return f"Error scheduling follow up: {str(e)}"
