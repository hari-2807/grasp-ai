# Databricks notebook source
# 01_ingest.py — Reads newly uploaded documents from Blob Storage,
# chunks them, and writes raw chunks into the Delta table for embedding.

dbutils.widgets.text("session_id", "", "Session ID to ingest")
dbutils.widgets.text("blob_path", "", "Blob path of uploaded document")

session_id = dbutils.widgets.get("session_id")
blob_path = dbutils.widgets.get("blob_path")

# COMMAND ----------

import sys
sys.path.append("/Workspace/Repos/grasp-ai")

from agent.chunker import chunk_text
from api.services.blob_service import download_document
from api.services.session_store import get_session

# COMMAND ----------

CATALOG = "grasp_catalog"
SCHEMA = "grasp_poc"
DOCUMENTS_TABLE = f"{CATALOG}.{SCHEMA}.documents"

secret_scope = "grasp-secrets"

# COMMAND ----------

content = get_session(session_id)
if content is None:
    raise ValueError(f"No session found for session_id={session_id}")

full_text = content["text"]
source_type = content.get("source_type", "unknown")
title = content.get("title", "Untitled")

# COMMAND ----------

chunks = chunk_text(full_text, chunk_size=500, overlap=50)

if not chunks:
    dbutils.notebook.exit(f"No chunks produced for session_id={session_id} — document may be empty")

# COMMAND ----------

from pyspark.sql import Row
from datetime import datetime

rows = [
    Row(
        chunk_id=f"{session_id}_{c['chunk_index']}",
        session_id=session_id,
        title=title,
        source_type=source_type,
        chunk_index=c["chunk_index"],
        text=c["text"],
        word_count=c["word_count"],
        start_word=c["start_word"],
        end_word=c["end_word"],
        ingested_at=datetime.utcnow(),
    )
    for c in chunks
]

df = spark.createDataFrame(rows)

# COMMAND ----------

df.write.format("delta").mode("append").saveAsTable(DOCUMENTS_TABLE)

print(f"Ingested {len(rows)} chunks for session_id={session_id} into {DOCUMENTS_TABLE}")

# COMMAND ----------

dbutils.notebook.exit(f"OK: {len(rows)} chunks ingested")
