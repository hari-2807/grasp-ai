from agent.llms import claude
from agent.llm_router import estimate_cost_gbp

_SYSTEM = """You are a sharp analyst. Read the content and return structured insights.

Format your response exactly like this:

**What Is This**
One sentence — document type and what it's about.

**Key Findings**
• Most important finding
• Second finding
• Third finding (up to 5)

**Risks or Red Flags**
• Any concerns, problems, or things to watch out for
• (Write "None identified" if nothing stands out)

**Action Items**
• Things a reader should do or follow up on
• (Write "None" if not applicable)

**Key Numbers & Dates**
• Important figures, amounts, deadlines, dates mentioned
• (Write "None" if not applicable)

Rules:
- Be precise and specific — quote actual numbers and names from the document
- Flag anything unusual, contradictory, or missing
- Keep each bullet tight — one clear point per bullet"""

MODEL_ID = "claude-sonnet-4-6"
MAX_CHARS = 150000


def run(content: dict, anthropic_key: str = None) -> dict:
    """Run deep analysis on content using Claude Sonnet."""
    full_text = content["text"]
    text = full_text[:MAX_CHARS]
    was_truncated = len(full_text) > MAX_CHARS

    try:
        result = claude.complete(
            system=_SYSTEM,
            user=f"Analyse this:\n\n{text}",
            model=MODEL_ID,
            max_tokens=1200,
            api_key=anthropic_key,
        )
    except Exception as e:
        return {
            "output": "Analysis failed — please try again.",
            "error": str(e),
            "model": "Claude Sonnet",
            "model_id": MODEL_ID,
            "cost_gbp": 0,
            "truncated": was_truncated,
        }

    cost = estimate_cost_gbp(MODEL_ID, result["input_tokens"], result["output_tokens"])

    return {
        "output": result["text"],
        "model": "Claude Sonnet",
        "model_id": MODEL_ID,
        "cost_gbp": cost,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "truncated": was_truncated,
    }
