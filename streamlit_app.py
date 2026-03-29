#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agnes AI — premium Streamlit application (single-file).
Multi-page router, luxury dark UI, OpenAI-compatible local API.
"""

from __future__ import annotations

import copy
import html
import json
import sys
from typing import Any, Callable, Dict, List, Tuple

# ---------------------------------------------------------------------------
# Safe dependency loading — app must not assume optional packages exist
# ---------------------------------------------------------------------------
try:
    import streamlit as st
except ImportError:  # pragma: no cover
    print("Streamlit is required. Install with: pip install streamlit", file=sys.stderr)
    sys.exit(1)

OpenAI = None  # type: ignore
try:
    from openai import OpenAI as _OpenAIClient  # type: ignore

    OpenAI = _OpenAIClient
except ImportError:
    pass

try:
    import urllib
    import urllib.error
    import urllib.request
except ImportError:  # pragma: no cover
    urllib = None  # type: ignore

# ---------------------------------------------------------------------------
# Design tokens — Aether / luxury dark
# ---------------------------------------------------------------------------
C_BG = "#1A1412"
C_CARD = "#000000"
C_ACCENT = "#00E5FF"
C_TEXT = "#F5F0EC"
C_MUTED = "#9A8F88"
C_BORDER = "rgba(0, 229, 255, 0.25)"

FONT_EN = '"Plus Jakarta Sans", system-ui, sans-serif'
FONT_AR = '"Cairo", "Plus Jakarta Sans", system-ui, sans-serif'

LOGO_PATH = "assets/1774731150152.png"


# ---------------------------------------------------------------------------
# Session bootstrap — defaults applied safely every run
# ---------------------------------------------------------------------------
def _default_settings() -> Dict[str, Any]:
    return {
        "api_url": "http://localhost:8000/v1",
        "model": "unsloth",
        "temperature": 0.7,
        "api_key": "",
        "language": "en",
    }


def init_session_state() -> None:
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state["page"] = "login"
        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.settings = _default_settings()
        st.session_state.code_buffer = ""
        st.session_state.code_output = ""
        st.session_state.chat_input_draft = ""
        st.session_state.last_api_error = ""

    base = _default_settings()
    cur = st.session_state.settings
    if not isinstance(cur, dict):
        st.session_state.settings = copy.deepcopy(base)
    else:
        for k, v in base.items():
            if k not in cur:
                cur[k] = copy.deepcopy(v) if isinstance(v, dict) else v


def dependency_status() -> Tuple[bool, List[str]]:
    """Return (can_call_api, warning_messages_for_ui)."""
    warns: List[str] = []
    if OpenAI is None:
        warns.append(
            "Optional dependency `openai` is not installed. The app will use the built-in HTTP client. "
            "Install with: pip install openai"
        )
    if urllib is None or not hasattr(urllib, "request"):
        warns.append("HTTP client (urllib) is unavailable. API calls cannot be made in this environment.")
        return False, warns
    return True, warns


def inject_global_css(rtl: bool) -> None:
    direction = "rtl" if rtl else "ltr"
    font_main = FONT_AR if rtl else FONT_EN
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

        @keyframes aegis-fade-in {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        html, body, [class*="css"] {{
            font-family: {font_main};
        }}
        .stApp {{
            background: radial-gradient(1200px 800px at 20% -10%, rgba(0, 229, 255, 0.08), transparent 55%),
                        radial-gradient(900px 600px at 100% 20%, rgba(0, 229, 255, 0.05), transparent 50%),
                        {C_BG};
            color: {C_TEXT};
        }}
        section.main, section.main .block-container {{
            direction: {direction};
            text-align: start;
        }}
        section.main .block-container {{
            padding-top: 1.25rem;
            padding-bottom: 6rem;
            max-width: 1100px;
            animation: aegis-fade-in 0.5s ease-out;
        }}
        section.main .block-container .element-container {{
            animation: aegis-fade-in 0.55s ease-out both;
        }}
        [data-testid="stHeader"] {{
            background: rgba(26, 20, 18, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid {C_BORDER};
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #120E0C 0%, {C_BG} 100%);
            border-right: 1px solid {C_BORDER};
        }}
        .agnes-topnav {{
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 0.5rem;
            padding: 0.35rem 0 1.1rem 0;
            margin-bottom: 0.25rem;
            border-bottom: 1px solid {C_BORDER};
            animation: aegis-fade-in 0.4s ease-out both;
        }}
        .premium-card {{
            background: {C_CARD};
            border: 1px solid {C_BORDER};
            border-radius: 18px;
            box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.06),
                        0 20px 50px rgba(0, 0, 0, 0.55),
                        0 0 40px rgba(0, 229, 255, 0.08);
            padding: 1.75rem 2rem;
            transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        }}
        .premium-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.14),
                        0 26px 56px rgba(0, 0, 0, 0.6),
                        0 0 52px rgba(0, 229, 255, 0.14);
            border-color: rgba(0, 229, 255, 0.35);
        }}
        .premium-card-glow {{
            border: 1px solid rgba(0, 229, 255, 0.55);
            box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.25),
                        0 24px 60px rgba(0, 229, 255, 0.12),
                        0 0 48px rgba(0, 229, 255, 0.2);
        }}
        .premium-card-glow:hover {{
            border-color: rgba(0, 229, 255, 0.75);
            box-shadow: 0 0 0 1px rgba(0, 229, 255, 0.35),
                        0 28px 64px rgba(0, 229, 255, 0.18),
                        0 0 56px rgba(0, 229, 255, 0.28);
        }}
        .badge-popular {{
            display: inline-block;
            background: linear-gradient(90deg, {C_ACCENT}, #00b8d4);
            color: #0a0a0a;
            font-weight: 700;
            font-size: 0.72rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            margin-bottom: 0.75rem;
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.45);
        }}
        .top-logo-wrap {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.35rem 0 1rem 0;
        }}
        .brand-mark {{
            font-weight: 700;
            font-size: 1.15rem;
            letter-spacing: 0.04em;
            color: {C_TEXT};
            text-shadow: 0 0 24px rgba(0, 229, 255, 0.35);
        }}
        .divider-or {{
            display: flex;
            align-items: center;
            gap: 1rem;
            color: {C_MUTED};
            font-size: 0.85rem;
            margin: 1rem 0;
        }}
        .divider-or::before, .divider-or::after {{
            content: "";
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent, {C_BORDER}, transparent);
        }}
        .chat-bubble-user {{
            background: linear-gradient(135deg, rgba(0, 229, 255, 0.12), rgba(0, 229, 255, 0.04));
            border: 1px solid {C_BORDER};
            border-radius: 16px 16px 4px 16px;
            padding: 0.9rem 1.1rem;
            margin: 0.5rem 0 0.5rem 2rem;
            box-shadow: 0 0 24px rgba(0, 229, 255, 0.08);
            animation: aegis-fade-in 0.35s ease-out both;
        }}
        .chat-bubble-ai {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px 16px 16px 4px;
            padding: 0.9rem 1.1rem;
            margin: 0.5rem 2rem 0.5rem 0;
            animation: aegis-fade-in 0.4s ease-out both;
        }}
        .mono-out {{
            font-family: ui-monospace, "Cascadia Code", "SF Mono", Menlo, monospace;
            background: #0d0d0d;
            border: 1px solid {C_BORDER};
            border-radius: 14px;
            padding: 1rem;
            color: #d6f7ff;
            white-space: pre-wrap;
            box-shadow: inset 0 0 30px rgba(0, 229, 255, 0.06);
            animation: aegis-fade-in 0.45s ease-out both;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }}
        .mono-out:hover {{
            border-color: rgba(0, 229, 255, 0.32);
            box-shadow: inset 0 0 36px rgba(0, 229, 255, 0.1);
        }}
        div[data-testid="stChatInput"] {{
            background: {C_CARD};
            border-radius: 14px;
            transition: box-shadow 0.2s ease;
        }}
        div[data-testid="stChatInput"]:hover {{
            box-shadow: 0 0 20px rgba(0, 229, 255, 0.12);
        }}
        footer[data-testid="stFooter"] {{
            background: linear-gradient(180deg, rgba(26, 20, 18, 0) 0%, rgba(26, 20, 18, 0.97) 40%, {C_BG} 100%);
            border-top: 1px solid {C_BORDER};
            backdrop-filter: blur(14px);
        }}
        .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
            background-color: #0a0a0a !important;
            color: {C_TEXT} !important;
            border-radius: 12px !important;
            border: 1px solid {C_BORDER} !important;
            transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
        }}
        .stTextInput input:hover, .stTextArea textarea:hover {{
            border-color: rgba(0, 229, 255, 0.35) !important;
        }}
        .stSlider > div > div > div {{
            background: {C_ACCENT} !important;
        }}
        .stButton > button {{
            border-radius: 12px !important;
            font-weight: 600 !important;
            border: 1px solid {C_BORDER} !important;
            background: linear-gradient(180deg, rgba(0, 229, 255, 0.15), rgba(0, 0, 0, 0.4)) !important;
            color: {C_TEXT} !important;
            box-shadow: 0 0 18px rgba(0, 229, 255, 0.12) !important;
            transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease !important;
        }}
        .stButton > button:hover {{
            border-color: rgba(0, 229, 255, 0.55) !important;
            box-shadow: 0 0 28px rgba(0, 229, 255, 0.25) !important;
            transform: translateY(-1px);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Logo + top navigation
# ---------------------------------------------------------------------------
def render_top_logo_bar() -> None:
    col_a, col_b = st.columns([1, 4])
    with col_a:
        try:
            st.image(LOGO_PATH, width=56)
        except Exception:
            st.warning("Logo not found or unreadable — expected path: " + LOGO_PATH)
            st.markdown('<div class="brand-mark" style="font-size:2rem;">◆</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(
            '<div class="top-logo-wrap"><span class="brand-mark">AGNES AI</span>'
            '<span style="color:#9A8F88;font-size:0.9rem;"> · Neural Workspace</span></div>',
            unsafe_allow_html=True,
        )


def render_dependency_warnings() -> None:
    _, warns = dependency_status()
    for msg in warns:
        st.warning(msg)


def render_top_navigation() -> None:
    settings = st.session_state.settings
    rtl = settings.get("language") == "ar"
    labels = [
        ("chat", "Chat" if not rtl else "محادثة"),
        ("code", "Code Assistant" if not rtl else "مساعد الكود"),
        ("settings", "Settings" if not rtl else "الإعدادات"),
        ("pricing", "Pricing" if not rtl else "الأسعار"),
    ]
    st.markdown('<div class="agnes-topnav">', unsafe_allow_html=True)
    cols = st.columns([1.15, 1.35, 1.05, 1.05, 0.88])
    for i, (key, text) in enumerate(labels):
        with cols[i]:
            if st.button(text, key=f"topnav_{key}", use_container_width=True):
                st.session_state["page"] = key
                st.rerun()
    with cols[4]:
        if st.button("Logout" if not rtl else "خروج", key="topnav_logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.messages = []
            st.session_state["page"] = "login"
            st.session_state.last_api_error = ""
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# API — OpenAI-compatible (local / Unsloth)
# ---------------------------------------------------------------------------
def _response_looks_like_error(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return True
    if t.startswith("[HTTP") or t.startswith("[API Error]") or t.startswith("[Error]"):
        return True
    if t.startswith("[OpenAI SDK Error]"):
        return True
    if "urllib not available" in t:
        return True
    return False


def _chat_via_urllib(messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
    if urllib is None or not hasattr(urllib, "request"):
        return "[Error] HTTP client unavailable — cannot reach the local API."
    base = str(settings.get("api_url", "")).rstrip("/")
    url = f"{base}/chat/completions"
    payload = {
        "model": settings.get("model", "unsloth"),
        "messages": messages,
        "temperature": float(settings.get("temperature", 0.7)),
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    key = (settings.get("api_key") or "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.load(resp)
        choices = body.get("choices") or []
        if not choices:
            return json.dumps(body, indent=2)[:4000]
        msg = choices[0].get("message") or {}
        return str(msg.get("content", ""))
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            err_body = str(e)
        return f"[HTTP {e.code}] {err_body[:2000]}"
    except Exception as e:
        return f"[API Error] {type(e).__name__}: {e}"


def _chat_via_openai_sdk(messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
    if OpenAI is None:
        return _chat_via_urllib(messages, settings)
    base = str(settings.get("api_url", "")).rstrip("/")
    key = (settings.get("api_key") or "not-needed").strip() or "not-needed"
    try:
        client = OpenAI(base_url=base, api_key=key)
        resp = client.chat.completions.create(
            model=str(settings.get("model", "unsloth")),
            messages=messages,
            temperature=float(settings.get("temperature", 0.7)),
        )
        return (resp.choices[0].message.content or "") if resp.choices else ""
    except Exception as e:
        return f"[OpenAI SDK Error] {type(e).__name__}: {e}"


def call_chat_completion(messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
    can, _ = dependency_status()
    if not can:
        return "[Error] API calls are disabled (no HTTP client)."
    try:
        if OpenAI is not None:
            out = _chat_via_openai_sdk(messages, settings)
            if not _response_looks_like_error(out):
                return out
            fallback = _chat_via_urllib(messages, settings)
            if not _response_looks_like_error(fallback):
                return fallback
            return out or fallback
        return _chat_via_urllib(messages, settings)
    except Exception as e:
        return f"[Error] {type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def render_login() -> None:
    settings = st.session_state.settings
    rtl = settings.get("language") == "ar"
    render_dependency_warnings()
    title = "تسجيل الدخول" if rtl else "Sign in to Agnes AI"
    subtitle = "منصة ذكاء اصطناعي محلية فاخرة" if rtl else "Luxury local AI workspace"
    st.markdown(
        f'<div style="text-align:center;color:{C_MUTED};margin-bottom:1.5rem;"><h2 style="color:{C_TEXT};margin:0;">{title}</h2><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )

    _, c, _ = st.columns([1, 2, 1])
    with c:
        st.markdown('<div class="premium-card">', unsafe_allow_html=True)
        email = st.text_input("Email" if not rtl else "البريد الإلكتروني", key="login_email")
        password = st.text_input("Password" if not rtl else "كلمة المرور", type="password", key="login_password")
        if st.button("Sign In" if not rtl else "تسجيل الدخول", use_container_width=True, type="primary"):
            if email and password:
                st.session_state.user = {"email": email, "name": email.split("@")[0]}
                st.session_state["page"] = "chat"
                st.rerun()
            else:
                st.warning("Enter email and password." if not rtl else "أدخل البريد وكلمة المرور.")
        st.markdown('<div class="divider-or">OR</div>' if not rtl else '<div class="divider-or">أو</div>', unsafe_allow_html=True)
        g1, g2 = st.columns(2)
        with g1:
            if st.button("Sign in with Google" if not rtl else "تسجيل عبر Google", use_container_width=True):
                st.info("Google OAuth requires backend configuration." if not rtl else "يتطلب OAuth إعداد الخادم.")
        with g2:
            if st.button("Sign in with GitHub" if not rtl else "تسجيل عبر GitHub", use_container_width=True):
                st.info("GitHub OAuth requires backend configuration." if not rtl else "يتطلب GitHub OAuth إعداد الخادم.")
        if st.button("View pricing" if not rtl else "عرض الأسعار", use_container_width=True, key="login_pricing"):
            st.session_state["page"] = "pricing"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def render_chat() -> None:
    settings = st.session_state.settings
    rtl = settings.get("language") == "ar"
    render_dependency_warnings()
    st.markdown(f'<h3 style="color:{C_TEXT};">{"المحادثة" if rtl else "Chat"}</h3>', unsafe_allow_html=True)

    if st.session_state.get("last_api_error"):
        st.warning(st.session_state.last_api_error)

    hist = st.container(height=420)
    with hist:
        if not st.session_state.messages:
            st.caption("Start a conversation with your local model." if not rtl else "ابدأ محادثة مع نموذجك المحلي.")
        for m in st.session_state.messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            safe = html.escape(content).replace("\n", "<br/>")
            if role == "user":
                st.markdown(
                    f'<div class="chat-bubble-user"><strong>You</strong><br/>{safe}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="chat-bubble-ai"><strong>Agnes</strong><br/>{safe}</div>',
                    unsafe_allow_html=True,
                )

    can_api, _ = dependency_status()
    prompt = st.chat_input(
        "Message Agnes…" if not rtl else "اكتب رسالة…",
        disabled=not can_api,
    )
    if not can_api:
        st.warning("Enable API access by fixing the dependency warnings above." if not rtl else "راجع التحذيرات أعلاه.")

    if prompt and can_api:
        st.session_state.messages.append({"role": "user", "content": prompt})
        api_messages = [{"role": x["role"], "content": x["content"]} for x in st.session_state.messages]
        st.session_state.last_api_error = ""
        with st.spinner("Thinking…" if not rtl else "جاري المعالجة…"):
            reply = call_chat_completion(api_messages, settings)
        if _response_looks_like_error(reply):
            st.session_state.last_api_error = reply[:3000]
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "The model did not return a valid reply. See the warning above or check Settings → API URL."
                    if not rtl
                    else "لم يُرجع النموذج رداً صالحاً. راجع التحذير أعلاه أو إعدادات رابط API.",
                }
            )
        else:
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


def render_code() -> None:
    settings = st.session_state.settings
    rtl = settings.get("language") == "ar"
    render_dependency_warnings()
    st.markdown(
        f'<h3 style="color:{C_TEXT};">{"مساعد الكود" if rtl else "Developer Code Assistant"}</h3>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("last_api_error"):
        st.warning(st.session_state.last_api_error)

    code = st.text_area(
        "Editor" if not rtl else "المحرر",
        value=st.session_state.code_buffer,
        height=320,
        key="code_editor_area",
        label_visibility="collapsed",
        placeholder="# Paste or write code here\n",
    )
    st.session_state.code_buffer = code
    b1, b2 = st.columns(2)
    can_api, _ = dependency_status()
    with b1:
        gen = st.button(
            "Generate Code" if not rtl else "توليد كود",
            use_container_width=True,
            disabled=not can_api,
        )
    with b2:
        dbg = st.button(
            "Debug Code" if not rtl else "تصحيح",
            use_container_width=True,
            disabled=not can_api,
        )

    if gen and can_api:
        sys_msg = "You are an expert software engineer. Respond with concise, production-quality code and brief notes."
        usr = f"Generate or complete this code:\n\n{code}"
        msgs = [{"role": "system", "content": sys_msg}, {"role": "user", "content": usr}]
        st.session_state.last_api_error = ""
        with st.spinner("Generating…" if not rtl else "جاري التوليد…"):
            out = call_chat_completion(msgs, settings)
        if _response_looks_like_error(out):
            st.session_state.last_api_error = out[:3000]
            st.session_state.code_output = ""
        else:
            st.session_state.code_output = out
        st.rerun()

    if dbg and can_api:
        sys_msg = "You are a debugging assistant. Find issues, explain them, and suggest fixes."
        usr = f"Debug and analyze:\n\n{code}"
        msgs = [{"role": "system", "content": sys_msg}, {"role": "user", "content": usr}]
        st.session_state.last_api_error = ""
        with st.spinner("Debugging…" if not rtl else "جاري التحليل…"):
            out = call_chat_completion(msgs, settings)
        if _response_looks_like_error(out):
            st.session_state.last_api_error = out[:3000]
            st.session_state.code_output = ""
        else:
            st.session_state.code_output = out
        st.rerun()

    st.markdown(f'<p style="color:{C_MUTED};margin-top:1rem;">{"الناتج" if rtl else "Output"}</p>', unsafe_allow_html=True)
    out = st.session_state.code_output or ("No output yet." if not rtl else "لا يوجد ناتج بعد.")
    st.markdown(f'<div class="mono-out">{html.escape(out)}</div>', unsafe_allow_html=True)


def render_settings() -> None:
    rtl = st.session_state.settings.get("language") == "ar"
    render_dependency_warnings()
    st.markdown(f'<h3 style="color:{C_TEXT};">{"الإعدادات" if rtl else "Settings"}</h3>', unsafe_allow_html=True)
    s = st.session_state.settings
    st.session_state.settings["api_url"] = st.text_input(
        "Local API URL" if not rtl else "رابط واجهة API",
        value=s.get("api_url", "http://localhost:8000/v1"),
    )
    st.session_state.settings["api_key"] = st.text_input(
        "API Key (optional)" if not rtl else "مفتاح API (اختياري)",
        value=s.get("api_key", ""),
        type="password",
    )
    models = ["unsloth", "local-llm", "gpt-4o-mini", "custom"]
    cur = s.get("model", "unsloth")
    idx = models.index(cur) if cur in models else 0
    st.session_state.settings["model"] = st.selectbox(
        "Model" if not rtl else "النموذج",
        models,
        index=idx,
    )
    st.session_state.settings["temperature"] = st.slider(
        "Temperature" if not rtl else "درجة الحرارة",
        0.0,
        1.0,
        float(s.get("temperature", 0.7)),
        0.05,
    )
    st.session_state.settings["language"] = st.selectbox(
        "Interface language" if not rtl else "لغة الواجهة",
        ["en", "ar"],
        index=0 if s.get("language", "en") == "en" else 1,
    )
    if st.button("Save" if not rtl else "حفظ", use_container_width=True):
        st.success("Settings saved to session." if not rtl else "تم حفظ الإعدادات.")


def render_pricing() -> None:
    rtl = st.session_state.settings.get("language") == "ar"
    render_dependency_warnings()
    if not st.session_state.user:
        if st.button("← " + ("Sign in" if not rtl else "تسجيل الدخول"), key="pricing_back_login"):
            st.session_state["page"] = "login"
            st.rerun()
    st.markdown(f'<h3 style="color:{C_TEXT};text-align:center;">{"الخطط" if rtl else "Plans"}</h3>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="premium-card">
                <h4 style="margin:0;color:{C_TEXT};">{"Pro Plan" if not rtl else "خطة Pro"}</h4>
                <p style="font-size:1.75rem;color:{C_ACCENT};margin:0.5rem 0;">$29<span style="font-size:0.9rem;color:{C_MUTED};">/mo</span></p>
                <ul style="color:{C_MUTED};line-height:1.7;">
                    <li>{"Priority inference" if not rtl else "أولوية المعالجة"}</li>
                    <li>{"Advanced chat" if not rtl else "محادثة متقدمة"}</li>
                    <li>{"Code copilot" if not rtl else "مساعد برمجة"}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Subscribe Pro" if not rtl else "اشترك برو", use_container_width=True, key="sub_pro"):
            st.toast("Stripe / billing placeholder." if not rtl else "واجهة دفع تجريبية.")

    with c2:
        st.markdown(
            f"""
            <div class="premium-card premium-card-glow">
                <span class="badge-popular">{"Most Popular" if not rtl else "الأكثر شعبية"}</span>
                <h4 style="margin:0;color:{C_TEXT};">{"Ultra Plan" if not rtl else "خطة Ultra"}</h4>
                <p style="font-size:1.75rem;color:{C_ACCENT};margin:0.5rem 0;">$79<span style="font-size:0.9rem;color:{C_MUTED};">/mo</span></p>
                <ul style="color:{C_MUTED};line-height:1.7;">
                    <li>{"Everything in Pro" if not rtl else "كل مزايا برو"}</li>
                    <li>{"Dedicated throughput" if not rtl else "إنتاجية مخصصة"}</li>
                    <li>{"Private routing" if not rtl else "توجيه خاص"}</li>
                    <li>{"White-glove support" if not rtl else "دعم مميز"}</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Subscribe Ultra" if not rtl else "اشترك ألترا", use_container_width=True, key="sub_ultra"):
            st.toast("Ultra checkout placeholder." if not rtl else "الدفع التجريبي لألترا.")


def render_page() -> None:
    init_session_state()
    settings = st.session_state.settings
    rtl = settings.get("language") == "ar"
    inject_global_css(rtl)

    render_top_logo_bar()

    page = st.session_state.get("page", "login")
    if not st.session_state.user and page not in ("login", "pricing"):
        st.session_state["page"] = "login"
        page = "login"

    if st.session_state.user:
        render_top_navigation()

    pages: Dict[str, Callable[[], None]] = {
        "login": render_login,
        "chat": render_chat,
        "code": render_code,
        "settings": render_settings,
        "pricing": render_pricing,
    }
    pages.get(page, render_login)()


def main() -> None:
    st.set_page_config(
        page_title="Agnes AI",
        page_icon="◆",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    render_page()


if __name__ == "__main__":
    main()
