# Databricks notebook source
# 03_vector_index.py — Triggers a sync of the embeddings Delta table
# into the Databricks Vector Search index so new chunks become searchable.

dbutils.widgets.text("session_id", "", "Session ID that was just embedded (for logging only)")

session_id = dbutils.widgets.get("session_id")

# COMMAND ----------

import sys
sys.path.append("/Workspace/Repos/grasp-ai")

from agent.vector_store import get_or_create_index, ENDPOINT_NAME, INDEX_NAME, SOURCE_TABLE

# COMMAND ----------

print(f"Syncing index {INDEX_NAME} from source table {SOURCE_TABLE} on endpoint {ENDPOINT_NAME}")

index = get_or_create_index()

# COMMAND ----------

sync_result = index.sync()

print(f"Sync triggered for session_id={session_id}: {sync_result}")

# COMMAND ----------

import time

MAX_WAIT_SECONDS = 300
POLL_INTERVAL = 10
elapsed = 0

while elapsed < MAX_WAIT_SECONDS:
    status = index.describe().get("status", {})
    state = status.get("detailed_state", "UNKNOWN")

    if state in ("ONLINE", "ONLINE_NO_PENDING_UPDATE"):
        print(f"Index is online after {elapsed}s")
        break
    if state in ("OFFLINE_FAILED",):
        raise RuntimeError(f"Vector index sync failed: {status}")

    time.sleep(POLL_INTERVAL)
    elapsed += POLL_INTERVAL
else:
    print(f"Index sync still in progress after {MAX_WAIT_SECONDS}s — continuing without blocking")

# COMMAND ----------

dbutils.notebook.exit(f"OK: index sync triggered for session_id={session_id}, final_state={state}")
