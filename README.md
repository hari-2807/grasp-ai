<div align="center">

# 🧠 Grasp

### Upload anything. Understand everything.

Drop a PDF, paste a link, upload an image, or record your meeting.  
Get a short, clear summary — powered by the right AI model at the right cost.

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Claude](https://img.shields.io/badge/Claude-Sonnet%20%2F%20Haiku-8B5CF6?style=flat-square)](https://anthropic.com)
[![Gemini](https://img.shields.io/badge/Gemini-Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://deepmind.google/gemini)
[![Whisper](https://img.shields.io/badge/Whisper-OpenAI-412991?style=flat-square)](https://openai.com/research/whisper)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/harshitboots/grasp-ai?style=flat-square&color=yellow)](https://github.com/harshitboots/grasp-ai/stargazers)

<br/>

**[🚀 Quick Start](#quick-start) · [🔀 LLM Router](#llm-router) · [📥 Inputs](#input-types) · [🎛️ Modes](#modes) · [🏗️ Architecture](#architecture) · [🗺️ Roadmap](#roadmap)**

</div>

---

## What is Grasp?

Most people don't have time to read everything thrown at them — long PDFs, hour-long YouTube videos, dense articles, meeting recordings.

Grasp solves that. Point it at any content and get back what matters in plain English.

```
You give Grasp →    A YouTube link       A PDF report      A photo of notes      A meeting recording
Grasp gives you →   Clear summary        Key findings       Extracted content      Action items
```

No reading required. No manual highlighting. No copy-paste into ChatGPT.

---

## Quick Start

### Prerequisites

- Python 3.10+
- At least one API key: [Anthropic](https://console.anthropic.com) · [Google AI](https://aistudio.google.com) · [OpenAI](https://platform.openai.com) (for meeting transcription)

### 1. Clone

```bash
git clone https://github.com/harshitboots/grasp-ai.git
cd grasp-ai
```

### 2. Create virtual environment

```bash
python -m venv venv

# Mac / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

```bash
cp .env.example .env
# Edit .env and add your keys
```

```env
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-...      # only needed for meeting transcription
```

### 5. Run

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

> You can also paste API keys directly in the sidebar — no `.env` file needed.

---

## Input Types

| Input | What you give it | How it works |
|-------|-----------------|--------------|
| **🔗 URL** | Any web article, blog, or docs page | BeautifulSoup scrapes and cleans the text |
| **▶️ YouTube** | Any YouTube link | `youtube-transcript-api` extracts the transcript |
| **📄 PDF** | Upload any PDF file | PyMuPDF extracts all text and metadata |
| **🖼️ Image** | Photo, screenshot, diagram, handwritten notes | Gemini Flash Vision reads and extracts content |
| **🎙️ Meeting** | MP3, MP4, WAV, M4A, WEBM recording | OpenAI Whisper transcribes the audio |

---

## Modes

| Mode | What it gives you | Model |
|------|------------------|-------|
| **Summary** | TL;DR + key bullet points in plain English | Routed (Flash / Haiku) |
| **Analysis** | Findings, risks, action items, key data | Claude Sonnet |
| **Q&A** *(coming soon)* | Chat with the content, sources shown | Claude Haiku |
| **Teaching** *(coming soon)* | AI tutor that asks you questions and gives feedback | Claude Sonnet |
| **Flashcards** *(coming soon)* | Revision cards generated from the content | Gemini Flash |

---

## LLM Router

The router picks the **cheapest model that can do the job** — no manual selection, no wasted spend.

```
Input content + mode
        ↓
┌────────────────────────────────────────────────┐
│              Router Decision                    │
│                                                │
│  image?          → Gemini Flash  (vision)      │
│  audio?          → Whisper → Claude Haiku      │
│  analysis mode?  → Claude Sonnet               │
│  words < 2,000?  → Gemini Flash                │
│  words < 8,000?  → Claude Haiku                │
│  words > 8,000?  → Claude Haiku + chunking     │
└────────────────────────────────────────────────┘
```

### Pricing per run

| Content | Model | Estimated cost |
|---------|-------|----------------|
| Short article summary | Gemini Flash | ~£0.0001 |
| Long PDF summary | Claude Haiku | ~£0.0005 |
| Deep document analysis | Claude Sonnet | ~£0.003 |
| Meeting transcription + summary | Whisper + Haiku | ~£0.006/min |

Cost is shown after every run in the UI.

---

## Architecture

```
User input (URL / PDF / Image / Audio)
              ↓
      ┌───────────────┐
      │  URL Detector  │  ← youtube or web?
      └───────┬───────┘
              ↓
   ┌──────────────────────┐
   │       Parsers         │
   │  web · youtube · pdf  │
   │  image · audio        │
   └──────────┬───────────┘
              ↓
   ┌──────────────────────┐
   │      LLM Router       │  ← Flash / Haiku / Sonnet
   └──────────┬───────────┘
              ↓
   ┌──────────────────────┐
   │     Mode Engine       │
   │  summary · analysis   │
   │  qa · teaching · cards│
   └──────────┬───────────┘
              ↓
     Output + cost shown
```

---

## Project Structure

```
grasp-ai/
├── app.py                          ← Streamlit web UI
├── agent/
│   ├── router.py                   ← YouTube vs web detection
│   ├── llm_router.py               ← model selection (Flash / Haiku / Sonnet)
│   ├── parsers/
│   │   ├── web_parser.py           ← BeautifulSoup scraper
│   │   ├── youtube_parser.py       ← transcript extraction
│   │   ├── pdf_parser.py           ← PyMuPDF text extraction
│   │   ├── image_parser.py         ← Gemini Vision
│   │   └── audio_parser.py         ← OpenAI Whisper
│   ├── modes/
│   │   ├── summary.py              ← TL;DR + key points
│   │   ├── analysis.py             ← deep analysis (Claude Sonnet)
│   │   ├── qa.py                   ← chat with content
│   │   ├── teaching.py             ← Socratic tutor
│   │   └── flashcards.py           ← revision cards
│   └── llms/
│       ├── claude.py               ← Anthropic SDK wrapper
│       ├── gemini.py               ← Google Gemini SDK wrapper
│       └── openai.py               ← OpenAI SDK wrapper
├── api/
│   ├── main.py                     ← FastAPI backend (in progress)
│   ├── routers/                    ← upload / agent / auth / payments
│   └── services/                   ← blob storage / SQL
├── auth/
│   ├── google_oauth.py
│   ├── usage_tracker.py
│   └── stripe_webhook.py
├── databricks/notebooks/           ← ingest / embed / vector index / agent
├── .streamlit/config.toml          ← dark purple theme
├── .env.example
├── Dockerfile
└── requirements.txt
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Web UI | Streamlit |
| Backend API | FastAPI |
| LLM — Analysis / Teaching | Claude Sonnet (`claude-sonnet-4-6`) |
| LLM — Summary / Q&A | Claude Haiku (`claude-haiku-4-5`) |
| LLM — Flashcards / Images | Gemini Flash (`gemini-1.5-flash`) |
| Meeting Transcription | OpenAI Whisper (`whisper-1`) |
| Embeddings | Azure OpenAI `text-embedding-3-small` |
| Vector Store | Databricks Vector Search |
| Document Storage | Azure Blob Storage |
| Metadata | Delta Lake (Unity Catalog) |
| Auth | Google OAuth |
| Payments | Stripe |
| PDF Parsing | PyMuPDF |
| Web Scraping | BeautifulSoup + requests |
| Language | Python 3.10+ |
| Hosting | Azure Container Apps |
| CI/CD | GitHub Actions |

---

## Roadmap

### Web version (current)
- [x] URL scraping (articles, blogs, docs)
- [x] YouTube transcript extraction
- [x] PDF parsing
- [x] Image reading (Gemini Vision)
- [x] Meeting / audio transcription (Whisper)
- [x] Summary mode
- [x] Deep analysis mode
- [x] Multi-model router (Flash / Haiku / Sonnet)
- [ ] Q&A mode — chat with any content
- [ ] Teaching mode — Socratic AI tutor
- [ ] Flashcards mode — revision cards from any content
- [ ] Google OAuth + usage tracking
- [ ] Free tier (3 uploads/month) + Pro (£5/month)
- [ ] Streamlit Cloud deployment

### Mobile app
- [ ] Expo / React Native app
- [ ] FastAPI backend
- [ ] Stripe payments
- [ ] App Store + Google Play

---

## Environment Variables

| Variable | Required for |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Summary, analysis, teaching, Q&A |
| `GEMINI_API_KEY` | Images, flashcards, short summaries |
| `OPENAI_API_KEY` | Meeting / audio transcription (Whisper) |
| `AZURE_OPENAI_KEY` | Embeddings (Q&A mode) |
| `AZURE_STORAGE_CONNECTION_STRING` | Document storage |
| `AZURE_SQL_CONNECTION_STRING` | Usage tracking |
| `DATABRICKS_HOST` | Vector search |
| `DATABRICKS_TOKEN` | Vector search |
| `STRIPE_SECRET_KEY` | Payments |
| `GOOGLE_CLIENT_ID` | Auth |

See [.env.example](.env.example) for the full list.

---

## Contributing

```bash
git clone https://github.com/harshitboots/grasp-ai.git
cd grasp-ai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
git checkout -b feature/your-feature
# make changes
streamlit run app.py   # test locally
git push origin feature/your-feature
# open a PR
```

Good first contributions:
- **New parser** — Word docs, PowerPoint, audio from URLs
- **Q&A mode** — `agent/modes/qa.py` using vector search
- **Flashcards mode** — `agent/modes/flashcards.py`
- **New connector** — Notion, Google Drive, Confluence

---

## License

MIT — free to use, modify and distribute.

---

<div align="center">

Built by **Harshit Tripathi**

[![GitHub](https://img.shields.io/badge/GitHub-harshitboots-181717?style=flat-square&logo=github)](https://github.com/harshitboots)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=flat-square&logo=linkedin)](https://linkedin.com/in/harshittripathi)

</div>
