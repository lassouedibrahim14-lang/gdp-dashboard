"""
Agnes AI — high-end minimalist mobile chat UI (Streamlit).
Palette: deep black, pure white, earthy browns (mocha, cedar, sand).
"""

from __future__ import annotations

import html
import inspect

import streamlit as st

_TABS_STATEFUL = "on_change" in inspect.signature(st.tabs).parameters

# —— Page ——
st.set_page_config(
    page_title="Agnes AI",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# —— Session ——
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "text": "مرحباً ، أنا أغنيس.. كيف يمكنني مساعدتك اليوم؟",
        }
    ]
if "active_model" not in st.session_state:
    st.session_state.active_model = "Agnes-Ultra"

# —— Custom CSS (10% scale + full theme) ——
st.markdown(
    """
<style>
  /* 10% UI scale reduction */
  html {
    zoom: 0.9;
  }
  @supports not (zoom: 1) {
    .main .block-container {
      transform: scale(0.9);
      transform-origin: top center;
      width: 111.11%;
      max-width: 111.11%;
    }
  }

  :root {
    --agnes-black: #0c0c0c;
    --agnes-black-soft: #141211;
    --agnes-white: #ffffff;
    --agnes-sand: #d4c4b0;
    --agnes-sand-muted: #b8a995;
    --agnes-mocha: #6b4423;
    --agnes-cedar: #5c3d2e;
    --agnes-accent: #a0522d;
    --agnes-accent-deep: #8b4513;
    --agnes-bubble-agnes: #3d2b1f;
    --agnes-glass: rgba(139, 69, 19, 0.12);
    --agnes-glass-border: rgba(160, 82, 45, 0.45);
  }

  .stApp {
    background: var(--agnes-black) !important;
    color: var(--agnes-white);
  }

  [data-testid="stAppViewContainer"],
  .main {
    background: var(--agnes-black) !important;
  }

  .main .block-container {
    padding-top: 0.5rem;
    padding-bottom: 5.5rem;
    max-width: 28rem;
  }

  /* Hide Streamlit chrome */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header[data-testid="stHeader"] { background: transparent; }

  /* Header */
  .agnes-header-wrap {
    padding: 0.75rem 0 1rem;
    border-bottom: 1px solid rgba(160, 82, 45, 0.25);
    margin-bottom: 0.75rem;
  }
  .agnes-title {
    font-family: "Segoe UI", system-ui, sans-serif;
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    color: var(--agnes-white);
    margin: 0;
    line-height: 1.2;
  }
  .agnes-subtitle {
    font-family: "Segoe UI", system-ui, sans-serif;
    font-size: 0.82rem;
    font-weight: 400;
    color: var(--agnes-sand);
    margin: 0.35rem 0 0;
    letter-spacing: 0.02em;
  }

  /* Tabs: Agnes-Ultra / Agnes-Fast — active underline in brown */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: transparent;
    border-bottom: 1px solid rgba(160, 82, 45, 0.2);
  }
  .stTabs [data-baseweb="tab"] {
    color: var(--agnes-sand-muted) !important;
    font-weight: 600;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
    padding: 0.5rem 1rem !important;
    background: transparent !important;
  }
  .stTabs [aria-selected="true"] {
    color: var(--agnes-white) !important;
    border-bottom: 2px solid var(--agnes-accent) !important;
    border-radius: 0 !important;
  }
  .stTabs [data-baseweb="tab-highlight"] {
    display: none;
  }

  /* Fallback: horizontal radio when st.tabs has no on_change / .open */
  .agnes-model-tabs-fallback .stRadio > div {
    flex-direction: row !important;
    gap: 0 !important;
    background: transparent !important;
    border-bottom: 1px solid rgba(160, 82, 45, 0.2);
    padding-bottom: 0 !important;
  }
  .agnes-model-tabs-fallback .stRadio > div > label {
    margin: 0 !important;
    padding: 0.5rem 1rem !important;
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    color: var(--agnes-sand-muted) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
  }
  .agnes-model-tabs-fallback .stRadio > div > label:has(input:checked) {
    color: var(--agnes-white) !important;
    border-bottom-color: var(--agnes-accent) !important;
  }

  /* Skills horizontal scroll */
  .skills-scroll {
    display: flex;
    gap: 0.75rem;
    overflow-x: auto;
    padding: 0.5rem 0 1rem;
    margin: 0 -0.25rem;
    scrollbar-color: var(--agnes-accent) var(--agnes-black-soft);
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
  }
  .skills-scroll::-webkit-scrollbar {
    height: 4px;
  }
  .skills-scroll::-webkit-scrollbar-thumb {
    background: var(--agnes-accent);
    border-radius: 2px;
  }
  .skill-card {
    flex: 0 0 auto;
    width: 148px;
    padding: 0.85rem 1rem;
    background: var(--agnes-glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--agnes-glass-border);
    border-radius: 10px;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.35), 0 0 0 1px rgba(0, 0, 0, 0.2);
  }
  .skill-card-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: var(--agnes-white);
    margin: 0 0 0.35rem;
    line-height: 1.25;
  }
  .skill-card-sub {
    font-size: 0.72rem;
    color: var(--agnes-sand-muted);
    margin: 0;
    line-height: 1.35;
  }

  /* Chat area */
  .agnes-chat-stack {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin: 1rem 0;
    min-height: 200px;
  }
  .bubble-row {
    display: flex;
    width: 100%;
  }
  .bubble-row.user { justify-content: flex-end; }
  .bubble-row.assistant { justify-content: flex-start; }
  .bubble-agnes {
    max-width: 92%;
    padding: 0.75rem 1rem;
    background: var(--agnes-bubble-agnes);
    color: var(--agnes-white);
    border-radius: 14px 14px 14px 4px;
    font-size: 0.9rem;
    line-height: 1.5;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
  }
  .bubble-user {
    max-width: 88%;
    padding: 0.75rem 1rem;
    background: var(--agnes-black-soft);
    color: var(--agnes-white);
    border: 1px solid rgba(255, 255, 255, 0.55);
    border-radius: 14px 14px 4px 14px;
    font-size: 0.9rem;
    line-height: 1.5;
  }

  /* Chat input */
  [data-testid="stChatInput"] {
    background: var(--agnes-black-soft) !important;
    border: 1px solid rgba(160, 82, 45, 0.35) !important;
    border-radius: 12px !important;
  }
  [data-testid="stChatInput"] textarea {
    color: var(--agnes-white) !important;
    caret-color: var(--agnes-accent);
  }
  [data-testid="stChatInput"] textarea::placeholder {
    color: var(--agnes-sand-muted) !important;
    opacity: 0.9;
  }

  /* Bottom bar */
  .agnes-bottom-bar {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 999990;
    background: var(--agnes-black);
    border-top: 1px solid rgba(160, 82, 45, 0.28);
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 0.55rem 0 calc(0.55rem + env(safe-area-inset-bottom, 0px));
    max-width: 28rem;
    margin: 0 auto;
  }
  .agnes-nav-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.2rem;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem 0.75rem;
    color: var(--agnes-sand);
    font-size: 0.62rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }
  .agnes-nav-btn svg {
    width: 22px;
    height: 22px;
    stroke: var(--agnes-accent);
    fill: none;
    stroke-width: 1.6;
  }
  .agnes-nav-btn--active { color: var(--agnes-white); }
  .agnes-nav-btn--active svg { stroke: var(--agnes-white); }

  /* Primary buttons */
  .stButton > button {
    background: var(--agnes-accent) !important;
    color: var(--agnes-white) !important;
    border: 1px solid var(--agnes-accent-deep) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
  }
  .stButton > button:hover {
    border-color: var(--agnes-accent) !important;
    box-shadow: 0 0 0 1px rgba(160, 82, 45, 0.4);
  }

  hr {
    border: none;
    border-top: 1px solid rgba(160, 82, 45, 0.15);
    margin: 0.75rem 0;
  }
</style>
""",
    unsafe_allow_html=True,
)


def render_header() -> None:
    st.markdown(
        """
<div class="agnes-header-wrap">
  <h1 class="agnes-title">Agnes</h1>
  <p class="agnes-subtitle">Your Sophisticated Intelligent Assistant</p>
</div>
    """,
        unsafe_allow_html=True,
    )


def render_skills_carousel() -> None:
    skills = [
        ("Research", "Deep synthesis & sources"),
        ("Writing", "Polished prose in your voice"),
        ("Code", "Review, refactor, ship"),
        ("Strategy", "Structured decisions"),
    ]
    cards = ""
    for title, sub in skills:
        cards += f"""
        <div class="skill-card">
          <p class="skill-card-title">{title}</p>
          <p class="skill-card-sub">{sub}</p>
        </div>"""
    st.markdown(
        f'<div class="skills-scroll">{cards}</div>',
        unsafe_allow_html=True,
    )


def render_chat() -> None:
    parts = ['<div class="agnes-chat-stack">']
    for m in st.session_state.messages:
        safe = html.escape(m["text"])
        if m["role"] == "assistant":
            parts.append(
                f'<div class="bubble-row assistant"><div class="bubble-agnes">{safe}</div></div>'
            )
        else:
            parts.append(
                f'<div class="bubble-row user"><div class="bubble-user">{safe}</div></div>'
            )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_bottom_bar() -> None:
    st.markdown(
        """
<div class="agnes-bottom-bar">
  <button type="button" class="agnes-nav-btn agnes-nav-btn--active" title="Chat">
    <svg viewBox="0 0 24 24"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
    Chat
  </button>
  <button type="button" class="agnes-nav-btn" title="Skills">
    <svg viewBox="0 0 24 24"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
    Skills
  </button>
  <button type="button" class="agnes-nav-btn" title="Settings">
    <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9c0 .55.22 1.09.62 1.49.4.4.94.62 1.49.62H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
    Settings
  </button>
</div>
        """,
        unsafe_allow_html=True,
    )


# —— Layout ——
render_header()

# Native tabs with lazy execution when supported; else tab-styled radio.
if _TABS_STATEFUL:
    tab_ultra, tab_fast = st.tabs(
        ["Agnes-Ultra", "Agnes-Fast"],
        on_change="rerun",
        key="agnes_model_tabs",
    )
    if tab_ultra.open:
        with tab_ultra:
            st.session_state.active_model = "Agnes-Ultra"
    if tab_fast.open:
        with tab_fast:
            st.session_state.active_model = "Agnes-Fast"
else:
    st.markdown('<div class="agnes-model-tabs-fallback">', unsafe_allow_html=True)
    _idx = 0 if st.session_state.get("active_model", "Agnes-Ultra") == "Agnes-Ultra" else 1
    _choice = st.radio(
        "Model",
        ["Agnes-Ultra", "Agnes-Fast"],
        horizontal=True,
        label_visibility="collapsed",
        index=_idx,
        key="agnes_model_radio",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.session_state.active_model = _choice

render_skills_carousel()
render_chat()

placeholder = (
    "Message Agnes…"
    if st.session_state.get("active_model", "Agnes-Ultra") == "Agnes-Ultra"
    else "Message Agnes (Fast)…"
)
prompt = st.chat_input(placeholder)
if prompt:
    st.session_state.messages.append({"role": "user", "text": prompt})
    if st.session_state.active_model == "Agnes-Ultra":
        reply = "Agnes-Ultra — UI demo. Connect your model here for full reasoning."
    else:
        reply = "Agnes-Fast — UI demo. Wire your streaming endpoint for snappy replies."
    st.session_state.messages.append({"role": "assistant", "text": reply})
    st.rerun()

render_bottom_bar()

