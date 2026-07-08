"""
Recommendation Prompt — Next Best Action Generation
===================================================

PURPOSE:
    Analyzes a doctor's interaction history to generate strategic "Next Best Action" (NBA) 
    recommendations for the sales representative. This is a crucial AI feature of the CRM.

MODEL TARGET:
    Groq gemma2-9b-it — Excellent at reasoning and synthesizing information. 
    The prompt asks the model to output distinct, actionable recommendations 
    with a clear "why" and "how".

DESIGN NOTES:
    - We feed the model a structured summary of past interactions.
    - Recommendations must be actionable, not vague (e.g., "Bring phase 3 trial data" 
      instead of "Follow up").
    - Categorizing recommendations by type (e.g., 'clinical', 'relationship', 'administrative')
      allows for better UI presentation.
"""


def build_recommendation_prompt(
    doctor_name: str,
    doctor_specialty: str = None,
    interaction_history: str = None,
    upcoming_follow_ups: str = None,
) -> str:
    """
    Build a prompt to generate AI recommendations for a specific doctor.

    Args:
        doctor_name: The HCP's name.
        doctor_specialty: e.g., "Cardiology".
        interaction_history: Formatted string of past interactions.
        upcoming_follow_ups: Formatted string of pending tasks.

    Returns:
        A formatted prompt string ready for LLM invocation.
    """

    specialty_str = f" ({doctor_specialty})" if doctor_specialty else ""
    
    history_section = (
        f"## INTERACTION HISTORY\n{interaction_history}" 
        if interaction_history else "## INTERACTION HISTORY\nNo past interactions recorded."
    )
    
    follow_ups_section = (
        f"## PENDING FOLLOW-UPS\n{upcoming_follow_ups}" 
        if upcoming_follow_ups else "## PENDING FOLLOW-UPS\nNo pending tasks."
    )

    return f"""You are a strategic AI advisor for pharmaceutical sales representatives. 
Your goal is to suggest the "Next Best Action" (NBA) for engaging with a specific Healthcare Professional (HCP).

## DOCTOR PROFILE
Name: {doctor_name}{specialty_str}

{history_section}

{follow_ups_section}

## RECOMMENDATION RULES

Based on the doctor's profile, history, and pending tasks, generate 2-3 highly specific, actionable recommendations.

1. **Specificity:** Do not say "Follow up soon." Say "Schedule a follow-up call next week to discuss the new safety profile of CardioMax."
2. **Context-Awareness:** 
   - If the sentiment was recently negative, suggest a softer, relationship-building approach.
   - If they are highly interested in clinical data, suggest bringing specific medical literature.
   - If there are overdue follow-ups, prioritize them.
3. **Categories:** Assign one of these categories to each recommendation:
   - `clinical`: Sharing data, discussing efficacy, side effects, etc.
   - `logistical`: Dropping off samples, scheduling a lunch, etc.
   - `relationship`: Checking in, non-promotional touchpoints.

## OUTPUT FORMAT

Return a JSON object with this exact structure:

{{
  "recommendations": [
    {{
      "title": "<A short, punchy title, max 5-7 words>",
      "description": "<Detailed explanation of what to do and why, 2-3 sentences>",
      "category": "<clinical | logistical | relationship>",
      "priority": "<high | medium | low>",
      "reasoning": "<1 sentence explaining why this is recommended based on their history>"
    }}
  ],
  "overall_strategy": "<1-2 sentences summarizing the general approach for this doctor>"
}}

Return ONLY the JSON object. No markdown fences, no explanation.
"""
