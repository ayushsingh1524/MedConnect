"""
Read-only and AI-powered tools for the LangGraph agent.
These tools query the database and generate recommendations.
"""

import uuid
import json
import datetime
from typing import Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.database import AsyncSessionLocal
from app.services.interaction_service import get_interactions
from app.services.hcp_service import get_doctor_by_id, get_all_doctors


# ==================== Search Doctors ====================

class SearchDoctorsInput(BaseModel):
    """Input schema for searching doctors by name and/or specialty."""
    name: Optional[str] = Field(None, description="The doctor's name or partial name to search for.")
    specialty: Optional[str] = Field(None, description="The medical specialty to filter by (e.g. Cardiology, Neurology, Oncology).")


@tool("search_doctors", args_schema=SearchDoctorsInput)
async def search_doctors(name: Optional[str] = None, specialty: Optional[str] = None) -> str:
    """
    Search for doctors by name and/or specialty in the CRM database.
    Use this FIRST whenever the user mentions a doctor by name or specialty, to get their UUID.
    You MUST call this before log_interaction, schedule_follow_up, or ai_recommendation
    if you only have the doctor's name and not their UUID.
    """
    try:
        async with AsyncSessionLocal() as db:
            doctors, total = await get_all_doctors(
                db, search=name, specialty=specialty, limit=10
            )

        if not doctors:
            search_desc = []
            if name:
                search_desc.append(f"name '{name}'")
            if specialty:
                search_desc.append(f"specialty '{specialty}'")
            return f"No doctors found matching {' and '.join(search_desc) or 'the criteria'}."

        results = []
        for doc in doctors:
            results.append(
                f"- ID: {doc.id} | Name: {doc.name} | Specialty: {doc.specialty} "
                f"| Hospital: {doc.hospital} | City: {doc.city}"
            )

        return (
            f"Found {total} doctor(s):\n"
            + "\n".join(results)
        )
    except Exception as e:
        return f"Error searching doctors: {str(e)}"


# ==================== Search Interactions ====================

class SearchInteractionsInput(BaseModel):
    """Input schema for searching past interactions."""
    query: Optional[str] = Field(
        None, description="Free-text search query for keywords in notes or summaries."
    )
    doctor_id: Optional[str] = Field(
        None, description="Filter by a specific doctor's UUID."
    )
    date_from: Optional[str] = Field(
        None, description="Start date for the search in YYYY-MM-DD format."
    )
    date_to: Optional[str] = Field(
        None, description="End date for the search in YYYY-MM-DD format."
    )


@tool("search_interactions", args_schema=SearchInteractionsInput)
async def search_interactions(
    query: Optional[str] = None,
    doctor_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> str:
    """
    Search past interaction history in the CRM database.
    Use this when the user asks questions like 'What did we discuss last time?',
    'Find my visits with Dr. Smith', or 'Show interactions from last week'.
    Returns real data from the database.
    """
    try:
        # Parse optional filters
        d_id = uuid.UUID(doctor_id) if doctor_id else None
        d_from = datetime.datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
        d_to = datetime.datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None

        async with AsyncSessionLocal() as db:
            interactions, total = await get_interactions(
                db,
                doctor_id=d_id,
                date_from=d_from,
                date_to=d_to,
                search=query,
                limit=10,
            )

        if not interactions:
            return "No interactions found matching the search criteria."

        # Format results for the LLM context
        results = []
        for ix in interactions:
            results.append(
                f"- [{ix.interaction_date}] ({ix.interaction_type}) "
                f"Sentiment: {ix.sentiment or 'N/A'}. "
                f"Products: {', '.join(ix.products_discussed) if ix.products_discussed else 'None'}. "
                f"Summary: {ix.ai_summary or ix.raw_notes or 'No notes'}"
            )

        return (
            f"Found {total} interaction(s). Showing top {len(interactions)}:\n"
            + "\n".join(results)
        )
    except Exception as e:
        return f"Error searching interactions: {str(e)}"


# ==================== AI Recommendation ====================

class AIRecommendationInput(BaseModel):
    """Input schema for generating strategic recommendations."""
    doctor_id: str = Field(..., description="The UUID of the doctor.")


@tool("ai_recommendation", args_schema=AIRecommendationInput)
async def ai_recommendation(doctor_id: str) -> str:
    """
    Generate strategic engagement recommendations for a given doctor
    based on their past interaction history. Use this when the user asks
    for advice, strategy, or 'what should I discuss with Dr. X?'.
    """
    try:
        d_id = uuid.UUID(doctor_id)

        async with AsyncSessionLocal() as db:
            doctor = await get_doctor_by_id(db, d_id)
            if not doctor:
                return f"Error: Doctor with ID {doctor_id} not found."

            interactions, total = await get_interactions(db, doctor_id=d_id, limit=10)

        doctor_name = doctor.name
        specialty = doctor.specialty

        if not interactions:
            return (
                f"No past interactions found for Dr. {doctor_name} ({specialty}). "
                f"Recommendation: Schedule an introductory visit to understand their "
                f"prescribing habits and clinical interests."
            )

        # Build a context summary from interaction history
        history_lines = []
        for ix in interactions:
            history_lines.append(
                f"- [{ix.interaction_date}] ({ix.interaction_type}) "
                f"Sentiment: {ix.sentiment or 'neutral'}. "
                f"Products: {', '.join(ix.products_discussed) if ix.products_discussed else 'None'}. "
                f"Notes: {ix.ai_summary or ix.raw_notes or 'N/A'}"
            )

        history_text = "\n".join(history_lines)

        # Analyze patterns for recommendations
        sentiments = [ix.sentiment for ix in interactions if ix.sentiment]
        products = []
        for ix in interactions:
            if ix.products_discussed:
                products.extend(ix.products_discussed)

        positive_pct = (sentiments.count("positive") / len(sentiments) * 100) if sentiments else 0
        top_products = list(set(products))[:5] if products else ["No products discussed yet"]
        last_date = interactions[0].interaction_date if interactions else "Unknown"

        return (
            f"Recommendation for Dr. {doctor_name} ({specialty}):\n"
            f"- Total interactions: {total}\n"
            f"- Last contact: {last_date}\n"
            f"- Positive sentiment rate: {positive_pct:.0f}%\n"
            f"- Key products: {', '.join(top_products)}\n"
            f"- Interaction history:\n{history_text}\n\n"
            f"Based on this data, provide specific, actionable next-step recommendations."
        )
    except Exception as e:
        return f"Error generating recommendation: {str(e)}"
