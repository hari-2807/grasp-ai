# GRASP — Project Context File
# Last updated: May 2026

---

## What is Grasp?
AI learning agent built by Harshit Tripathi under Britcore AI.
Users upload any document, image, YouTube video or URL.
They get instant summary then chat with AI tutor about it.

**Tagline:** "Upload anything. Grasp everything."
**Goal:** Public product, Britcore AI portfolio, Global Talent Visa evidence
**Status:** Step 0 complete — moving to Step 1

---

## Owner
- **Name:** Harshit Tripathi
- **Company:** Britcore AI
- **Background:** Lead Data Engineer, Boots UK. 9 years. Databricks Certified.
- **Goal:** Global Talent Visa (Exceptional Talent) + 20 Agents in 30 Days

---

## Pricing — Final
- **Free:** 3 uploads/month, summary only
- **Pro:** £5/month — unlimited uploads, all 4 modes, all file types

---

## Input Types
- PDF (books, papers, reports)
- Images (diagrams, screenshots, handwritten notes)
- YouTube URL (transcript extraction)
- Web URL (scrape and summarise)
- Plain text (paste directly)

---

## Modes (4 total)
- **Summary** — auto-generated on upload, TL;DR + key points
- **Q&A** — chat with AI about document, sources shown
- **Teaching** — AI explains like tutor, asks questions, gives feedback
- **Flashcards** — generates revision cards from content

## User Journey (Option C)
Upload → Auto summary loads immediately
       → Persistent chat always available underneath
       → Teaching mode button
       → Flashcards button

---

## Tech Stack — Final

| Layer | Tool |
|---|---|
| Mobile app | Expo / React Native |
| Backend API | FastAPI (Python) |
| Hosting | Azure Container Apps |
| LLM — Teaching | Claude Sonnet (Anthropic) |
| LLM — Summary + Q&A | GPT-4o (OpenAI) |
| LLM — Flashcards + Images | Gemini Flash (Google) |
| Embeddings | Azure OpenAI text-embedding-3-small |
| Vector Store | Databricks Vector Search |
| Document Storage | Azure Blob Storage (container: grasp-docs) |
| Metadata + Chunks | Delta Lake (Unity Catalog) |
| Auth | Google OAuth |
| Usage Tracking | Azure SQL Database |
| Payments | Stripe (£5/month Pro) |
| PDF Parsing | PyMuPDF |
| Image Parsing | Gemini Flash Vision |
| YouTube | youtube-transcript-api |
| Web Scraping | BeautifulSoup + requests |
| Orchestration | Databricks Jobs |
| Tracking | MLflow |
| CI/CD | GitHub Actions → Azure |
| IDE | VS Code + Cursor |

---

## Databricks — Britcore Workspace
```
Catalog:        britcore_catalog
Schema:         grasp_poc
Secret scope:   grasp-secrets
```

### Delta Tables
```
britcore_catalog.grasp_poc.documents     — raw chunks
britcore_catalog.grasp_poc.embeddings    — vectors
britcore_catalog.grasp_poc.sessions      — user sessions
```

### Notebooks
```
databricks/notebooks/01_ingest.py
databricks/notebooks/02_embed.py
databricks/notebooks/03_vector_index.py
databricks/notebooks/04_agent.py
```

---

## Azure Resources
```
Resource Group:         rg-grasp-prod
Blob Storage:           graspstore / container: grasp-docs
Azure OpenAI:           text-embedding-3-small
Azure SQL:              free tier — users + usage tables
Container Apps:         grasp-env (hosts FastAPI)
```

### Azure SQL Schema
```sql
CREATE TABLE users (
    user_id         VARCHAR(255) PRIMARY KEY,
    email           VARCHAR(255),
    created_at      DATETIME,
    tier            VARCHAR(50),
    stripe_id       VARCHAR(255)
);

CREATE TABLE usage (
    id              INT IDENTITY PRIMARY KEY,
    user_id         VARCHAR(255),
    action          VARCHAR(100),
    timestamp       DATETIME,
    month_year      VARCHAR(20)
);
```

---

## Project Structure
```
grasp-ai/
├── api/
│   ├── main.py                     ← FastAPI app entry point
│   ├── routers/
│   │   ├── upload.py               ← file upload endpoints
│   │   ├── agent.py                ← summary/qa/teaching/flashcards
│   │   ├── auth.py                 ← Google OAuth endpoints
│   │   └── payments.py             ← Stripe endpoints
│   ├── services/
│   │   ├── blob_service.py         ← Azure Blob operations
│   │   └── sql_service.py          ← Azure SQL operations
│   └── models/
│       └── schemas.py              ← Pydantic models
├── agent/
│   ├── router.py                   ← detect input type
│   ├── chunker.py                  ← 500-word chunks, 50-word overlap
│   ├── embedder.py                 ← Azure OpenAI embeddings
│   ├── vector_store.py             ← Databricks Vector Search
│   ├── llm_router.py               ← route to Claude/GPT/Gemini
│   ├── parsers/
│   │   ├── pdf_parser.py
│   │   ├── image_parser.py
│   │   ├── youtube_parser.py
│   │   └── web_parser.py
│   ├── modes/
│   │   ├── summary.py
│   │   ├── qa.py
│   │   ├── teaching.py
│   │   └── flashcards.py
│   └── llms/
│       ├── claude.py
│       ├── openai.py
│       └── gemini.py
├── auth/
│   ├── google_oauth.py
│   ├── usage_tracker.py
│   └── stripe_webhook.py
├── databricks/
│   └── notebooks/
│       ├── 01_ingest.py
│       ├── 02_embed.py
│       ├── 03_vector_index.py
│       └── 04_agent.py
├── mobile/
│   ├── screens/
│   ├── components/
│   └── navigation/
├── .github/workflows/deploy.yml
├── .env.example
├── .cursorrules
├── Dockerfile
├── requirements.txt
├── README.md
└── GRASP_CONTEXT.md
```

---

## LLM Routing Logic
```python
Teaching mode    → Claude Sonnet  (best reasoning)
Summary          → GPT-4o         (fast, structured)
Q&A              → GPT-4o         (reliable)
Flashcards       → Gemini Flash   (cheap, good enough)
Image parsing    → Gemini Flash   (multimodal, cheapest)
Embeddings       → Azure OpenAI   (text-embedding-3-small)
```

---

## Design
```
Theme:          Dark, mobile first
Primary:        #6C63FF  (purple)
Accent:         #00D4AA  (teal)
Background:     #0A0A0F
Surface:        #13131A
Text:           #FFFFFF / #8B8BA7
```

---

## 5 Steps Plan
```
Step 0  — Setup + accounts + structure         ✅ DONE
Step 1  — Azure + Databricks infrastructure
Step 2  — FastAPI backend (auth/upload/usage/Stripe)
Step 3  — AI engine (parse/embed/agent/4 modes)
Step 4  — Expo mobile app (all screens)
Step 5  — Deploy + ship (Azure + Expo Go link)
```

---

## Launch Plan
```
Phase 1  — Testing (Month 1)
           100 students via Expo Go, all free
           Collect feedback, fix bugs

Phase 2  — Pricing (Month 2)
           Introduce £5/month Pro
           Target 20% conversion = £100/month

Phase 3  — App Store (Month 2-3)
           Apple Developer £80/year
           Google Play £20 once
```

---

## How to Use This File
1. Paste entire file at start of every new Claude chat
2. One chat per step
3. Error template:
   STEP: [which step]
   FILE: [which file]
   ERROR: [exact error]
   WHAT I DID: [what you ran]
