# Databricks notebook source
# 04_agent.py — Retrieval-augmented Q&A: embeds a user's question,
# retrieves the most relevant chunks from Vector Search, and asks Claude.

dbutils.widgets.text("session_id", "", "Session ID to query")
dbutils.widgets.text("question", "", "User's question")

session_id = dbutils.widgets.get("session_id")
question = dbutils.widgets.get("question")

# COMMAND ----------

import sys
sys.path.append("/Workspace/Repos/grasp-ai")

from agent.embedder import embed_query
from agent.vector_store import search
from agent.llms import claude

# COMMAND ----------

secret_scope = "grasp-secrets"
azure_key = dbutils.secrets.get(scope=secret_scope, key="azure-openai-key")
azure_endpoint = dbutils.secrets.get(scope=secret_scope, key="azure-openai-endpoint")
anthropic_key = dbutils.secrets.get(scope=secret_scope, key="anthropic-api-key")

# COMMAND ----------

if not question.strip():
    dbutils.notebook.exit("No question provided")

query_embedding = embed_query(question, api_key=azure_key, endpoint=azure_endpoint)

# COMMAND ----------

TOP_K = 5

retrieved_chunks = search(session_id, query_embedding, num_results=TOP_K)

valid_chunks = [c for c in retrieved_chunks if c.get("text") and not c.get("error")]

if not valid_chunks:
    dbutils.notebook.exit(f"No relevant chunks found for session_id={session_id}")

# COMMAND ----------

sorted_chunks = sorted(valid_chunks, key=lambda c: c.get("start_word", 0))
context = "\n\n---\n\n".join(c["text"] for c in sorted_chunks)

# COMMAND ----------

MODEL_ID = "claude-haiku-4-5"

system = f"""You are answering a question about a specific document using only the excerpts below.

If the answer isn't in these excerpts, say so clearly — don't make things up.
Keep answers short and direct.

--- RELEVANT EXCERPTS ---
{context}
--- END EXCERPTS ---"""

result = claude.complete(
    system=system,
    user=question,
    model=MODEL_ID,
    max_tokens=600,
    api_key=anthropic_key,
)

# COMMAND ----------

print(f"Question: {question}")
print(f"Retrieved {len(valid_chunks)} chunks")
print(f"Answer: {result['text']}")

# COMMAND ----------

dbutils.notebook.exit(result["text"])
