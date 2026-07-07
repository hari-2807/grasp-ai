# Databricks notebook source
# 02_embed.py — Reads newly ingested chunks from the documents table,
# embeds them via Azure OpenAI, and writes vectors into the embeddings table.

dbutils.widgets.text("session_id", "", "Session ID to embed")

session_id = dbutils.widgets.get("session_id")

# COMMAND ----------

import sys
sys.path.append("/Workspace/Repos/grasp-ai")

from agent.embedder import embed_chunks

# COMMAND ----------

CATALOG = "grasp_catalog"
SCHEMA = "grasp_poc"
DOCUMENTS_TABLE = f"{CATALOG}.{SCHEMA}.documents"
EMBEDDINGS_TABLE = f"{CATALOG}.{SCHEMA}.embeddings"

secret_scope = "grasp-secrets"
azure_key = dbutils.secrets.get(scope=secret_scope, key="azure-openai-key")
azure_endpoint = dbutils.secrets.get(scope=secret_scope, key="azure-openai-endpoint")

# COMMAND ----------

chunks_df = spark.table(DOCUMENTS_TABLE).filter(f"session_id = '{session_id}'")

if chunks_df.count() == 0:
    dbutils.notebook.exit(f"No chunks found for session_id={session_id} — nothing to embed")

# COMMAND ----------

existing_ids = set(
    row["chunk_id"]
    for row in spark.table(EMBEDDINGS_TABLE)
    .filter(f"session_id = '{session_id}'")
    .select("chunk_id")
    .collect()
) if spark.catalog.tableExists(EMBEDDINGS_TABLE) else set()

chunks_pd = chunks_df.toPandas()
chunks_pd = chunks_pd[~chunks_pd["chunk_id"].isin(existing_ids)]

if chunks_pd.empty:
    dbutils.notebook.exit(f"All chunks for session_id={session_id} already embedded — skipping")

# COMMAND ----------

chunk_dicts = [
    {
        "chunk_index": row["chunk_index"],
        "text": row["text"],
        "word_count": row["word_count"],
        "start_word": row["start_word"],
        "end_word": row["end_word"],
    }
    for _, row in chunks_pd.iterrows()
]

embedded = embed_chunks(chunk_dicts, api_key=azure_key, endpoint=azure_endpoint)

# COMMAND ----------

from pyspark.sql import Row
from datetime import datetime

rows = []
failed_count = 0

for chunk_id, chunk, meta in zip(chunks_pd["chunk_id"], embedded, chunks_pd.itertuples()):
    if chunk.get("embedding") is None:
        failed_count += 1
        continue
    rows.append(
        Row(
            chunk_id=chunk_id,
            session_id=session_id,
            text=chunk["text"],
            embedding=chunk["embedding"],
            start_word=chunk["start_word"],
            end_word=chunk["end_word"],
            model=chunk.get("model", "text-embedding-3-small"),
            embedded_at=datetime.utcnow(),
        )
    )

if not rows:
    dbutils.notebook.exit(f"All embeddings failed for session_id={session_id}")

df = spark.createDataFrame(rows)

# COMMAND ----------

df.write.format("delta").mode("append").saveAsTable(EMBEDDINGS_TABLE)

print(f"Embedded {len(rows)} chunks ({failed_count} failed) for session_id={session_id}")

# COMMAND ----------

dbutils.notebook.exit(f"OK: {len(rows)} embedded, {failed_count} failed")
