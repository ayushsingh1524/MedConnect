"""
Log Interaction Prompt — Field Extraction for CRM Logging
==========================================================

PURPOSE:
    When a user describes a doctor interaction conversationally (e.g.,
    "I visited Dr. Patel today and discussed CardioMax, she was very
    receptive"), this prompt instructs the LLM to extract the structured
    fields required by the `log_interaction` tool.

    This is a PRE-TOOL prompt — it runs BEFORE the tool is called, to
    transform unstructured natural language into a validated JSON payload.

MODEL TARGET:
    Groq gemma2-9b-it — We use explicit field-by-field instructions with
    examples because Gemma 2 benefits from concrete demonstrations over
    abstract rules. The JSON schema is spelled out literally to avoid
    malformed output.

DESIGN NOTES:
    - Few-shot examples are included inline. Gemma 2 9B performs
      significantly better with 2-3 examples than with zero-shot.
    - Each field has a fallback rule (what to do when the info is missing).
    - The prompt enforces ISO date format explicitly because smaller models
      frequently output dates in ambiguous formats like "July 8th".
    - Products are normalised to title case to avoid duplicates like
      "cardiomax" vs "CardioMax".
"""

import datetime


def build_log_interaction_prompt(user_message: str, doctor_context: dict = None) -> str:
    """
    Build a prompt that extracts structured interaction data from a
    user's free-text description.

    Args:
        user_message: The raw conversational input from the sales rep.
        doctor_context: Optional dict with pre-resolved doctor info,
                        e.g. {"id": "uuid-string", "name": "Dr. Smith"}.
                        Passed when the doctor was already identified
                        in a prior turn.

    Returns:
        A formatted prompt string ready for LLM invocation.
    """
    today = datetime.date.today().isoformat()

    doctor_hint = ""
    if doctor_context:
        doctor_hint = f"""
KNOWN DOCTOR CONTEXT (from prior conversation):
- doctor_id: "{doctor_context.get('id', 'UNKNOWN')}"
- doctor_name: "{doctor_context.get('name', 'UNKNOWN')}"
Use this doctor_id in your output. Do not ask the user again.
"""

    return f"""You are a data extraction assistant for a pharmaceutical CRM system.

Today's date is {today}.

Your task: Extract structured interaction data from the user's message below.
{doctor_hint}
## USER MESSAGE
\"\"\"{user_message}\"\"\"

## EXTRACTION RULES

For each field, follow these rules exactly:

1. **doctor_name** (string | null)
   - Extract the doctor's name as stated. Include "Dr." prefix if present.
   - If no name is mentioned, set to `null`.

2. **doctor_id** (string | null)
   - Only populate if provided in KNOWN DOCTOR CONTEXT above.
   - Never guess or fabricate a UUID. Set to `null` if unknown.

3. **interaction_type** (string | null)
   - Must be one of: `"in-person"`, `"phone"`, `"email"`, `"video"`, `"conference"`
   - Mapping rules:
     * "visited", "met", "stopped by", "office visit", "clinic" → `"in-person"`
     * "called", "phone call", "rang" → `"phone"`
     * "emailed", "sent email", "wrote to" → `"email"`
     * "video call", "zoom", "teams", "virtual" → `"video"`
     * "conference", "event", "symposium", "seminar" → `"conference"`
   - If unclear, set to `null`.

4. **interaction_date** (string | null)
   - Must be in ISO format: `YYYY-MM-DD`
   - Relative date resolution (today is {today}):
     * "today" → `"{today}"`
     * "yesterday" → subtract 1 day
     * "last week" → subtract 7 days
     * "this morning" → `"{today}"`
   - If no date is mentioned, set to `null`.

5. **products_discussed** (list of strings)
   - Extract all pharmaceutical product or drug names mentioned.
   - Normalise to Title Case (e.g., "cardiomax" → "CardioMax").
   - If none mentioned, return an empty list `[]`.

6. **sentiment** (string)
   - Must be one of: `"positive"`, `"neutral"`, `"negative"`
   - Positive signals: "interested", "excited", "agreed", "receptive", "wants to try", "happy"
   - Negative signals: "refused", "not interested", "complained", "dismissed", "skeptical"
   - Neutral signals: factual tone, no strong emotion, "sent info", "dropped samples"
   - When uncertain, default to `"neutral"`.

7. **raw_notes** (string)
   - A clean, professional 1-3 sentence summary of the interaction.
   - Include: what was discussed, doctor's response, any commitments made.
   - Do NOT copy the user's message verbatim — rephrase into clinical CRM language.

8. **follow_up_needed** (boolean)
   - `true` if the message mentions any future action: "need to follow up",
     "will call back", "send samples", "schedule another visit", "remind me".
   - `false` otherwise.

9. **follow_up_date** (string | null)
   - If follow_up_needed is true AND a date is mentioned, resolve to `YYYY-MM-DD`.
   - If follow_up_needed is true but no date is given, set to `null`.
   - If follow_up_needed is false, set to `null`.

10. **follow_up_description** (string | null)
    - If follow_up_needed is true, describe the action in one sentence.
    - If follow_up_needed is false, set to `null`.

## EXAMPLES

**Example 1:**
User: "Met Dr. Rivera at her clinic today. We discussed NeuroShield and she's very interested in the phase 3 data. She asked me to send the full study next week."

```json
{{
  "doctor_name": "Dr. Rivera",
  "doctor_id": null,
  "interaction_type": "in-person",
  "interaction_date": "{today}",
  "products_discussed": ["NeuroShield"],
  "sentiment": "positive",
  "raw_notes": "In-person visit with Dr. Rivera at her clinic. Discussed NeuroShield phase 3 clinical data. Dr. Rivera expressed strong interest and requested the full study report.",
  "follow_up_needed": true,
  "follow_up_date": null,
  "follow_up_description": "Send NeuroShield phase 3 full study report to Dr. Rivera."
}}
```

**Example 2:**
User: "Called Dr. Tanaka yesterday about CardioMax. He said he's not convinced by the efficacy data and won't be switching from his current prescription."

```json
{{
  "doctor_name": "Dr. Tanaka",
  "doctor_id": null,
  "interaction_type": "phone",
  "interaction_date": "{{yesterday_date}}",
  "products_discussed": ["CardioMax"],
  "sentiment": "negative",
  "raw_notes": "Phone call with Dr. Tanaka regarding CardioMax. Doctor is unconvinced by the efficacy data and has declined to switch from his current prescription.",
  "follow_up_needed": false,
  "follow_up_date": null,
  "follow_up_description": null
}}
```

## OUTPUT FORMAT

Return ONLY a single JSON object with the fields above.
No markdown fences. No explanation. No preamble.
Just the raw JSON object.
"""


# ──────────────────────────────────────────────────────────────
# Pre-built prompt for simple (no-context) usage.
# For production use, call build_log_interaction_prompt() directly
# to inject doctor_context and dynamic dates.
# ──────────────────────────────────────────────────────────────

LOG_INTERACTION_PROMPT_TEMPLATE = build_log_interaction_prompt("{user_message}")
