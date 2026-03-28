"""
Agnes AI — Luxurious Tech multi-page platform with Lottie login mascot.
Install deps: pip install -r requirements.txt  (includes streamlit-lottie for web deploy).
"""

from __future__ import annotations

import html
import inspect
import os
import time
from typing import Any

import requests
import streamlit as st
from streamlit_lottie import st_lottie

try:
    from st_keyup import st_keyup
except ImportError:  # pragma: no cover
    st_keyup = None  # type: ignore[misc, assignment]

_TABS_STATEFUL = "on_change" in inspect.signature(st.tabs).parameters

# Testing defaults (override with AGNES_USER / AGNES_PASS)
_DEMO_USER = os.environ.get("AGNES_USER", "admin")
_DEMO_PASS = os.environ.get("AGNES_PASS", "1234")

# Public Lottie JSON URLs (robot idle vs. shy/peek — swap URLs anytime)
_LOTTIE_IDLE_URL = os.environ.get(
    "AGNES_LOTTIE_IDLE",
    "https://assets5.lottiefiles.com/packages/lf20_V9t630.json",
)
_LOTTIE_TYPING_URL = os.environ.get(
    "AGNES_LOTTIE_TYPING",
    "https://assets9.lottiefiles.com/packages/lf20_ofhjoshi.json",
)

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "login_title": "Welcome back!",
        "login_sub": "Sign in to continue to Agnes AI",
        "username": "Email or username",
        "password": "Password",
        "sign_in": "Log In",
        "nav_chat": "Chat",
        "nav_settings": "Settings",
        "nav_upgrade": "Upgrade to Pro / Ultra",
        "logout": "Log out",
        "settings_title": "Settings",
        "dark_mode": "Dark mode (Luxurious Tech)",
        "language": "Language",
        "creativity": "AI creativity level",
        "pricing_title": "Choose your Agnes plan",
        "buy": "Buy now",
        "chat_ph_ultra": "Message Agnes…",
        "chat_ph_fast": "Message Agnes (Fast)…",
        "welcome_ar": "مرحباً ، أنا أغنيس.. كيف يمكنني مساعدتك اليوم؟",
        "welcome_en": "Hello, I'm Agnes. How can I help you today?",
        "reply_ultra": "Agnes-Ultra — connect your model here for full reasoning.",
        "reply_fast": "Agnes-Fast — wire your streaming endpoint for snappy replies.",
        "mascot_hint": "The character reacts while you type your password.",
        "tagline": "Your Sophisticated Intelligent Assistant",
        "lottie_err": "Could not load animation. Check network/CORS on deploy.",
        "login_demo_hint": "Demo: username **admin**, password **1234**.",
    },
    "ar": {
        "login_title": "مرحباً بعودتك!",
        "login_sub": "سجّل الدخول للمتابعة إلى أغنيس",
        "username": "البريد أو اسم المستخدم",
        "password": "كلمة المرور",
        "sign_in": "تسجيل الدخول",
        "nav_chat": "محادثة",
        "nav_settings": "الإعدادات",
        "nav_upgrade": "الترقية إلى Pro / Ultra",
        "logout": "تسجيل الخروج",
        "settings_title": "الإعدادات",
        "dark_mode": "الوضع الداكن (فاخر تقني)",
        "language": "اللغة",
        "creativity": "مستوى إبداع الذكاء الاصطناعي",
        "pricing_title": "اختر باقة أغنيس",
        "buy": "اشترِ الآن",
        "chat_ph_ultra": "رسالة إلى أغنيس…",
        "chat_ph_fast": "رسالة إلى أغنيس (سريع)…",
        "welcome_ar": "مرحباً ، أنا أغنيس.. كيف يمكنني مساعدتك اليوم؟",
        "welcome_en": "Hello, I'm Agnes. How can I help you today?",
        "reply_ultra": "Agnes-Ultra — اربط نموذجك هنا للاستدلال الكامل.",
        "reply_fast": "Agnes-Fast — اربط بث الاستجابة السريع للإنتاج.",
        "mascot_hint": "الشخصية تتفاعل أثناء كتابة كلمة المرور.",
        "tagline": "مساعدتك الذكية الأنيقة",
        "lottie_err": "تعذر تحميل الرسوم المتحركة. تحقق من الشبكة.",
        "login_demo_hint": "تجربة: اسم المستخدم **admin** وكلمة المرور **1234**.",
    },
}


def tr(key: str) -> str:
    lang = st.session_state.get("language", "en")
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)


@st.cache_data(ttl=3600, show_spinner=False)
def load_lottie_url(url: str) -> dict[str, Any] | None:
    try:
        r = requests.get(url, timeout=12)
        if r.status_code != 200:
            return None
        return r.json()
    except (requests.RequestException, ValueError):
        return None


def inject_global_css() -> None:
    dark = st.session_state.get("dark_mode", True)
    logged_in = st.session_state.get("logged_in", False)
    rtl = st.session_state.get("language") == "ar"

    if dark:
        bg = "#000000"
        text = "#F4F2EF"
        muted = "#9A8F88"
        accent = "#00E5FF"
        input_bg = "#0D0D0D"
    else:
        bg = "#F5F1EC"
        text = "#1A1412"
        muted = "#5C534D"
        accent = "#00A8C6"
        input_bg = "#FAFAFA"

    hide_sb = (
        '[data-testid="stSidebar"] { display: none !important; }'
        if not logged_in
        else ""
    )

    st.markdown(
        f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --lux-bg: {bg};
    --lux-text: {text};
    --lux-muted: {muted};
    --lux-accent: {accent};
    --lux-input-bg: {input_bg};
  }}
  html {{ zoom: 0.92; }}
  .stApp, [data-testid="stAppViewContainer"], .main {{
    background: var(--lux-bg) !important;
    color: var(--lux-text) !important;
  }}
  .main .block-container {{
    padding-top: 0.75rem;
    padding-bottom: 4rem;
    max-width: 72rem;
    direction: {"rtl" if rtl else "ltr"};
  }}
  .font-ar, [lang="ar"], .rtl-block {{
    font-family: "Cairo", system-ui, sans-serif !important;
  }}
  body, .stApp {{ font-family: "Plus Jakarta Sans", "Segoe UI", system-ui, sans-serif; }}
  .login-rtl-fix[dir="rtl"] {{ text-align: right; unicode-bidi: plaintext; }}
  {hide_sb}
  [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0A0A0A 0%, #12100E 100%) !important;
    border-right: 1px solid rgba(0, 229, 255, 0.12) !important;
  }}
  [data-testid="stSidebar"] .block-container {{ padding-top: 1.25rem; }}
  [data-testid="stSidebar"] * {{ color: #EAE6E1 !important; }}
  .stTextInput input, .stTextArea textarea, [data-baseweb="input"] {{
    background: var(--lux-input-bg) !important;
    color: var(--lux-text) !important;
    border-color: rgba(0, 229, 255, 0.45) !important;
    border-radius: 10px !important;
  }}
  .stTextInput input:focus, .stTextArea textarea:focus, [data-baseweb="input"]:focus {{
    border-color: var(--lux-accent) !important;
    box-shadow: 0 0 0 1px var(--lux-accent) !important;
    outline: none !important;
  }}
  [data-testid="stChatInput"] {{
    background: var(--lux-input-bg) !important;
    border: 1px solid rgba(0, 229, 255, 0.45) !important;
    border-radius: 12px !important;
  }}
  [data-testid="stChatInput"] textarea {{
    color: var(--lux-text) !important;
    caret-color: var(--lux-accent);
  }}
  .stTabs [data-baseweb="tab-list"] {{
    gap: 0; background: transparent;
    border-bottom: 1px solid rgba(0, 229, 255, 0.2);
  }}
  .stTabs [data-baseweb="tab"] {{
    color: var(--lux-muted) !important; font-weight: 600; font-size: 0.88rem;
    padding: 0.5rem 1rem !important; background: transparent !important;
  }}
  .stTabs [aria-selected="true"] {{
    color: var(--lux-accent) !important;
    border-bottom: 2px solid var(--lux-accent) !important;
    border-radius: 0 !important;
  }}
  .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}
</style>
        """,
        unsafe_allow_html=True,
    )


def init_session() -> None:
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    defaults: dict[str, Any] = {
        "nav_slug": "chat",
        "dark_mode": True,
        "language": "en",
        "creativity": 0.65,
        "active_model": "Agnes-Ultra",
        "messages": None,
        "payment_toast": None,
        "checkout_plan": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if not st.session_state.get("_nav_v2"):
        st.session_state.pop("nav_page", None)
        st.session_state.pop("nav_page_radio", None)
        st.session_state.pop("authenticated", None)
        st.session_state._nav_v2 = True
    if "login_username" not in st.session_state:
        st.session_state["login_username"] = _DEMO_USER

    if st.session_state.messages is None:
        lang0 = st.session_state.language
        if lang0 == "ar":
            wtext = STRINGS["ar"]["welcome_ar"]
            rtl = True
        else:
            wtext = STRINGS["en"]["welcome_en"]
            rtl = False
        st.session_state.messages = [
            {"role": "assistant", "text": wtext, "force_rtl": rtl}
        ]


def render_login_lottie_pw_len(pw_len: int) -> None:
    """Swap Lottie source when the user types in the password field."""
    use_typing = pw_len > 0
    url = _LOTTIE_TYPING_URL if use_typing else _LOTTIE_IDLE_URL
    data = load_lottie_url(url)
    if data is None:
        st.warning(tr("lottie_err"))
        return
    st_lottie(
        data,
        speed=1,
        reverse=False,
        loop=True,
        quality="medium",
        height=380,
        width=None,
        key=f"agnes_lottie_{'type' if use_typing else 'idle'}_{url[-24:]}",
    )


def render_login() -> None:
    pw_key = "login_password_live"
    st.selectbox(
        tr("language"),
        ["en", "ar"],
        format_func=lambda x: "English" if x == "en" else "العربية",
        index=0 if st.session_state.get("language", "en") == "en" else 1,
        key="language",
    )
    pw_len = len(str(st.session_state.get(pw_key, "")))

    st.markdown(
        """
<style>
  .welcome-head h2 {
    margin: 0 0 0.35rem 0; font-size: 1.55rem; font-weight: 700; color: #FFFFFF;
    letter-spacing: 0.02em;
  }
  .welcome-head p.sub { margin: 0 0 0.85rem 0; color: #B8A99A; font-size: 0.92rem; }
</style>
        """,
        unsafe_allow_html=True,
    )

    c_mascot, c_card = st.columns([1.05, 1.0], gap="large")

    with c_mascot:
        st.markdown(
            '<p style="color:#00E5FF;font-size:0.72rem;letter-spacing:0.14em;text-transform:uppercase;margin:0 0 0.5rem;">AI Character</p>',
            unsafe_allow_html=True,
        )
        render_login_lottie_pw_len(pw_len)

    with c_card:
        is_ar = st.session_state.get("language") == "ar"
        with st.container(border=True):
            rh = f'<div class="welcome-head login-rtl-fix font-ar" dir="rtl" lang="ar">' if is_ar else '<div class="welcome-head">'
            st.markdown(
                rh
                + f'<h2 class="font-ar">{html.escape(tr("login_title"))}</h2>'
                f'<p class="sub font-ar">{html.escape(tr("login_sub"))}</p></div>',
                unsafe_allow_html=True,
            )
            st.caption(tr("login_demo_hint"))

            if st_keyup is not None:
                st_keyup(tr("password"), key=pw_key, debounce=0)
                st.caption(tr("mascot_hint"))
            else:
                st.text_input(tr("password"), type="password", key=pw_key)
                st.caption("Install **streamlit-keyup** so the Lottie swaps on each keystroke.")

            with st.form("login_form_agnes", clear_on_submit=False):
                username = st.text_input(tr("username"), key="login_username")
                submitted = st.form_submit_button(
                    tr("sign_in"), type="primary", use_container_width=True
                )
                if submitted:
                    password_value = str(st.session_state.get(pw_key, ""))
                    if (
                        username.strip() == _DEMO_USER
                        and password_value == _DEMO_PASS
                    ):
                        st.session_state["logged_in"] = True
                        st.rerun()
                    else:
                        st.error(
                            f"Invalid credentials. Use username `{_DEMO_USER}` and password `{_DEMO_PASS}`."
                        )


def _nav_label(slug: str) -> str:
    return {
        "chat": "💬 " + tr("nav_chat"),
        "settings": "⚙️ " + tr("nav_settings"),
        "upgrade": "💎 " + tr("nav_upgrade"),
    }[slug]


def render_sidebar() -> None:
    st.sidebar.markdown("### ✦ **Agnes AI**")
    st.sidebar.markdown(
        '<p style="color:#9A8F88;font-size:0.82rem;margin-top:-0.5rem;">Platform</p>',
        unsafe_allow_html=True,
    )
    slugs = ("chat", "settings", "upgrade")
    if st.session_state.nav_slug not in slugs:
        st.session_state.nav_slug = "chat"
    st.sidebar.radio(
        "Navigation",
        list(slugs),
        format_func=_nav_label,
        key="nav_slug",
        label_visibility="collapsed",
    )
    st.sidebar.divider()
    if st.sidebar.button(tr("logout"), use_container_width=True):
        st.session_state["logged_in"] = False
        for k in (
            "login_username",
            "login_password_live",
            "nav_slug",
            "agnes_model_tabs",
            "agnes_model_radio",
            "checkout_plan",
            "payment_toast",
        ):
            st.session_state.pop(k, None)
        st.session_state.nav_slug = "chat"
        st.rerun()


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
          <p class="skill-card-title">{html.escape(title)}</p>
          <p class="skill-card-sub">{html.escape(sub)}</p>
        </div>"""
    st.markdown(
        f"""
<style>
  .skills-scroll {{
    display: flex; gap: 0.75rem; overflow-x: auto; padding: 0.5rem 0 1rem;
    scrollbar-color: #00E5FF #0A0A0A; scrollbar-width: thin;
  }}
  .skill-card {{
    flex: 0 0 auto; width: 158px; padding: 0.9rem 1rem; background: #1A1412;
    border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 12px;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.35), 0 0 0 1px rgba(0,0,0,0.25);
  }}
  .skill-card-title {{
    font-size: 0.9rem; font-weight: 700; color: #FFFFFF; margin: 0 0 0.35rem;
  }}
  .skill-card-sub {{ font-size: 0.72rem; color: #B8A99A; margin: 0; line-height: 1.35; }}
</style>
<div class="skills-scroll">{cards}</div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_bubbles() -> None:
    lang = st.session_state.get("language", "en")
    parts = ['<div class="agnes-chat-stack">']
    for m in st.session_state.messages:
        safe = html.escape(m["text"])
        force_rtl = m.get("force_rtl") or (lang == "ar" and m["role"] == "assistant")
        dattr = ' dir="rtl" lang="ar" class="rtl-block font-ar"' if force_rtl else ""
        if m["role"] == "assistant":
            parts.append(
                f'<div class="bubble-row assistant"><div class="bubble-agnes"{dattr}>{safe}</div></div>'
            )
        else:
            u_rtl = lang == "ar"
            ud = ' dir="rtl" lang="ar" class="rtl-block font-ar"' if u_rtl else ""
            parts.append(
                f'<div class="bubble-row user"><div class="bubble-user"{ud}>{safe}</div></div>'
            )
    parts.append("</div>")
    st.markdown(
        """
<style>
  .agnes-chat-stack {
    display: flex; flex-direction: column; gap: 0.75rem; margin: 1rem 0; min-height: 200px;
  }
  .bubble-row { display: flex; width: 100%; }
  .bubble-row.user { justify-content: flex-end; }
  .bubble-row.assistant { justify-content: flex-start; }
  .bubble-agnes {
    max-width: 92%; padding: 0.75rem 1rem; background: #1A1412; color: #FFFFFF;
    border: 1px solid rgba(0, 229, 255, 0.22); border-radius: 14px 14px 14px 4px;
    font-size: 0.95rem; line-height: 1.65; text-align: start;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
  }
  .bubble-user {
    max-width: 88%; padding: 0.75rem 1rem; background: #0A0A0A; color: #F4F2EF;
    border: 1px solid rgba(0, 229, 255, 0.45); border-radius: 14px 14px 4px 14px;
    font-size: 0.95rem; line-height: 1.5;
  }
  .bubble-agnes[dir="rtl"], .bubble-user[dir="rtl"] {
    text-align: right; unicode-bidi: plaintext;
  }
</style>
        """
        + "".join(parts),
        unsafe_allow_html=True,
    )


def sync_welcome_message_language() -> None:
    msgs = st.session_state.messages
    if not msgs:
        return
    first = msgs[0]
    if first.get("role") != "assistant":
        return
    if st.session_state.language == "ar":
        first["text"] = STRINGS["ar"]["welcome_ar"]
        first["force_rtl"] = True
    else:
        first["text"] = STRINGS["en"]["welcome_en"]
        first["force_rtl"] = False


def render_chat_page() -> None:
    sync_welcome_message_language()
    st.markdown(
        '<p style="font-size:1.35rem;font-weight:700;color:#FFFFFF;letter-spacing:0.03em;">Agnes</p>',
        unsafe_allow_html=True,
    )
    st.caption(tr("tagline"))

    creativity = float(st.session_state.get("creativity", 0.65))
    st.caption(f"Creativity index: {creativity:.2f} (map to model temperature)")

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
        _idx = 0 if st.session_state.get("active_model", "Agnes-Ultra") == "Agnes-Ultra" else 1
        st.session_state.active_model = st.radio(
            "Model",
            ["Agnes-Ultra", "Agnes-Fast"],
            horizontal=True,
            label_visibility="collapsed",
            index=_idx,
            key="agnes_model_radio",
        )

    render_skills_carousel()
    render_chat_bubbles()

    ph = (
        tr("chat_ph_ultra")
        if st.session_state.get("active_model") == "Agnes-Ultra"
        else tr("chat_ph_fast")
    )
    prompt = st.chat_input(ph)
    if prompt:
        st.session_state.messages.append({"role": "user", "text": prompt})
        reply = (
            tr("reply_ultra")
            if st.session_state.active_model == "Agnes-Ultra"
            else tr("reply_fast")
        )
        st.session_state.messages.append(
            {"role": "assistant", "text": reply + f" (creativity {creativity:.2f})"}
        )
        st.rerun()


def render_settings_page() -> None:
    st.header(tr("settings_title"))
    st.session_state.dark_mode = st.toggle(
        tr("dark_mode"), value=st.session_state.dark_mode
    )
    st.selectbox(
        tr("language"),
        ["en", "ar"],
        format_func=lambda x: "English" if x == "en" else "العربية",
        index=0 if st.session_state.get("language", "en") == "en" else 1,
        key="language",
    )
    st.session_state.creativity = st.slider(
        tr("creativity"),
        min_value=0.0,
        max_value=1.0,
        value=float(st.session_state.creativity),
        step=0.05,
    )
    st.info("Theme updates immediately. Sidebar labels follow your language.")


def _payment_dialog_body(plan_key: str) -> None:
    st.markdown(
        f"**{html.escape(plan_key)}** — secure demo checkout.",
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="color:#9A8F88;font-size:0.9rem;">No real charges. Confirm to simulate success.</p>',
        unsafe_allow_html=True,
    )
    c_ok, c_cancel = st.columns(2)
    with c_ok:
        if st.button("Confirm payment", type="primary", use_container_width=True):
            st.session_state.payment_toast = plan_key
            st.session_state.checkout_plan = None
            time.sleep(0.35)
            st.rerun()
    with c_cancel:
        if st.button("Cancel", use_container_width=True):
            st.session_state.checkout_plan = None
            st.rerun()


if hasattr(st, "dialog"):
    payment_dialog = st.dialog("💳 Checkout")(_payment_dialog_body)
else:  # pragma: no cover

    def payment_dialog(plan_key: str) -> None:
        st.session_state.checkout_plan = plan_key


def render_upgrade_page() -> None:
    st.markdown(
        f'<h2 class="font-ar" style="color:#FFFFFF;margin-bottom:0.25rem;">{html.escape(tr("pricing_title"))}</h2>',
        unsafe_allow_html=True,
    )
    if st.session_state.get("checkout_plan") and not hasattr(st, "dialog"):
        st.markdown("#### 💳 Checkout")
        _payment_dialog_body(st.session_state.checkout_plan)

    if st.session_state.get("payment_toast"):
        st.success(
            f"Payment successful — {st.session_state.payment_toast}. Welcome to Agnes."
        )
        if st.button("Dismiss"):
            st.session_state.payment_toast = None
            st.rerun()

    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(
            """
<div style="background:#1A1412;border:1px solid rgba(0,229,255,0.18);border-radius:16px;padding:1.5rem;min-height:320px;">
  <h3 style="color:#FFFFFF;margin-top:0;">Agnes Pro</h3>
  <p style="color:#B8A99A;font-size:0.95rem;">For power users who want speed and depth.</p>
  <ul style="color:#EAE6E1;line-height:1.7;">
    <li>Faster response</li><li>Advanced memory</li><li>Priority queue</li><li>Expanded context</li>
  </ul>
  <p style="color:#00E5FF;font-size:1.35rem;font-weight:700;">$12<span style="font-size:0.85rem;color:#9A8F88">/mo</span></p>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(tr("buy") + " — Pro", key="buy_pro", use_container_width=True):
            payment_dialog("Agnes Pro")
    with c2:
        st.markdown(
            """
<div style="background:linear-gradient(145deg,#0A1A1C 0%,#1A1412 55%,#0E2226 100%);
 border:1px solid rgba(0,229,255,0.55);border-radius:16px;padding:1.5rem;min-height:320px;
 box-shadow:0 0 40px rgba(0,229,255,0.12), inset 0 1px 0 rgba(0,229,255,0.2);position:relative;overflow:hidden;">
  <div style="position:absolute;top:12px;right:14px;font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;
    color:#001018;background:#00E5FF;padding:0.25rem 0.55rem;border-radius:999px;font-weight:700;">Ultra</div>
  <h3 style="color:#00E5FF;margin-top:0;">Agnes Ultra</h3>
  <p style="color:#B8A99A;font-size:0.95rem;">Electric performance for teams and creators.</p>
  <ul style="color:#EAE6E1;line-height:1.7;">
    <li><span style="color:#00E5FF">Fastest</span> inference tier</li>
    <li>Long-horizon memory & tools</li><li>Dedicated quality lane</li><li>Concierge onboarding</li>
  </ul>
  <p style="color:#00E5FF;font-size:1.35rem;font-weight:700;">$29<span style="font-size:0.85rem;color:#9A8F88">/mo</span></p>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button(tr("buy") + " — Ultra", key="buy_ultra", use_container_width=True):
            payment_dialog("Agnes Ultra")


def main() -> None:
    st.set_page_config(
        page_title="Agnes AI — Platform",
        page_icon="✦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_session()
    inject_global_css()

    if not st.session_state.get("logged_in"):
        render_login()
        return

    render_sidebar()
    slug = st.session_state.get("nav_slug", "chat")
    if slug == "settings":
        render_settings_page()
    elif slug == "upgrade":
        render_upgrade_page()
    else:
        render_chat_page()


if __name__ == "__main__":
    main()



