from agent.llms import claude
from agent.llm_router import estimate_cost_gbp

MODEL_ID = "claude-sonnet-4-6"
MAX_CHARS = 100000

_SYSTEM_TEMPLATE = """You are a patient, encouraging tutor teaching the user about the content below.

Use the Socratic method: instead of just explaining everything, ask guiding questions that help
the user reach understanding themselves. Give hints before giving answers. Check understanding
before moving on. Adapt difficulty based on how the user responds.

If the user seems stuck or asks directly for the answer, explain clearly then check they understood
with a follow-up question.

Keep responses focused — a few sentences or one question at a time, not a lecture.

--- CONTENT START ---
{content}
--- CONTENT END ---"""


def run(content: dict, message: str, history: list = None, anthropic_key: str = None) -> dict:
    """Run a Socratic tutoring session on the content."""
    history = history or []
    full_text = content["text"]
    text = full_text[:MAX_CHARS]
    was_truncated = len(full_text) > MAX_CHARS

    system = _SYSTEM_TEMPLATE.format(content=text)
    messages = history + [{"role": "user", "content": message}]

    try:
        result = claude.chat(
            system=system,
            messages=messages,
            model=MODEL_ID,
            max_tokens=700,
            api_key=anthropic_key,
        )
    except Exception as e:
        return {
            "output": "Couldn't continue the session — please try again.",
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


def start_session(content: dict, anthropic_key: str = None) -> dict:
    """Kick off a new teaching session with an opening question about the content."""
    opener = "Let's begin. Based on this content, what would you like to understand better, or should I pick where we start?"
    return run(content, opener, history=[], anthropic_key=anthropic_key)
