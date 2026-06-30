import os
import streamlit as st
from dotenv import load_dotenv

from agent.router import detect
from agent.parsers import web_parser, youtube_parser, pdf_parser, image_parser, audio_parser
from agent.modes import summary, analysis

load_dotenv()

st.set_page_config(
    page_title="Grasp — Britcore AI",
    page_icon="🧠",
    layout="centered",
)


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_key(env_name: str, sidebar_val: str) -> str:
    """Return sidebar value if set, else st.secrets, else .env."""
    if sidebar_val:
        return sidebar_val
    try:
        return st.secrets.get(env_name, "") or os.getenv(env_name, "")
    except Exception:
        return os.getenv(env_name, "")


def _cost_badge(gbp: float) -> str:
    return f"£{gbp:.4f}" if gbp >= 0.0001 else "<£0.0001"


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🧠 Grasp")
    st.caption("Britcore AI — Upload anything. Understand everything.")
    st.divider()

    st.subheader("API Keys")
    sb_anthropic = st.text_input("Anthropic (Claude)", type="password", placeholder="sk-ant-...")
    sb_gemini = st.text_input("Google (Gemini)", type="password", placeholder="AIza...")
    sb_openai = st.text_input("OpenAI (Whisper)", type="password", placeholder="sk-...")
    st.caption("Keys live in your browser session only — never saved.")
    st.divider()
    st.markdown("[GitHub](https://github.com/harshitboots/grasp-ai) · MIT Licence")


anthropic_key = _get_key("ANTHROPIC_API_KEY", sb_anthropic)
gemini_key = _get_key("GEMINI_API_KEY", sb_gemini)
openai_key = _get_key("OPENAI_API_KEY", sb_openai)


# ── header ────────────────────────────────────────────────────────────────────

st.title("🧠 Grasp")
st.markdown("**Paste a link · Drop a document · Upload an image · Record your meeting**")
st.markdown("Get a short, clear summary instantly.")
st.divider()


# ── input tabs ────────────────────────────────────────────────────────────────

tab_url, tab_doc, tab_img, tab_meeting = st.tabs(
    ["🔗 URL / YouTube", "📄 Document", "🖼️ Image", "🎙️ Meeting"]
)

content = None  # parsed content dict — set by whichever tab runs

# ── URL / YouTube tab ─────────────────────────────────────────────────────────
with tab_url:
    url = st.text_input(
        "Paste any link",
        placeholder="https://... or https://youtube.com/watch?v=...",
        label_visibility="collapsed",
    )
    if st.button("Summarise", key="btn_url", type="primary") and url:
        with st.spinner("Reading the link..."):
            try:
                url_type = detect(url)
                if url_type == "youtube":
                    content = youtube_parser.parse(url)
                else:
                    content = web_parser.parse(url)
                st.session_state["content"] = content
            except Exception as e:
                st.error(f"Could not read that link: {e}")

# ── Document tab ──────────────────────────────────────────────────────────────
with tab_doc:
    uploaded_doc = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        label_visibility="collapsed",
    )
    if st.button("Summarise", key="btn_doc", type="primary") and uploaded_doc:
        with st.spinner("Reading document..."):
            try:
                content = pdf_parser.parse(uploaded_doc.read())
                st.session_state["content"] = content
            except Exception as e:
                st.error(f"Could not read that document: {e}")

# ── Image tab ─────────────────────────────────────────────────────────────────
with tab_img:
    if not gemini_key:
        st.info("Add your Gemini API key in the sidebar to use image reading.")
    uploaded_img = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
    if st.button("Read Image", key="btn_img", type="primary") and uploaded_img:
        if not gemini_key:
            st.error("Gemini API key required for image reading.")
        else:
            with st.spinner("Reading image with Gemini Vision..."):
                try:
                    content = image_parser.parse(uploaded_img.read(), api_key=gemini_key)
                    st.session_state["content"] = content
                except Exception as e:
                    st.error(f"Could not read image: {e}")

# ── Meeting tab ───────────────────────────────────────────────────────────────
with tab_meeting:
    if not openai_key:
        st.info("Add your OpenAI API key in the sidebar to transcribe meetings.")
    uploaded_audio = st.file_uploader(
        "Upload meeting recording",
        type=["mp3", "mp4", "wav", "m4a", "webm", "ogg"],
        label_visibility="collapsed",
    )
    st.caption("Supports MP3, MP4, WAV, M4A, WEBM — up to ~25 MB")
    if st.button("Transcribe & Summarise", key="btn_meeting", type="primary") and uploaded_audio:
        if not openai_key:
            st.error("OpenAI API key required for audio transcription.")
        else:
            with st.spinner("Transcribing with Whisper..."):
                try:
                    content = audio_parser.transcribe(
                        uploaded_audio.read(),
                        filename=uploaded_audio.name,
                        api_key=openai_key,
                    )
                    st.session_state["content"] = content
                except Exception as e:
                    st.error(f"Transcription failed: {e}")


# ── results ───────────────────────────────────────────────────────────────────

content = content or st.session_state.get("content")

if content:
    st.divider()

    # source info bar
    source_emoji = {
        "web": "🌐", "youtube": "▶️", "pdf": "📄", "image": "🖼️", "audio": "🎙️"
    }
    emoji = source_emoji.get(content.get("source_type", "web"), "📄")
    pages = f" · {content['page_count']} pages" if "page_count" in content else ""
    dur = f" · ~{content['estimated_duration_mins']} min recording" if "estimated_duration_mins" in content else ""

    st.markdown(
        f"{emoji} **{content['title']}** · "
        f"{content['word_count']:,} words{pages}{dur}"
    )

    # ── summary ───────────────────────────────────────────────────────────────
    if "summary_result" not in st.session_state or \
            st.session_state.get("summary_content_id") != id(content):

        if not anthropic_key and not gemini_key:
            st.warning("Add at least one API key (Anthropic or Gemini) in the sidebar to generate a summary.")
        else:
            with st.spinner("Generating summary..."):
                try:
                    result = summary.run(
                        content,
                        anthropic_key=anthropic_key,
                        gemini_key=gemini_key,
                    )
                    st.session_state["summary_result"] = result
                    st.session_state["summary_content_id"] = id(content)
                except Exception as e:
                    st.error(f"Summary failed: {e}")

    if "summary_result" in st.session_state:
        result = st.session_state["summary_result"]
        st.markdown(result["output"])

        # model + cost strip
        st.caption(
            f"Model: **{result['model']}** · "
            f"Tokens: {result['input_tokens']:,} in / {result['output_tokens']:,} out · "
            f"Cost: **{_cost_badge(result['cost_gbp'])}** · "
            f"_{result['reason']}_"
        )

        st.divider()

        # ── analysis ──────────────────────────────────────────────────────────
        st.markdown("#### 🔍 Deep Analysis")
        if not anthropic_key:
            st.info("Add your Anthropic API key to run deep analysis (uses Claude Sonnet).")
        else:
            if st.button("Run Analysis", key="btn_analysis"):
                with st.spinner("Analysing with Claude Sonnet..."):
                    try:
                        a_result = analysis.run(content, anthropic_key=anthropic_key)
                        st.session_state["analysis_result"] = a_result
                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

            if "analysis_result" in st.session_state:
                a = st.session_state["analysis_result"]
                st.markdown(a["output"])
                st.caption(
                    f"Model: **{a['model']}** · "
                    f"Tokens: {a['input_tokens']:,} in / {a['output_tokens']:,} out · "
                    f"Cost: **{_cost_badge(a['cost_gbp'])}**"
                )
