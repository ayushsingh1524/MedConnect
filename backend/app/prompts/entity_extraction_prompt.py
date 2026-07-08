"""
Entity Extraction Prompt — Named Entity Recognition for CRM
=============================================================

PURPOSE:
    General-purpose entity extraction from any user message or raw text
    within the MedConnect CRM. Unlike the log_interaction_prompt (which
    extracts a fixed schema for logging), this prompt identifies and
    classifies ALL named entities in a piece of text.

    Use cases:
    - Enriching raw interaction notes with structured entity tags.
    - Powering the search/autocomplete: "find interactions about CardioMax"
      → extract product entity → filter by product.
    - Pre-processing chat messages to resolve doctor references before
      tool calls (e.g., "I saw Dr. Patel" → resolve to doctor_id).
    - Detecting product mentions for analytics dashboards.

MODEL TARGET:
    Groq gemma2-9b-it — Entity extraction is one of the strongest
    capabilities of instruction-tuned models at this size. The prompt
    uses a strict taxonomy with definitions and examples per entity type
    to minimise misclassification.

DESIGN NOTES:
    - The entity taxonomy is pharmaceutical-CRM specific, not generic NER.
    - Each entity type has positive AND negative examples to reduce
      false positives (e.g., "Dr. Pepper" is not a doctor).
    - Confidence scoring is included so downstream consumers can filter
      low-confidence extractions.
    - Coreference hints help with pronouns ("she", "he", "the doctor").
"""


def build_entity_extraction_prompt(
    text: str,
    known_doctors: list[dict] = None,
    known_products: list[str] = None,
) -> str:
    """
    Build a prompt to extract named entities from arbitrary CRM text.

    Args:
        text: The raw text to extract entities from.
        known_doctors: Optional list of dicts with known doctor info,
                       e.g. [{"id": "uuid", "name": "Dr. Smith", "specialty": "Cardiology"}].
                       Helps the model resolve ambiguous references.
        known_products: Optional list of known product names in the company portfolio.
                        Helps distinguish product names from general nouns.

    Returns:
        A formatted prompt string ready for LLM invocation with JSON mode.
    """

    # Build optional context sections
    doctor_context = ""
    if known_doctors:
        doctor_lines = "\n".join(
            f'  - "{d["name"]}" (ID: {d["id"]}, Specialty: {d.get("specialty", "N/A")})'
            for d in known_doctors[:20]  # Cap at 20 to stay within context limits
        )
        doctor_context = f"""
KNOWN DOCTORS IN TERRITORY:
{doctor_lines}

When a name in the text matches or closely resembles a known doctor, use their exact name and ID.
"""

    product_context = ""
    if known_products:
        product_list = ", ".join(f'"{p}"' for p in known_products[:30])
        product_context = f"""
KNOWN PRODUCT PORTFOLIO:
{product_list}

Prioritise matching against these known products. If a word closely resembles a known product (e.g., "cardio max" → "CardioMax"), normalise to the known spelling.
"""

    return f"""You are a pharmaceutical CRM entity extraction system. Your task is to identify and classify every named entity in the text below.
{doctor_context}{product_context}
## INPUT TEXT
\"\"\"{text}\"\"\"

## ENTITY TAXONOMY

Extract entities into these categories:

### 1. PERSON (Doctors / HCPs)
**What to extract:** Names of healthcare professionals mentioned.
**Format:** Include title (Dr., Prof.) if present.
**Examples:**
  ✅ "Dr. Sarah Jenkins" → PERSON
  ✅ "Professor Chen" → PERSON
  ✅ "the cardiologist Dr. Rivera" → PERSON (name: "Dr. Rivera")
**Not entities:**
  ❌ "the doctor" (pronoun, not a named entity — but note in coreferences)
  ❌ "Dr. Pepper" (brand, not a person)

### 2. PRODUCT (Pharmaceutical products / drugs)
**What to extract:** Brand names, generic drug names, compound names.
**Format:** Normalise to Title Case.
**Examples:**
  ✅ "CardioMax" → PRODUCT
  ✅ "atorvastatin" → PRODUCT
  ✅ "NeuroShield 50mg" → PRODUCT (name: "NeuroShield", dosage: "50mg")
**Not entities:**
  ❌ "samples" (generic noun)
  ❌ "medication" (category, not a specific product)

### 3. ORGANIZATION (Hospitals, clinics, institutions)
**What to extract:** Named healthcare facilities, universities, pharma companies.
**Examples:**
  ✅ "Mount Sinai Hospital" → ORGANIZATION
  ✅ "Cleveland Clinic" → ORGANIZATION
  ✅ "Pfizer" → ORGANIZATION
**Not entities:**
  ❌ "the hospital" (generic reference)
  ❌ "her clinic" (unresolved possessive)

### 4. DATE_TIME (Dates, times, temporal references)
**What to extract:** Any temporal expression, resolved to ISO format when possible.
**Examples:**
  ✅ "July 8, 2026" → DATE_TIME (resolved: "2026-07-08")
  ✅ "next Tuesday" → DATE_TIME (resolved: relative, note the reference)
  ✅ "3pm" → DATE_TIME
  ✅ "Q3 2026" → DATE_TIME

### 5. MEDICAL_TERM (Clinical terms, conditions, procedures)
**What to extract:** Disease names, therapeutic areas, clinical procedures, trial phases.
**Examples:**
  ✅ "type 2 diabetes" → MEDICAL_TERM
  ✅ "phase 3 trial" → MEDICAL_TERM
  ✅ "coronary artery disease" → MEDICAL_TERM
**Not entities:**
  ❌ "health" (too generic)

### 6. SENTIMENT_SIGNAL (Phrases indicating doctor's attitude)
**What to extract:** Key phrases that reveal the doctor's sentiment toward a product or topic.
**Examples:**
  ✅ "very receptive" → SENTIMENT_SIGNAL (valence: positive)
  ✅ "expressed concerns about side effects" → SENTIMENT_SIGNAL (valence: negative)
  ✅ "asked for more data" → SENTIMENT_SIGNAL (valence: neutral)

## OUTPUT FORMAT

Return a JSON object with this exact structure:

{{
  "entities": [
    {{
      "text": "<exact text span from the input>",
      "type": "<PERSON | PRODUCT | ORGANIZATION | DATE_TIME | MEDICAL_TERM | SENTIMENT_SIGNAL>",
      "normalized": "<cleaned / normalized form of the entity>",
      "confidence": <float 0.0 to 1.0>,
      "metadata": {{
        // Type-specific metadata. Include only relevant fields:
        // PERSON: "title", "specialty" (if inferrable), "doctor_id" (if matched to known)
        // PRODUCT: "dosage" (if mentioned)
        // DATE_TIME: "resolved" (ISO date if resolvable)
        // SENTIMENT_SIGNAL: "valence" ("positive" | "neutral" | "negative")
      }}
    }}
  ],
  "coreferences": [
    {{
      "pronoun": "<e.g., 'she', 'he', 'the doctor'>",
      "refers_to": "<the entity it most likely refers to, or null if unresolvable>"
    }}
  ],
  "summary": {{
    "person_count": <int>,
    "product_count": <int>,
    "overall_sentiment": "<positive | neutral | negative | mixed>"
  }}
}}

## RULES

1. Extract ALL entities — do not skip any, even if low confidence.
2. Set confidence < 0.5 for ambiguous extractions rather than omitting them.
3. If a word could be two types (e.g., a brand that's also a medical term), pick the most likely and note the alternative in metadata.
4. The `coreferences` array helps resolve pronouns. If "she" appears after "Dr. Rivera", link them.
5. `overall_sentiment` in the summary should reflect the dominant sentiment signal. If signals conflict, use "mixed".

Return ONLY the JSON object. No markdown fences, no explanation.
"""


# ──────────────────────────────────────────────────────────────
# Convenience export: a simple template for basic usage without
# doctor/product context injection. For production, call
# build_entity_extraction_prompt() directly.
# ──────────────────────────────────────────────────────────────

ENTITY_EXTRACTION_PROMPT_TEMPLATE = (
    "Extract all named entities from the following text and return structured JSON.\n\n"
    "Text: {text}\n\n"
    "Return a JSON object with 'entities' (list of objects with text, type, normalized, confidence, metadata), "
    "'coreferences' (pronoun resolution), and 'summary' (counts and overall_sentiment)."
)
