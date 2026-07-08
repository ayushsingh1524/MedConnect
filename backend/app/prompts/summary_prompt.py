"""
Summary Prompt — AI Interaction Summarisation
===============================================

PURPOSE:
    Generates concise, professional summaries of doctor interactions from
    raw field rep notes. This prompt serves two distinct use cases:

    1. **Single Interaction Summary** — After a rep logs an interaction,
       the AI generates a clean 2-3 sentence summary for the CRM record.
       This replaces the `ai_summary` field on the Interaction model.

    2. **Multi-Interaction Rollup** — When a rep views a doctor's profile
       or prepares for a visit, the AI synthesises multiple past interactions
       into a single engagement narrative.

MODEL TARGET:
    Groq gemma2-9b-it — Summarisation is a core strength of this model.
    The prompt constrains output length explicitly (sentence count and
    word count) because Gemma 2 tends to be verbose without hard limits.

DESIGN NOTES:
    - The "CRM voice" instructions ensure summaries read like professional
      CRM entries, not casual chat messages or academic papers.
    - The structured JSON output includes both the summary text and
      extracted metadata (key topics, action items) so the frontend can
      render rich summary cards.
    - For multi-interaction rollups, interactions are sorted chronologically
      and the prompt emphasises trajectory/trends over individual events.
"""


def build_single_summary_prompt(
    raw_notes: str,
    interaction_type: str = None,
    doctor_name: str = None,
    products: list[str] = None,
    sentiment: str = None,
    interaction_date: str = None,
) -> str:
    """
    Build a prompt to summarise a single interaction's raw notes into
    a professional CRM summary.

    Args:
        raw_notes: The rep's raw, unedited notes from the interaction.
        interaction_type: e.g., "in-person", "phone", "email".
        doctor_name: The HCP's name.
        products: List of products discussed.
        sentiment: Detected sentiment ("positive", "neutral", "negative").
        interaction_date: ISO date string.

    Returns:
        A formatted prompt string for LLM invocation with JSON mode.
    """

    # Build metadata context so the summary is grounded in facts
    context_lines = []
    if doctor_name:
        context_lines.append(f"Doctor: {doctor_name}")
    if interaction_type:
        context_lines.append(f"Type: {interaction_type}")
    if interaction_date:
        context_lines.append(f"Date: {interaction_date}")
    if products:
        context_lines.append(f"Products discussed: {', '.join(products)}")
    if sentiment:
        context_lines.append(f"Detected sentiment: {sentiment}")

    context_block = "\n".join(context_lines) if context_lines else "No additional context provided."

    return f"""You are a CRM summarisation engine for pharmaceutical field sales. Your task is to transform raw interaction notes into a clean, professional summary.

## INTERACTION METADATA
{context_block}

## RAW NOTES
\"\"\"{raw_notes}\"\"\"

## SUMMARISATION RULES

1. **Length:** 2-3 sentences. Maximum 75 words. Be ruthlessly concise.
2. **Voice:** Professional, third-person, past tense. Write as if this will appear in a CRM report read by a sales manager.
   - ✅ "Discussed CardioMax efficacy data with Dr. Rivera. Doctor expressed interest in phase 3 results and requested the full study report."
   - ❌ "I went and talked to Dr. Rivera about CardioMax and she seemed pretty into it."
3. **Structure:** Lead with WHAT happened, then the doctor's RESPONSE, then any NEXT STEPS.
4. **Products:** Always mention specific product names discussed. Use exact capitalisation.
5. **Sentiment reflection:** The tone of the summary should subtly reflect the detected sentiment without using the word "positive/negative/neutral".
   - Positive → use words like "receptive", "interested", "agreed", "committed"
   - Negative → use words like "expressed concerns", "declined", "unconvinced"
   - Neutral → use factual language, no emotional valence
6. **Action items:** If the notes mention any follow-up action, include it as the final sentence.
7. **Never invent facts.** If something isn't in the raw notes, don't add it.

## OUTPUT FORMAT

Return a JSON object:

{{
  "summary": "<the 2-3 sentence professional summary>",
  "key_topics": ["<topic1>", "<topic2>"],
  "action_items": ["<action1>", "<action2>"] or [],
  "sentiment_label": "<positive | neutral | negative>",
  "word_count": <integer>
}}

**Field definitions:**
- `summary`: The polished CRM summary text.
- `key_topics`: 2-5 key discussion topics extracted from the notes (short phrases).
- `action_items`: Any follow-up actions mentioned. Empty list if none.
- `sentiment_label`: Your assessment of overall interaction sentiment.
- `word_count`: The word count of the summary field (for validation).

Return ONLY the JSON object. No markdown fences, no explanation.
"""


def build_rollup_summary_prompt(
    interactions: list[dict],
    doctor_name: str,
    doctor_specialty: str = None,
) -> str:
    """
    Build a prompt to synthesise multiple interactions with the same doctor
    into an engagement narrative / rollup summary.

    Args:
        interactions: List of dicts, each with keys:
                      "date", "type", "summary" (or "raw_notes"),
                      "products", "sentiment".
                      Should be sorted chronologically (oldest first).
        doctor_name: The HCP's name.
        doctor_specialty: e.g., "Cardiology".

    Returns:
        A formatted prompt string for LLM invocation with JSON mode.
    """

    # Format the interaction timeline
    timeline_entries = []
    for i, ix in enumerate(interactions, 1):
        date = ix.get("date", "Unknown date")
        ix_type = ix.get("type", "unknown")
        summary = ix.get("summary") or ix.get("raw_notes", "No notes")
        products = ", ".join(ix.get("products", [])) or "None"
        sentiment = ix.get("sentiment", "neutral")

        timeline_entries.append(
            f"{i}. [{date}] ({ix_type}) — {summary}\n"
            f"   Products: {products} | Sentiment: {sentiment}"
        )

    timeline_text = "\n\n".join(timeline_entries)

    specialty_note = f" ({doctor_specialty})" if doctor_specialty else ""

    return f"""You are a CRM analytics engine. Synthesise the interaction history below into an engagement narrative for a sales manager preparing for a territory review.

## DOCTOR PROFILE
Name: {doctor_name}{specialty_note}
Total interactions: {len(interactions)}

## INTERACTION TIMELINE (oldest → newest)

{timeline_text}

## ROLLUP RULES

1. **Length:** 4-6 sentences. Maximum 150 words.
2. **Focus on trajectory:** How has the relationship evolved over time? Is engagement increasing or decreasing?
3. **Product affinity:** Which products resonate most? Which were rejected?
4. **Sentiment trend:** Is the doctor becoming more receptive, more resistant, or staying flat?
5. **Recency bias:** Weight recent interactions more heavily than old ones.
6. **Actionable closing:** End with a concrete recommendation for the next engagement.

## OUTPUT FORMAT

Return a JSON object:

{{
  "rollup_summary": "<the 4-6 sentence engagement narrative>",
  "relationship_status": "<growing | stable | declining | new>",
  "top_products": ["<most discussed product>", "<second>"],
  "sentiment_trend": "<improving | stable | declining>",
  "engagement_frequency": "<high | moderate | low>",
  "last_interaction_date": "<ISO date of most recent interaction>",
  "recommended_next_action": "<specific, actionable recommendation>"
}}

Return ONLY the JSON object. No markdown fences, no explanation.
"""


# ──────────────────────────────────────────────────────────────
# Convenience constants for backward compatibility.
# Production code should call the builder functions directly.
# ──────────────────────────────────────────────────────────────

SINGLE_SUMMARY_PROMPT_TEMPLATE = (
    "Summarise the following interaction notes into a professional "
    "2-3 sentence CRM summary. Return JSON with 'summary', 'key_topics', "
    "'action_items', 'sentiment_label', and 'word_count'.\n\n"
    "Notes: {raw_notes}"
)

ROLLUP_SUMMARY_PROMPT_TEMPLATE = (
    "Synthesise the following interaction history for {doctor_name} into "
    "an engagement narrative. Return JSON with 'rollup_summary', "
    "'relationship_status', 'top_products', 'sentiment_trend', "
    "'engagement_frequency', 'last_interaction_date', and "
    "'recommended_next_action'.\n\n"
    "Interactions:\n{interactions_text}"
)
