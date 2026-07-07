# GRASP — Project Context File
# Last updated: July 2026

---

## What is Grasp?
AI learning agent built by Harshit Tripathi.
Users upload any document, image, YouTube video or URL.
They get instant summary then chat with AI tutor about it.

**Tagline:** "Upload anything. Grasp everything."
**Goal:** Public product
**Status:** Step 3 in progress — AI engine + backend built, pending mobile app + deploy

---

## Owner
- **Name:** Harshit Tripathi
- **Company:** —

---

## Pricing — Final
- **Free:** 3 uploads/month, summary only
- **Pro:** £5/month — unlimited uploads, all 5 modes, all file types

---

## Input Types
- PDF (books, papers, reports)
- Images (diagrams, screenshots, handwritten notes)
- YouTube URL (transcript extraction)
- Web URL (scrape and summarise)
- Audio/video (meeting recordings — MP3, MP4, WAV, M4A, WEBM)
- Plain text (paste directly)

---

## Modes (5 total)
- **Summary** — auto-generated on upload, TL;DR + key points
- **Analysis** — deep findings, risks, action items, key numbers/dates
- **Q&A** — chat with AI about document, sources shown
- **Teaching** — AI explains like tutor, asks questions, gives feedback
- **Flashcards** — generates revision cards from content

## User Journey (Option C)
Upload → Auto summary loads immediately
       → Persistent chat always available underneath
       → Analysis mode button
       → Teaching mode button
       → Flashcards button

---

## Tech Stack — Final

| Layer | Tool |
|---|---|
| Mobile app | Expo / React Native |
| Backend API | FastAPI (Python) |
| Hosting | Azure Container Apps |
| LLM — Analysis + Teaching | Claude Sonnet 4.6 (Anthropic) |
| LLM — Summary + Q&A | Claude Haiku 4.5 (Anthropic) |
| LLM — Flashcards + Images | Gemini 3 Flash (Google) |
| Audio Transcription | OpenAI Whisper (`whisper-1`) |
| Embeddings | Azure OpenAI text-embedding-3-small |
| Vector Store | Databricks Vector Search |
| Document Storage | Azure Blob Storage (container: grasp-docs) |
| Metadata + Chunks | Delta Lake (Unity Catalog) |
| Auth | Google OAuth  + JWT (access/refresh tokens) |
| Usage Tracking | Azure SQL Database |
| Payments | Stripe (£5/month Pro subscription) |
| PDF Parsing | PyMuPDF |
| Image Parsing | Gemini Vision |
| YouTube | youtube-transcript-api (v1.0+ instance API) |
| Web Scraping | BeautifulSoup + requests |
| Orchestration | Databricks Jobs |
| Tracking | MLflow |
| CI/CD | GitHub Actions → Azure |
| IDE | VS Code + Cursor |

---

## Model Versions — Why They Changed

| Old (May 2026 plan) | New (current) | Reason |
|---|---|---|
| GPT-4o (summary/QA) | Claude Haiku 4.5 | GPT-4o retired from API access Feb 2026 |
| gemini-1.5-flash | Gemini 3 Flash | 1.5 series fully shut down Feb 2026 |
| claude-sonnet-4-6 (unchanged) | claude-sonnet-4-6 | Still current, no change needed |
| google-generativeai SDK | google-genai SDK | Old SDK deprecated, replaced by unified client |

---

## Databricks
```
Catalog:         grasp_catalog
Schema:          grasp_poc
Secret scope:    grasp-secrets
Vector endpoint: grasp-vector-endpoint
```

### Delta Tables
```
grasp_catalog.grasp_poc.documents — raw chunks (written by 01_ingest.py)
grasp_catalog.grasp_poc.embeddings — vectors (written by 02_embed.py)
grasp_catalog.grasp_poc.embeddings_index — Vector Search index (synced by 03_vector_index.py)
grasp_catalog.grasp_poc.sessions — user sessions
```

### Notebooks
```
databricks/notebooks/01_ingest.py — chunk uploaded text, write to documents table
databricks/notebooks/02_embed.py — embed chunks via Azure OpenAI, write to embeddings table
databricks/notebooks/03_vector_index.py — sync embeddings into searchable Vector Search index
databricks/notebooks/04_agent.py — retrieval-augmented Q&A (embed question → search → Claude)
```

---

## Azure Resources
```
Resource Group:  rg-grasp-prod
Blob Storage:    graspstore / container: grasp-docs
Azure OpenAI:    text-embedding-3-small
Azure SQL:       free tier — users + usage tables
Container Apps:  grasp-env (hosts FastAPI)
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
│   ├── main.py ← FastAPI app entry point, CORS, lifespan, routers
│ ├── auth/
│ │   └── dependencies.py ← get_current_user JWT dependency
│ ├── routers/
│ │   ├── upload.py ← file/URL upload endpoints
│ │   ├── agent.py ← summary/analysis/qa/teaching/flashcards
│ │   ├── auth.py ← Google OAuth login + token refresh endpoints
│ │   └── payments.py ← Stripe checkout + webhook endpoints
│ ├── services/
│ │   ├── blob_service.py ← Azure Blob operations
│ │   ├── sql_service.py ← Azure SQL operations (pure data access)
│ │ └── session_store.py ← parsed content lookup by session_id
│ └── models/
│     └── schemas.py ← Pydantic models
├── agent/
│   ├── router.py ← detect input type (youtube vs web)
│   ├── chunker.py ← 500-word chunks, 50-word overlap
│   ├── embedder.py ← Azure OpenAI embeddings
│   ├── vector_store.py ← Databricks Vector Search client
│   ├── llm_router.py ← route to Claude/Gemini + cost estimation
│ ├── parsers/
│ │   ├── pdf_parser.py
│ │   ├── image_parser.py
│ │   ├── youtube_parser.py
│ │   ├── web_parser.py
│ │   └── audio_parser.py
│ ├── modes/
│ │   ├── summary.py
│ │   ├── analysis.py
│ │   ├── qa.py
│ │   ├── teaching.py
│ │   └── flashcards.py
│ └── llms/
│     ├── claude.py
│     ├── openai.py ← Whisper transcription only
│     └── gemini.py
├── auth/
│    ├── google_oauth.py ← Google token verification + JWT issuance
│    ├── usage_tracker.py ← Free tier limit business logic
│    └── stripe_webhook.py ← Stripe event verification + handling
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
├── .gitignore
├── Dockerfile
├── requirements.txt
├── README.md
├── app.py
└── GRASP_CONTEXT.md
```

---

## LLM Routing Logic
```
Analysis mode    → Claude Sonnet 4.6   (best reasoning)
Teaching mode    → Claude Sonnet 4.6   (best reasoning)
Summary          → Claude Haiku 4.5 / Gemini 3 Flash (routed by length)
Q&A              → Claude Haiku 4.5    (reliable, cost-efficient)
Flashcards       → Gemini 3 Flash      (cheap, good enough)
Image parsing    → Gemini 3 Flash      (multimodal, cheapest)
Audio             → Whisper → Claude Haiku 4.5
Embeddings       → Azure OpenAI        (text-embedding-3-small)
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
Step 0 — Setup + accounts + structure ✅ DONE
Step 1 — Azure + Databricks infrastructure ✅ DONE
Step 2 — FastAPI backend (auth/upload/usage/Stripe) ✅ DONE
Step 3 — AI engine (parse/embed/agent/5 modes) ✅ DONE
Step 4 — Expo mobile app (all screens) 🔲 NOT STARTED
Step 5 — Deploy + ship (Azure + Expo Go link) 🔲 NOT STARTED
```

---

## Known Gaps / Next Priorities
```
Mobile app screens not built yet (Step 4)

qa.py still uses truncate-and-stuff approach for context, not yet wired to the retrieval pipeline (chunker → embedder → vector_store) that 04_agent.py demonstrates — this is the highest-value upgrade

Scanned/image-only PDFs have no OCR fallback (pdf_parser.py flags likely_scanned but nothing consumes it yet)

Web scraping has no headless browser fallback for JS-heavy sites

Whisper's long-term replacement path is unresolved industry-wide; monitor for updates before this becomes a bigger issue

Refresh token rotation not implemented (flagged as future security upgrade)
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
   FILE: [which file]
   ERROR: [exact error]
   WHAT I DID: [what you ran]
