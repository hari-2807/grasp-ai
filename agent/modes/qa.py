from agent.llms import claude
from agent.llm_router import estimate_cost_gbp

MODEL_ID = "claude-haiku-4-5"
MAX_CHARS = 100000
MAX_HISTORY_TURNS = 10

_SYSTEM_TEMPLATE = """You are answering questions about a specific piece of content the user uploaded to Grasp.

Only answer using the content below. If the answer isn't in the content, say so clearly — don't make things up.

Keep answers short and direct. Reference specific parts of the content when useful.

--- CONTENT START ---
{content}
--- CONTENT END ---"""


def run(content: dict, question: str, history: list = None, anthropic_key: str = None) -> dict:
    """Answer a question about the content, using prior chat turns for context."""
    history = history or []
    full_text = content["text"]
    text = full_text[:MAX_CHARS]
    was_truncated = len(full_text) > MAX_CHARS

    recent_history = history[-(MAX_HISTORY_TURNS * 2):]

    system = _SYSTEM_TEMPLATE.format(content=text)
    messages = recent_history + [{"role": "user", "content": question}]

    try:
        result = claude.chat(
            system=system,
            messages=messages,
            model=MODEL_ID,
            max_tokens=600,
            api_key=anthropic_key,
        )
    except Exception as e:
        return {
            "output": "Couldn't answer that — please try again.",
            "error": str(e),
            "model": "Claude Haiku",
            "model_id": MODEL_ID,
            "cost_gbp": 0,
            "truncated": was_truncated,
        }

    cost = estimate_cost_gbp(MODEL_ID, result["input_tokens"], result["output_tokens"])

    return {
        "output": result["text"],
        "model": "Claude Haiku",
        "model_id": MODEL_ID,
        "cost_gbp": cost,
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],        
        "truncated": was_truncated,
    }
