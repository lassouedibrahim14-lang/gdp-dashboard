"""
Agnes AI Platform — multi-page Streamlit app (Luxurious Tech theme).
Place branding image at: assets/1774731150152.png (same folder as this file).
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

import streamlit as st
from openai import OpenAI

# —— Paths ——
_ROOT = Path(__file__).resolve().parent
LOGO_PATH = _ROOT / "assets" / "1774731150152.png"

# —— Theme ——
BG = "#000000"
CARD = "#1A1412"
ACCENT = "#00E5FF"

CODE_SYSTEM_PROMPT = """You are an expert software engineer and coding assistant for the Agnes AI Platform.
Always produce clear, production-minded answers: correct code blocks with language tags, brief explanations when helpful, and security-aware defaults."""

PAGE_LABELS: dict[str, str] = {
    "chat": "💬 Chat",
    "code": "</> Code Assistant",
    "settings": "⚙️ Settings",
    "upgrade": "💎 Upgrade (Pro/Ultra)",
}


def _init_state() -> None:
    defaults: dict[str, Any] = {
        "logged_in": False,
        "current_page": "chat",
        "unsloth_url": "http://localhost:8000/v1",
        "model_name": "default",
        "temperature": 0.7,
        "language": "en",
        "chat_messages": [],
        "code_prompt": "",
        "code_last_reply": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _is_ar() -> bool:
    return st.session_state.get("language") == "ar"


def _inject_css() -> None:
    rtl = "rtl" if _is_ar() else "ltr"
    hide_sb = (
        '[data-testid="stSidebar"] { display: none !important; }'
        if not st.session_state.get("logged_in")
        else ""
    )
    st.markdown(
        f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  html, body, .stApp, [data-testid="stAppViewContainer"], .main {{
    font-family: "Cairo", system-ui, sans-serif !important;
  }}
  .stApp, [data-testid="stAppViewContainer"] {{
    background: {BG} !important;
    color: #EAE6E1 !important;
  }}
  .main .block-container {{
    padding-top: 0.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
    direction: {rtl};
  }}
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0A0A0A 0%, #12100E 100%) !important;
    border-right: 1px solid rgba(0, 229, 255, 0.15) !important;
  }}
  {hide_sb}
  .lux-card {{
    background: {CARD};
    border: 1px solid rgba(0, 229, 255, 0.22);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 0 40px rgba(0, 229, 255, 0.06);
  }}
  .stTextInput input, .stTextArea textarea {{
    background: #0D0D0D !important;
    color: #F4F2EF !important;
    border: 1px solid rgba(0, 229, 255, 0.35) !important;
    border-radius: 10px !important;
  }}
  .stTextInput input:focus, .stTextArea textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 1px {ACCENT} !important;
    outline: none !important;
  }}
  [data-testid="stChatInput"] {{
    border: 1px solid rgba(0, 229, 255, 0.4) !important;
    border-radius: 12px !important;
    background: #0D0D0D !important;
  }}
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
  .rtl-msg {{ direction: rtl; text-align: right; unicode-bidi: plaintext; }}
</style>
        """,
        unsafe_allow_html=True,
    )


def _normalize_api_base(url: str) -> str:
    u = url.strip().rstrip("/")
    if not u.endswith("/v1"):
        u = u + "/v1"
    return u


def _client() -> OpenAI:
    return OpenAI(base_url=_normalize_api_base(st.session_state.unsloth_url), api_key="not-needed")


def _render_brand_header() -> None:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:1.25rem;flex-wrap:wrap;margin-bottom:1rem;">',
        unsafe_allow_html=True,
    )
    if LOGO_PATH.is_file():
        st.image(str(LOGO_PATH), width=280)
    else:
        st.warning(
            f"Logo not found. Add your image as: `{LOGO_PATH}`"
        )
    st.markdown(
        """
</div>
<div style="border-bottom:1px solid rgba(0,229,255,0.2);margin-bottom:1rem;"></div>
        """,
        unsafe_allow_html=True,
    )


def _render_login() -> None:
    _, c, _ = st.columns([1, 2, 1])
    with c:
        with st.container(border=True):
            st.markdown("### Sign in to **Agnes AI Platform**")
            st.caption("Luxurious Tech · Local Unsloth ready")

            with st.form("signin_form"):
                st.text_input("Email or username", key="login_user")
                st.text_input("Password", type="password", key="login_pwd")
                go = st.form_submit_button(
                    "Sign in", type="primary", use_container_width=True
                )

            if go:
                st.session_state.logged_in = True
                st.session_state.current_page = "chat"
                st.rerun()

            st.markdown(
                "<p style='text-align:center;opacity:0.45;margin:1rem 0;'>or continue with</p>",
                unsafe_allow_html=True,
            )
            g1, g2 = st.columns(2)
            with g1:
                if st.button("Sign in with Google", use_container_width=True):
                    st.info("Google OAuth can be wired here (e.g. Authlib / cloud IdP).")
            with g2:
                if st.button("Sign in with GitHub", use_container_width=True):
                    st.info("GitHub OAuth can be wired here.")


def _render_sidebar() -> None:
    st.sidebar.markdown("### Agnes AI Platform")
    st.sidebar.caption("Navigation")
    options = list(PAGE_LABELS.keys())
    if st.session_state.current_page not in options:
        st.session_state.current_page = "chat"

    st.sidebar.radio(
        "Page",
        options,
        format_func=lambda k: PAGE_LABELS[k],
        label_visibility="collapsed",
        key="current_page",
    )

    if st.sidebar.button("Log out", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["chat_messages"] = []
        st.rerun()


def _chat_page() -> None:
    st.subheader("Chat")
    st.caption(
        f"Endpoint: `{st.session_state.unsloth_url}` · Model: `{st.session_state.model_name}`"
    )

    for msg in st.session_state.chat_messages:
        role = msg["role"]
        content = msg["content"]
        with st.chat_message(role):
            if _is_ar():
                st.markdown(
                    f'<div class="rtl-msg">{html.escape(content)}</div>',
                    unsafe_allow_html=True,
                )
            elif role == "user":
                st.text(content)
            else:
                st.markdown(content)

    prompt = st.chat_input("Message Agnes…")
    if not prompt:
        return

    st.session_state.chat_messages.append({"role": "user", "content": prompt})

    try:
        cli = _client()
        msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages]
        resp = cli.chat.completions.create(
            model=st.session_state.model_name,
            messages=msgs,
            temperature=float(st.session_state.temperature),
        )
        text = resp.choices[0].message.content or ""
    except Exception as e:
        text = (
            f"**Connection error:** {e!s}\n\n"
            "Check **Settings → Local Unsloth API URL** and that your server is running."
        )

    st.session_state.chat_messages.append({"role": "assistant", "content": text})
    st.rerun()


def _code_page() -> None:
    st.subheader("Code Assistant")
    st.caption("Sends a developer system prompt to your Unsloth OpenAI-compatible API.")

    st.text_area(
        "Describe what to build or fix",
        height=220,
        key="code_prompt",
    )

    if st.button("Generate Code", type="primary"):
        prompt = str(st.session_state.get("code_prompt", "")).strip()
        if not prompt:
            st.warning("Enter a prompt first.")
            return
        try:
            cli = _client()
            r = cli.chat.completions.create(
                model=st.session_state.model_name,
                messages=[
                    {"role": "system", "content": CODE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=float(st.session_state.temperature),
            )
            st.session_state.code_last_reply = r.choices[0].message.content or ""
        except Exception as e:
            st.session_state.code_last_reply = f"Error: {e!s}"

    if st.session_state.code_last_reply:
        st.markdown("#### Output")
        st.markdown(st.session_state.code_last_reply)


def _settings_page() -> None:
    st.subheader("Settings")

    st.markdown("##### AI Connection")
    st.text_input(
        "Local Unsloth API URL",
        key="unsloth_url",
        help="OpenAI-compatible base, e.g. http://localhost:8000/v1",
    )
    st.text_input(
        "Model name (as exposed by your server)",
        key="model_name",
    )

    st.markdown("##### Preferences")
    st.slider(
        "AI Creativity (Temperature)",
        min_value=0.0,
        max_value=2.0,
        step=0.05,
        key="temperature",
    )
    ar = st.toggle(
        "Language: Arabic (RTL)",
        value=st.session_state.language == "ar",
        key="settings_lang_toggle",
    )
    st.session_state.language = "ar" if ar else "en"
    st.info("Arabic mode applies RTL layout and right-aligned assistant text in chat.")


def _upgrade_page() -> None:
    st.subheader("Upgrade")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(
            f"""
<div class="lux-card" style="min-height:340px;">
  <h3 style="color:#fff;margin-top:0;">Agnes Pro</h3>
  <p style="color:#B8A99A;font-size:0.95rem;">Solid tier for daily use.</p>
  <p style="color:{ACCENT};font-size:1.6rem;font-weight:700;">$9.99<span style="font-size:0.85rem;color:#9A8F88">/mo</span></p>
  <ul style="color:#EAE6E1;line-height:1.8;">
    <li>Faster response priority</li>
    <li>Standard context window</li>
    <li>Email support</li>
  </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Subscribe Now — Pro", key="sub_pro", use_container_width=True):
            st.success("Redirecting to secure payment gateway…")

    with c2:
        st.markdown(
            f"""
<div style="
  min-height:340px;
  background: {CARD};
  border: 2px solid {ACCENT};
  border-radius:16px;
  padding:1.5rem;
  box-shadow:0 0 48px rgba(0,229,255,0.25), inset 0 0 60px rgba(0,229,255,0.06);
">
  <div style="display:inline-block;background:{ACCENT};color:#001018;font-size:0.65rem;font-weight:700;
    letter-spacing:0.12em;padding:0.25rem 0.6rem;border-radius:999px;margin-bottom:0.5rem;">ULTRA</div>
  <h3 style="color:{ACCENT};margin-top:0;">Agnes Ultra</h3>
  <p style="color:#B8A99A;font-size:0.95rem;">Maximum performance for power users.</p>
  <p style="color:{ACCENT};font-size:1.6rem;font-weight:700;">$19.99<span style="font-size:0.85rem;color:#9A8F88">/mo</span></p>
  <ul style="color:#EAE6E1;line-height:1.8;">
    <li><span style="color:{ACCENT}">Faster Unsloth</span> processing</li>
    <li><span style="color:{ACCENT}">Unlimited context</span> (where supported)</li>
    <li>Priority routing & premium support</li>
  </ul>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Subscribe Now — Ultra", key="sub_ultra", use_container_width=True):
            st.success("Redirecting to secure payment gateway…")


def _route() -> None:
    page = st.session_state.current_page
    if page == "code":
        _code_page()
    elif page == "settings":
        _settings_page()
    elif page == "upgrade":
        _upgrade_page()
    else:
        _chat_page()


def main() -> None:
    st.set_page_config(
        page_title="Agnes AI Platform",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _init_state()
    _inject_css()

    _render_brand_header()

    if not st.session_state.logged_in:
        _render_login()
        return

    _render_sidebar()
    _route()


if __name__ == "__main__":
    main()
