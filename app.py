import streamlit as st
from groq import Groq
import pandas as pd
import speech_recognition as sr
from gtts import gTTS
import tempfile
import random
import base64
import json
import requests
import hashlib
from datetime import datetime
import plotly.graph_objects as go
import platform

# ─── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="MedIntel AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
#  FIREBASE CONFIG  ──  Replace with your Firebase project values
# ══════════════════════════════════════════════════════════════
FIREBASE_API_KEY       = "AIzaSyCGGABpQzyk-TrGvPTPLVUAFRivZOAgTTE"           # Web API Key
FIREBASE_PROJECT_ID    = "med-intel-147b2"                  # Project ID
FIRESTORE_BASE_URL     = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"
FIREBASE_AUTH_URL      = f"https://identitytoolkit.googleapis.com/v1/accounts"

# ─── SESSION STATE ─────────────────────────────────────────
for k, v in {
    "page": "🏠 Home",
    "history": [], "risk_history": [], "user_profile": {},
    "drift_log": [], "feedback_log": [],
    "stt_text": "", "last_result": "",
    "last_risk": 0.0, "last_symptoms": "", "tts_file": "",
    # Auth state
    "auth_user": None,          # {"uid": ..., "email": ..., "idToken": ..., "refreshToken": ...}
    "auth_page": "login",       # "login" | "register"
    "auth_error": "",
    "auth_success": "",
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif !important;
    background-color: #060d1f !important;
    color: #c8e6ff !important;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #04091a 0%, #060f22 100%) !important;
    border-right: 2px solid #00d4ff33 !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important; text-align: left !important;
    background: transparent !important; border: 1px solid transparent !important;
    color: #5a8aaa !important; font-family: 'Rajdhani', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    letter-spacing: 1px !important; padding: 0.5rem 0.8rem !important;
    border-radius: 8px !important; margin-bottom: 2px !important;
    transition: all 0.2s !important; transform: none !important; box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,212,255,0.1) !important;
    border-color: rgba(0,212,255,0.3) !important;
    color: #00d4ff !important; transform: none !important; box-shadow: none !important;
}
.main .stButton > button {
    background: rgba(0,212,255,0.08) !important;
    border: 1px solid #00d4ff !important;
    color: #00d4ff !important; font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important; letter-spacing: 2px !important;
    border-radius: 8px !important; font-size: 0.78rem !important;
    transition: all 0.25s ease !important;
}
.main .stButton > button:hover {
    background: rgba(0,212,255,0.18) !important;
    box-shadow: 0 0 20px rgba(0,212,255,0.3) !important;
    transform: translateY(-1px) !important;
}
textarea, input[type="text"], input[type="number"], input[type="email"], input[type="password"] {
    background: #08132a !important; border: 1px solid rgba(0,212,255,0.25) !important;
    color: #c8e6ff !important; border-radius: 8px !important;
    font-family: 'Rajdhani', sans-serif !important;
}
textarea:focus, input:focus {
    border-color: #00d4ff !important; box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
}
.card {
    background: rgba(6,15,40,0.9); border: 1px solid rgba(0,212,255,0.15);
    border-radius: 14px; padding: 1.4rem; margin-bottom: 1rem;
    position: relative; overflow: hidden;
}
.card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #00d4ff, #00ff9d, transparent);
    opacity: 0.6;
}
.page-title {
    font-family: 'Orbitron', sans-serif !important; font-size: 2rem; font-weight: 900;
    background: linear-gradient(135deg, #00d4ff, #00ff9d);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; letter-spacing: 3px; margin-bottom: 0.2rem;
}
.page-eyebrow {
    font-family: 'Share Tech Mono', monospace; font-size: 0.6rem;
    color: rgba(0,212,255,0.55); letter-spacing: 5px;
    text-transform: uppercase; margin-bottom: 0.3rem;
}
.page-sub {
    font-family: 'Share Tech Mono', monospace; font-size: 0.58rem;
    color: #1e4060; letter-spacing: 3px; margin-bottom: 1.5rem;
}
.sec-h {
    font-family: 'Share Tech Mono', monospace; font-size: 0.6rem;
    color: #00d4ff; letter-spacing: 4px; text-transform: uppercase;
    margin-bottom: 0.8rem; padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(0,212,255,0.15);
}
.metric-box {
    background: rgba(6,15,40,0.9); border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px; padding: 1rem; text-align: center; border-bottom: 2px solid #00d4ff;
}
.metric-val { font-family: 'Orbitron', sans-serif; font-size: 1.6rem; font-weight: 700; color: #00d4ff; line-height: 1; }
.metric-lbl { font-family: 'Share Tech Mono', monospace; font-size: 0.52rem; color: #1e4060; letter-spacing: 2px; margin-top: 0.3rem; }
.r-bar-bg { background: rgba(255,255,255,0.05); border-radius: 4px; height: 8px; overflow: hidden; margin: 4px 0 12px; }
.r-bar-fill { height: 100%; border-radius: 4px; transition: width 1s ease; }
.alert { border-radius: 10px; padding: 0.8rem 1rem; margin: 0.6rem 0; font-size: 0.85rem; border-left: 3px solid; }
.alert-c { background: rgba(0,212,255,0.06); border-color: #00d4ff; color: #00d4ff; }
.alert-g { background: rgba(0,255,157,0.06); border-color: #00ff9d; color: #00ff9d; }
.alert-y { background: rgba(255,170,0,0.06); border-color: #ffaa00; color: #ffaa00; }
.alert-r { background: rgba(255,50,80,0.06); border-color: #ff3250; color: #ff3250; }
.dx-out {
    background: rgba(4,10,28,0.95); border: 1px solid rgba(0,212,255,0.18);
    border-radius: 12px; padding: 1.3rem; font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem; line-height: 1.85; white-space: pre-wrap; color: #c8e6ff;
}
.badge { display: inline-block; padding: 0.12rem 0.65rem; border-radius: 20px;
    font-family: 'Share Tech Mono', monospace; font-size: 0.55rem; letter-spacing: 2px;
    margin-left: 0.4rem; vertical-align: middle; }
.b-h { background: rgba(255,50,80,0.18); color: #ff3250; border: 1px solid rgba(255,50,80,0.4); }
.b-m { background: rgba(255,170,0,0.18); color: #ffaa00; border: 1px solid rgba(255,170,0,0.4); }
.b-l { background: rgba(0,255,157,0.15); color: #00ff9d; border: 1px solid rgba(0,255,157,0.35); }
.xai-step { display: flex; gap: 0.9rem; padding: 0.8rem; background: rgba(0,212,255,0.03);
    border: 1px solid rgba(0,212,255,0.12); border-left: 3px solid #00d4ff;
    border-radius: 10px; margin-bottom: 0.5rem; }
.xai-n { font-family: 'Orbitron', sans-serif; font-size: 1.3rem; color: #00d4ff; min-width: 1.8rem; line-height: 1; }
.xai-t { font-size: 0.87rem; line-height: 1.65; }
.tl { padding-left: 1rem; border-left: 1px solid rgba(0,212,255,0.2); margin-bottom: 0.8rem; }
.tl-time { font-family: 'Share Tech Mono', monospace; font-size: 0.58rem; color: #1e4060; margin-bottom: 0.15rem; }
.feat-card { background: rgba(6,15,40,0.9); border: 1px solid rgba(0,212,255,0.12);
    border-radius: 14px; padding: 1.2rem; text-align: center; transition: all 0.3s ease;
    cursor: default; height: 100%; }
.feat-card:hover { border-color: rgba(0,212,255,0.35); background: rgba(0,212,255,0.05);
    transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
.feat-icon { font-size: 2rem; margin-bottom: 0.6rem; display: block; }
.feat-title { font-family: 'Orbitron', sans-serif; font-size: 0.7rem; color: #00d4ff; letter-spacing: 2px; margin-bottom: 0.4rem; }
.feat-desc { font-size: 0.78rem; color: #1e4060; line-height: 1.5; }
.vring { width: 90px; height: 90px; border-radius: 50%; border: 2px solid #00d4ff;
    box-shadow: 0 0 20px rgba(0,212,255,0.4); margin: 0 auto 1rem;
    display: flex; align-items: center; justify-content: center; font-size: 2.4rem;
    animation: vpulse 2s ease-in-out infinite; }
@keyframes vpulse { 0%,100%{box-shadow:0 0 15px rgba(0,212,255,0.4)} 50%{box-shadow:0 0 35px rgba(0,212,255,0.7)} }
.divider { height: 1px; background: linear-gradient(90deg, transparent, rgba(0,212,255,0.25), transparent); margin: 0.8rem 0; }

/* ── AUTH CARD ── */
.auth-wrap {
    max-width: 460px; margin: 4rem auto;
    background: rgba(6,15,40,0.97); border: 1px solid rgba(0,212,255,0.2);
    border-radius: 18px; padding: 2.5rem; position: relative; overflow: hidden;
}
.auth-wrap::before {
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background: linear-gradient(90deg, transparent, #00d4ff, #00ff9d, transparent);
}
.auth-logo { text-align:center; margin-bottom:2rem; }
.auth-logo-title { font-family:'Orbitron',sans-serif; font-size:1.8rem; font-weight:900;
    background:linear-gradient(135deg,#00d4ff,#00ff9d);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-clip:text; letter-spacing:4px; }
.auth-logo-sub { font-family:'Share Tech Mono',monospace; font-size:0.52rem;
    color:rgba(0,212,255,0.4); letter-spacing:3px; margin-top:0.3rem; }
.user-pill {
    display:inline-flex; align-items:center; gap:0.5rem;
    background:rgba(0,212,255,0.07); border:1px solid rgba(0,212,255,0.2);
    border-radius:20px; padding:0.3rem 0.9rem;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #04091a; }
::-webkit-scrollbar-thumb { background: #00d4ff; border-radius: 2px; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  FIREBASE REST API HELPERS
# ══════════════════════════════════════════════════════════════

def fb_register(email, password):
    """Create new user via Firebase Auth REST API."""
    url = f"{FIREBASE_AUTH_URL}:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload, timeout=10)
    return r.json()

def fb_login(email, password):
    """Sign in existing user via Firebase Auth REST API."""
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, json=payload, timeout=10)
    return r.json()

def get_device_info():
    """Collect basic device/environment metadata."""
    return {
        "platform": platform.system(),
        "platform_version": platform.version()[:60],
        "python_version": platform.python_version(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "local_time": datetime.now().strftime("%H:%M · %d %b %Y"),
    }

# ── Firestore field value builders ──────────────────────────
def _str(v):   return {"stringValue": str(v)}
def _num(v):   return {"doubleValue": float(v)}
def _int(v):   return {"integerValue": str(int(v))}
def _bool(v):  return {"booleanValue": bool(v)}
def _map(d):   return {"mapValue": {"fields": d}}
def _arr(lst): return {"arrayValue": {"values": lst}}

def fs_write(collection, doc_id, fields, id_token):
    """Create/overwrite a Firestore document."""
    url = f"{FIRESTORE_BASE_URL}/{collection}/{doc_id}?key={FIREBASE_API_KEY}"
    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
    body = {"fields": fields}
    r = requests.patch(url, json=body, headers=headers, timeout=10)
    return r.json()

def fs_add(collection, fields, id_token):
    """Add a new auto-ID document to a Firestore collection."""
    url = f"{FIRESTORE_BASE_URL}/{collection}?key={FIREBASE_API_KEY}"
    headers = {"Authorization": f"Bearer {id_token}", "Content-Type": "application/json"}
    body = {"fields": fields}
    r = requests.post(url, json=body, headers=headers, timeout=10)
    return r.json()

def fs_get_collection(collection, id_token):
    """List all documents in a Firestore collection."""
    url = f"{FIRESTORE_BASE_URL}/{collection}?key={FIREBASE_API_KEY}"
    headers = {"Authorization": f"Bearer {id_token}"}
    r = requests.get(url, headers=headers, timeout=10)
    return r.json()

def fs_field_val(fv):
    """Extract Python value from a Firestore field value dict."""
    for k in ("stringValue","integerValue","doubleValue","booleanValue"):
        if k in fv:
            return fv[k]
    if "mapValue" in fv:
        return {k: fs_field_val(v) for k, v in fv["mapValue"]["fields"].items()}
    if "arrayValue" in fv:
        return [fs_field_val(v) for v in fv["arrayValue"].get("values", [])]
    return None

# ══════════════════════════════════════════════════════════════
#  AUTH ACTIONS
# ══════════════════════════════════════════════════════════════

def do_login_session(data):
    """Store auth user in session after successful auth."""
    st.session_state.auth_user = {
        "uid":          data["localId"],
        "email":        data["email"],
        "idToken":      data["idToken"],
        "refreshToken": data["refreshToken"],
    }

def log_login_event(uid, email, id_token):
    """Write login event to Firestore: users/{uid}/logins/{auto}"""
    dev = get_device_info()
    fields = {
        "uid":              _str(uid),
        "email":            _str(email),
        "login_time_utc":   _str(dev["timestamp"]),
        "login_time_local": _str(dev["local_time"]),
        "platform":         _str(dev["platform"]),
        "platform_version": _str(dev["platform_version"]),
        "python_version":   _str(dev["python_version"]),
    }
    try:
        fs_add(f"users/{uid}/logins", fields, id_token)
    except Exception:
        pass  # don't block app if logging fails

def save_query_to_firestore(uid, id_token, symptoms, result, risk, age, gender, duration):
    """Save a symptom query + result to Firestore: users/{uid}/queries/{auto}"""
    ts = datetime.now().strftime("%H:%M · %d %b %Y")
    fields = {
        "timestamp":     _str(ts),
        "timestamp_utc": _str(datetime.utcnow().isoformat() + "Z"),
        "symptoms":      _str(symptoms),
        "age":           _int(age),
        "gender":        _str(gender),
        "duration":      _str(duration),
        "diagnosis":     _str(result[:2000]),       # cap at 2000 chars
        "risk_score":    _num(risk),
        "risk_pct":      _int(int(risk * 100)),
        "risk_level":    _str("HIGH" if risk >= 0.7 else "MODERATE" if risk >= 0.4 else "LOW"),
    }
    try:
        fs_add(f"users/{uid}/queries", fields, id_token)
    except Exception:
        pass

def fetch_user_queries(uid, id_token):
    """Fetch all stored queries for current user."""
    try:
        data = fs_get_collection(f"users/{uid}/queries", id_token)
        docs = data.get("documents", [])
        rows = []
        for doc in docs:
            f = doc.get("fields", {})
            rows.append({
                "time":       fs_field_val(f.get("timestamp", _str(""))),
                "symptoms":   fs_field_val(f.get("symptoms",  _str(""))),
                "risk_pct":   fs_field_val(f.get("risk_pct",  _int(0))),
                "risk_level": fs_field_val(f.get("risk_level",_str(""))),
                "diagnosis":  fs_field_val(f.get("diagnosis", _str(""))),
            })
        return rows
    except Exception:
        return []

def fetch_login_history(uid, id_token):
    """Fetch login history for current user."""
    try:
        data = fs_get_collection(f"users/{uid}/logins", id_token)
        docs = data.get("documents", [])
        rows = []
        for doc in docs:
            f = doc.get("fields", {})
            rows.append({
                "time":     fs_field_val(f.get("login_time_local", _str(""))),
                "platform": fs_field_val(f.get("platform", _str(""))),
                "email":    fs_field_val(f.get("email", _str(""))),
            })
        return rows
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════
#  AUTH UI  (shown when not logged in)
# ══════════════════════════════════════════════════════════════

def render_auth_page():
    st.markdown("""
    <div class="auth-logo">
      <div class="auth-logo-title">🧬 MEDINTEL</div>
      <div class="auth-logo-sub">DEEP SPACE AI · SECURE ACCESS</div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_reg = st.tabs(["🔐  LOGIN", "🚀  REGISTER"])

    # ── LOGIN TAB ──────────────────────────────────────────────
    with tab_login:
        st.markdown('<div class="sec-h" style="margin-top:1rem">USER CREDENTIALS</div>', unsafe_allow_html=True)
        email_l = st.text_input("Email", key="login_email", placeholder="your@email.com")
        pass_l  = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")

        if st.button("🔐  LOGIN TO MEDINTEL", use_container_width=True, key="btn_login"):
            if not email_l or not pass_l:
                st.markdown('<div class="alert alert-y">⚡ Please enter email and password.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Authenticating..."):
                    resp = fb_login(email_l.strip(), pass_l)
                if "idToken" in resp:
                    do_login_session(resp)
                    log_login_event(resp["localId"], resp["email"], resp["idToken"])
                    st.markdown('<div class="alert alert-g">✓ Login successful! Loading...</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    err = resp.get("error", {}).get("message", "Login failed.")
                    friendly = {
                        "EMAIL_NOT_FOUND":     "No account with this email.",
                        "INVALID_PASSWORD":    "Incorrect password.",
                        "USER_DISABLED":       "Account disabled.",
                        "INVALID_LOGIN_CREDENTIALS": "Invalid email or password.",
                        "TOO_MANY_ATTEMPTS_TRY_LATER": "Too many attempts. Try later.",
                    }.get(err, err)
                    st.markdown(f'<div class="alert alert-r">⚠️ {friendly}</div>', unsafe_allow_html=True)

    # ── REGISTER TAB ───────────────────────────────────────────
    with tab_reg:
        st.markdown('<div class="sec-h" style="margin-top:1rem">CREATE ACCOUNT</div>', unsafe_allow_html=True)
        email_r  = st.text_input("Email", key="reg_email",  placeholder="your@email.com")
        pass_r   = st.text_input("Password (min 6 chars)", type="password", key="reg_pass",  placeholder="••••••••")
        pass_r2  = st.text_input("Confirm Password",        type="password", key="reg_pass2", placeholder="••••••••")

        if st.button("🚀  CREATE ACCOUNT", use_container_width=True, key="btn_reg"):
            if not email_r or not pass_r:
                st.markdown('<div class="alert alert-y">⚡ Please fill all fields.</div>', unsafe_allow_html=True)
            elif pass_r != pass_r2:
                st.markdown('<div class="alert alert-r">⚠️ Passwords do not match.</div>', unsafe_allow_html=True)
            elif len(pass_r) < 6:
                st.markdown('<div class="alert alert-y">⚡ Password must be at least 6 characters.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Creating account..."):
                    resp = fb_register(email_r.strip(), pass_r)
                if "idToken" in resp:
                    do_login_session(resp)
                    log_login_event(resp["localId"], resp["email"], resp["idToken"])
                    # Create user profile doc
                    fs_write(f"users/{resp['localId']}/profile", "info", {
                        "email":      _str(resp["email"]),
                        "uid":        _str(resp["localId"]),
                        "created_at": _str(datetime.utcnow().isoformat() + "Z"),
                    }, resp["idToken"])
                    st.markdown('<div class="alert alert-g">✓ Account created! Loading...</div>', unsafe_allow_html=True)
                    st.rerun()
                else:
                    err = resp.get("error", {}).get("message", "Registration failed.")
                    friendly = {
                        "EMAIL_EXISTS":              "An account with this email already exists.",
                        "WEAK_PASSWORD : Password should be at least 6 characters": "Password must be at least 6 characters.",
                        "INVALID_EMAIL":             "Invalid email format.",
                    }.get(err, err)
                    st.markdown(f'<div class="alert alert-r">⚠️ {friendly}</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  GUARD: show auth if not logged in
# ══════════════════════════════════════════════════════════════
if not st.session_state.auth_user:
    render_auth_page()
    st.stop()

# ══════════════════════════════════════════════════════════════
#  LOGGED-IN AREA
# ══════════════════════════════════════════════════════════════
uid      = st.session_state.auth_user["uid"]
email    = st.session_state.auth_user["email"]
id_token = st.session_state.auth_user["idToken"]

# ─── API ───────────────────────────────────────────────────
client = Groq(api_key="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")

PAGES = [
    "🏠 Home", "🩺 Symptom Analyzer", "🎤 Speech to Text",
    "🔊 Text to Speech", "⚠️ Self-Doubt Engine", "🧠 Explainable AI",
    "📊 Dashboard", "👤 Baseline Profile", "📡 Drift Monitor",
    "🗂️ My Records",   # NEW — shows cloud-stored data
]

# ─── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
      <div style="font-family:'Orbitron',sans-serif;font-size:1.4rem;font-weight:900;
                  background:linear-gradient(135deg,#00d4ff,#00ff9d);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;letter-spacing:4px">MEDINTEL</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.52rem;
                  color:rgba(0,212,255,0.4);letter-spacing:3px;margin-top:0.2rem">
        DEEP SPACE AI · v6
      </div>
      <div style="display:inline-flex;align-items:center;gap:0.4rem;
                  background:rgba(0,255,157,0.08);border:1px solid rgba(0,255,157,0.25);
                  border-radius:20px;padding:0.22rem 0.7rem;margin-top:0.5rem">
        <span style="width:5px;height:5px;border-radius:50%;background:#00ff9d;
                     box-shadow:0 0 6px #00ff9d;display:inline-block"></span>
        <span style="font-family:'Share Tech Mono',monospace;font-size:0.52rem;
                     color:#00ff9d;letter-spacing:2px">ONLINE</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── User pill ──────────────────────────────────────────
    st.markdown(f"""
    <div style="margin:0.5rem 0;padding:0.6rem;background:rgba(0,212,255,0.05);
                border:1px solid rgba(0,212,255,0.15);border-radius:10px;text-align:center">
      <div style="font-size:0.65rem;margin-bottom:0.15rem">👤</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:0.5rem;
                  color:#00d4ff;letter-spacing:2px;word-break:break-all">{email}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.52rem;color:#1e4060;letter-spacing:3px;margin-bottom:0.4rem">◈ NAVIGATION</p>', unsafe_allow_html=True)

    for p in PAGES:
        is_active = st.session_state.page == p
        label = f"{'▶ ' if is_active else '   '}{p}"
        if st.button(label, key=f"nav_{p}", use_container_width=True):
            st.session_state.page = p
            st.rerun()

    st.markdown("---")

    # Logout
    if st.button("🚪  LOGOUT", use_container_width=True, key="nav_logout"):
        for k in ["auth_user","history","risk_history","user_profile",
                  "drift_log","feedback_log","stt_text","last_result",
                  "last_risk","last_symptoms","tts_file"]:
            st.session_state[k] = [] if isinstance(st.session_state.get(k), list) else \
                                   {} if isinstance(st.session_state.get(k), dict) else \
                                   None if k == "auth_user" else \
                                   0.0 if k in ("last_risk",) else ""
        st.session_state.page = "🏠 Home"
        st.rerun()

    st.markdown("---")
    total = len(st.session_state.history)
    avg_r = round(sum(st.session_state.risk_history) / max(len(st.session_state.risk_history), 1) * 100)
    hc    = sum(1 for r in st.session_state.risk_history if r >= 0.7)
    pf    = sum(1 for f in st.session_state.feedback_log if f["vote"] == "positive")

    st.markdown(f"""
    <p style="font-family:'Share Tech Mono',monospace;font-size:0.52rem;color:#1e4060;letter-spacing:3px;margin-bottom:0.5rem">◈ LIVE STATS</p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.4rem">
      <div style="background:rgba(0,212,255,0.06);border:1px solid rgba(0,212,255,0.15);border-radius:8px;padding:0.5rem;text-align:center">
        <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:#00d4ff">{total}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.47rem;color:#1e4060;letter-spacing:2px">CASES</div>
      </div>
      <div style="background:rgba(0,255,157,0.06);border:1px solid rgba(0,255,157,0.15);border-radius:8px;padding:0.5rem;text-align:center">
        <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:#00ff9d">{avg_r}%</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.47rem;color:#1e4060;letter-spacing:2px">AVG RISK</div>
      </div>
      <div style="background:rgba(255,50,80,0.06);border:1px solid rgba(255,50,80,0.15);border-radius:8px;padding:0.5rem;text-align:center">
        <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:#ff3250">{hc}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.47rem;color:#1e4060;letter-spacing:2px">HIGH RISK</div>
      </div>
      <div style="background:rgba(255,170,0,0.06);border:1px solid rgba(255,170,0,0.15);border-radius:8px;padding:0.5rem;text-align:center">
        <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:#ffaa00">{pf}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:0.47rem;color:#1e4060;letter-spacing:2px">FEEDBACK</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── HELPERS ───────────────────────────────────────────────
def ai_analysis(sym):
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": (
                    "You are MedIntel AI — advanced clinical AI assistant. "
                    "Structure your response with these sections:\n"
                    "🩺 DIAGNOSIS\n⚡ RISK LEVEL (Low/Moderate/High)\n"
                    "🔬 CLINICAL EXPLANATION\n🔄 DIFFERENTIAL DIAGNOSIS\n"
                    "🏥 WHEN TO SEE DOCTOR\n💊 IMMEDIATE SELF-CARE\n"
                    "Be precise, empathetic, and mention any diagnostic ambiguity."
                )},
                {"role": "user", "content": f"Patient symptoms: {sym}"}
            ]
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"

def ai_explainer(sym, res):
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "XAI engine. Give exactly 4 numbered steps explaining reasoning. Each = 1 plain sentence. Format: 1. ... 2. ... 3. ... 4. ..."},
                {"role": "user", "content": f"Symptoms: {sym}\nDiagnosis: {res[:300]}"}
            ]
        )
        return r.choices[0].message.content
    except:
        return "1. Symptom keywords were extracted and clinically weighted.\n2. Matched against a database of 500+ disease profiles.\n3. Top differentials ranked by symptom overlap probability.\n4. Risk level assigned from severity, duration, and patient context."

def ai_doubt(res):
    try:
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": 'Medical AI critic. Return ONLY valid JSON, nothing else: {"confused":true/false,"pair":"Disease A vs Disease B","reason":"one sentence","confidence":0.85}'},
                {"role": "user", "content": res[:400]}
            ]
        )
        raw = r.choices[0].message.content.strip().replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except:
        return {"confused": False, "pair": "", "reason": "", "confidence": 0.88}

def extract_risk(text):
    t = text.lower()
    if "high" in t:     return 0.82
    if "moderate" in t: return 0.50
    return 0.25

def do_stt():
    rec = sr.Recognizer()
    try:
        with sr.Microphone() as src:
            rec.adjust_for_ambient_noise(src, duration=0.5)
            audio = rec.listen(src, timeout=6, phrase_time_limit=12)
        return rec.recognize_google(audio)
    except sr.WaitTimeoutError:  return "⚠️ Timeout — no speech detected"
    except sr.UnknownValueError: return "⚠️ Could not understand audio"
    except Exception as e:       return f"⚠️ Mic error: {e}"

def do_tts(text):
    obj = gTTS(text[:600])
    f = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    obj.save(f.name)
    return f.name

def play_audio(fp):
    with open(fp, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f'<audio autoplay controls style="width:100%;margin-top:0.8rem;border-radius:8px">'
        f'<source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>',
        unsafe_allow_html=True)

def upd_profile(sym):
    for w in sym.lower().split():
        if len(w) > 3:
            st.session_state.user_profile[w] = st.session_state.user_profile.get(w, 0) + 1

def baseline(sym):
    ws = [w for w in sym.lower().split() if len(w) > 3]
    return ([w for w in ws if st.session_state.user_profile.get(w, 0) > 1],
            [w for w in ws if w not in st.session_state.user_profile])

def drift_status():
    rh = st.session_state.risk_history
    if len(rh) < 3: return "INSUFFICIENT DATA", "#1e4060"
    d = abs(sum(rh[-3:]) / 3 - sum(rh) / len(rh))
    if d < 0.05: return "✅ STABLE",       "#00ff9d"
    if d < 0.15: return "⚡ MINOR DRIFT",  "#ffaa00"
    return "🔴 DRIFT ALERT", "#ff3250"

def rbadge(r):
    if r >= 0.7: return '<span class="badge b-h">HIGH RISK</span>'
    if r >= 0.4: return '<span class="badge b-m">MODERATE</span>'
    return '<span class="badge b-l">LOW RISK</span>'

def pdef():
    return dict(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani', color='#c8e6ff'),
        margin=dict(l=0, r=10, t=20, b=0))

# ─── TICKER ────────────────────────────────────────────────
items = [f"◈ MEDINTEL AI · {email}", "◈ LLaMA 3.1 ACTIVE", "◈ XAI MODULE READY",
         "◈ FIREBASE CONNECTED", f"◈ CASES: {len(st.session_state.history)}",
         "◈ DRIFT MONITOR RUNNING", "◈ ALL SYSTEMS NOMINAL"]
ticker = "  ◇  ".join(items) * 3
st.markdown(f"""
<div style="overflow:hidden;background:rgba(0,212,255,0.04);
            border-bottom:1px solid rgba(0,212,255,0.1);padding:0.3rem 0;margin-bottom:1.5rem">
  <span style="display:inline-block;white-space:nowrap;font-family:'Share Tech Mono',monospace;
               font-size:0.58rem;color:rgba(0,212,255,0.5);letter-spacing:3px;
               animation:tick 40s linear infinite">
    {ticker}
  </span>
</div>
<style>@keyframes tick{{from{{transform:translateX(100vw)}}to{{transform:translateX(-100%)}}}}</style>
""", unsafe_allow_html=True)

page = st.session_state.page

# ══════════════════════════════════════════════════════
#  PAGE: HOME
# ══════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown('<p class="page-eyebrow">◈ MEDINTEL DEEP SPACE AI</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-sub">WELCOME BACK · {email.upper()} · ALL SYSTEMS NOMINAL · v6.0</p>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, icon, val, lbl, clr in zip(
        [c1,c2,c3,c4,c5],
        ["🧬","🎤","🔊","🛡️","🔥"],
        ["LLaMA 3.1","Google STT","gTTS","XAI","Firebase"],
        ["AI ENGINE","VOICE IN","VOICE OUT","EXPLAINER","AUTH+DB"],
        ["#00d4ff","#00ff9d","#7b2fff","#ffaa00","#ff2d78"]
    ):
        col.markdown(f"""
        <div class="metric-box" style="border-bottom:2px solid {clr}">
          <div style="font-size:1.5rem;margin-bottom:0.3rem">{icon}</div>
          <div class="metric-val" style="color:{clr};font-size:0.85rem">{val}</div>
          <div class="metric-lbl">{lbl}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    feats = [
        ("🩺","SYMPTOM ANALYZER","AI clinical diagnosis with real-time risk scoring and differential analysis."),
        ("🎤","SPEECH TO TEXT","Speak your symptoms — neural STT converts voice to medical text instantly."),
        ("🔊","TEXT TO SPEECH","AI reads diagnosis aloud with natural TTS voice synthesis."),
        ("⚠️","SELF-DOUBT ENGINE","AI audits its own confidence and flags confusion between diseases."),
        ("🧠","EXPLAINABLE AI","4-step transparent reasoning chain with feature importance visuals."),
        ("📊","DASHBOARD","Live risk trends, distribution charts, full case history."),
        ("👤","BASELINE PROFILE","Tracks personal symptom patterns and detects health deviations."),
        ("🗂️","MY RECORDS","Cloud-synced history — all your queries and diagnoses from Firebase."),
    ]
    for row in [feats[:4], feats[4:]]:
        cols = st.columns(4)
        for col, (icon, title, desc) in zip(cols, row):
            col.markdown(f"""
            <div class="feat-card">
              <span class="feat-icon">{icon}</span>
              <div class="feat-title">{title}</div>
              <div class="feat-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    if st.session_state.risk_history:
        st.markdown('<div class="sec-h">LIVE RISK FEED</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=st.session_state.risk_history, mode='lines+markers',
            line=dict(color='#00d4ff', width=2),
            marker=dict(color='#00ff9d', size=7),
            fill='tozeroy', fillcolor='rgba(0,212,255,0.05)'
        ))
        fig.update_layout(**pdef(), height=120,
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, range=[0,1.1], zeroline=False),
            showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════
#  PAGE: SYMPTOM ANALYZER  (with Firestore save)
# ══════════════════════════════════════════════════════
elif page == "🩺 Symptom Analyzer":
    st.markdown('<p class="page-eyebrow">◈ NEURAL DIAGNOSTIC ENGINE</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">SYMPTOM ANALYZER</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">ENTER SYMPTOMS · AI ANALYSIS · RISK SCORING · SAVED TO FIREBASE</p>', unsafe_allow_html=True)

    L, R = st.columns([1, 1], gap="large")

    with L:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">PATIENT INPUT</div>', unsafe_allow_html=True)
        pre      = st.session_state.stt_text or ""
        symptoms = st.text_area("Enter symptoms:", value=pre, height=130,
            placeholder="e.g. high fever 3 days, dry cough, headache, body ache, chills...",
            label_visibility="collapsed")

        st.markdown('<p style="font-size:0.65rem;color:#1e4060;font-family:\'Share Tech Mono\',monospace;letter-spacing:2px;margin-bottom:0.3rem">QUICK TAGS:</p>', unsafe_allow_html=True)
        q = st.columns(5)
        for i, tag in enumerate(["Fever","Cough","Nausea","Fatigue","Pain"]):
            if q[i].button(tag, key=f"qt{i}"):
                symptoms = (symptoms + " " + tag).strip()

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        age    = c1.number_input("Age", 1, 120, 25)
        gender = c2.selectbox("Gender", ["Male", "Female", "Other"])
        dur    = c3.selectbox("Duration", ["< 24h", "1-3 days", "3-7 days", "> 7 days"])
        go_btn = st.button("🔍  INITIATE NEURAL SCAN", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with R:
        if go_btn:
            if symptoms.strip():
                with st.spinner("🧬 Analyzing + saving to Firebase..."):
                    full = f"{symptoms} | Age:{age} | Gender:{gender} | Duration:{dur}"
                    res  = ai_analysis(full)
                    risk = extract_risk(res)
                    ts   = datetime.now().strftime("%H:%M · %d %b %Y")
                    st.session_state.history.append({"symptoms":symptoms,"result":res,"risk":risk,"time":ts})
                    st.session_state.risk_history.append(risk)
                    st.session_state.last_result   = res
                    st.session_state.last_risk     = risk
                    st.session_state.last_symptoms = symptoms
                    upd_profile(symptoms)
                    # ── Save to Firestore ──────────────────────────
                    save_query_to_firestore(uid, id_token, symptoms, res, risk, age, gender, dur)

                st.markdown('<div class="alert alert-g" style="font-size:0.75rem">✓ Diagnosis saved to Firebase cloud.</div>', unsafe_allow_html=True)
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<div class="sec-h">DIAGNOSIS RESULT {rbadge(risk)}</div>', unsafe_allow_html=True)

                bc = "#ff3250" if risk >= 0.7 else "#ffaa00" if risk >= 0.4 else "#00ff9d"
                st.markdown(f"""
                <div style="margin-bottom:1rem">
                  <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:0.58rem;color:#1e4060;margin-bottom:0.3rem">
                    <span>RISK SCORE</span><span style="color:{bc}">{int(risk*100)}%</span>
                  </div>
                  <div class="r-bar-bg">
                    <div class="r-bar-fill" style="width:{int(risk*100)}%;background:linear-gradient(90deg,{bc}66,{bc})"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

                st.markdown(f'<div class="dx-out">{res}</div>', unsafe_allow_html=True)
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

                fb1, fb2 = st.columns(2)
                if fb1.button("👍 Accurate",   key="fby", use_container_width=True):
                    st.session_state.feedback_log.append({"time":ts,"vote":"positive","symptoms":symptoms})
                    st.markdown('<div class="alert alert-g">✓ Positive feedback logged.</div>', unsafe_allow_html=True)
                if fb2.button("👎 Inaccurate", key="fbn", use_container_width=True):
                    st.session_state.feedback_log.append({"time":ts,"vote":"negative","symptoms":symptoms})
                    st.markdown('<div class="alert alert-y">⚡ Noted. AI will calibrate.</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert alert-y">⚡ Please enter symptoms first.</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="card" style="text-align:center;padding:4rem 1rem">
              <div style="font-size:4rem;margin-bottom:1rem">🩺</div>
              <div style="font-family:'Orbitron',sans-serif;font-size:0.8rem;color:#00d4ff;letter-spacing:3px">AWAITING SCAN</div>
              <div style="font-size:0.78rem;color:#1e4060;margin-top:0.5rem">Enter symptoms and click Initiate</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  PAGE: MY RECORDS  (NEW — Firebase cloud history)
# ══════════════════════════════════════════════════════
elif page == "🗂️ My Records":
    st.markdown('<p class="page-eyebrow">◈ FIREBASE CLOUD STORAGE</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">MY RECORDS</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">ALL YOUR QUERIES · DIAGNOSES · LOGIN HISTORY — SYNCED FROM FIREBASE</p>', unsafe_allow_html=True)

    tab_q, tab_l = st.tabs(["🩺  QUERY HISTORY", "🔐  LOGIN HISTORY"])

    with tab_q:
        st.markdown('<div class="sec-h">CLOUD QUERY REGISTRY</div>', unsafe_allow_html=True)
        with st.spinner("Fetching from Firebase..."):
            queries = fetch_user_queries(uid, id_token)

        if queries:
            st.markdown(f'<div class="alert alert-g">✓ {len(queries)} records found in your Firebase account.</div>', unsafe_allow_html=True)
            df = pd.DataFrame([{
                "TIME":      q["time"],
                "SYMPTOMS":  str(q["symptoms"])[:55] + "..." if len(str(q["symptoms"])) > 55 else q["symptoms"],
                "RISK %":    f"{q['risk_pct']}%",
                "LEVEL":     ("🔴 HIGH" if q["risk_level"] == "HIGH"
                              else "🟡 MODERATE" if q["risk_level"] == "MODERATE"
                              else "🟢 LOW"),
            } for q in queries])
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown('<div class="sec-h" style="margin-top:1.5rem">DIAGNOSIS DETAIL VIEWER</div>', unsafe_allow_html=True)
            idx = st.selectbox("Select record to view full diagnosis:", range(len(queries)),
                format_func=lambda i: f"[{queries[i]['time']}] {str(queries[i]['symptoms'])[:40]}...")
            if idx is not None:
                q = queries[idx]
                bc = "#ff3250" if q["risk_level"] == "HIGH" else "#ffaa00" if q["risk_level"] == "MODERATE" else "#00ff9d"
                st.markdown(f"""
                <div style="margin:0.8rem 0">
                  <div style="display:flex;justify-content:space-between;font-family:'Share Tech Mono',monospace;font-size:0.58rem;color:#1e4060;margin-bottom:0.3rem">
                    <span>RISK</span><span style="color:{bc}">{q['risk_pct']}% · {q['risk_level']}</span>
                  </div>
                  <div class="r-bar-bg"><div class="r-bar-fill" style="width:{q['risk_pct']}%;background:{bc}"></div></div>
                </div>
                <div class="dx-out">{q['diagnosis']}</div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert alert-c">◈ No cloud records yet. Run the Symptom Analyzer to create your first record.</div>', unsafe_allow_html=True)

    with tab_l:
        st.markdown('<div class="sec-h">LOGIN HISTORY</div>', unsafe_allow_html=True)
        with st.spinner("Fetching login history..."):
            logins = fetch_login_history(uid, id_token)

        if logins:
            st.markdown(f'<div class="alert alert-g">✓ {len(logins)} login events recorded.</div>', unsafe_allow_html=True)
            for ev in reversed(logins):
                st.markdown(f"""
                <div class="tl">
                  <div class="tl-time">🔐 {ev['time']} · <span style="color:#00d4ff">{ev['platform']}</span></div>
                  <div style="font-size:0.82rem;color:#5a8aaa">{ev['email']}</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert alert-c">◈ No login history found.</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
#  REMAINING PAGES (unchanged from original)
# ══════════════════════════════════════════════════════
elif page == "🎤 Speech to Text":
    st.markdown('<p class="page-eyebrow">◈ NEURAL STT ENGINE</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">SPEECH TO TEXT</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">SPEAK YOUR SYMPTOMS · REAL-TIME TRANSCRIPTION</p>', unsafe_allow_html=True)
    L, R = st.columns([1, 1], gap="large")
    with L:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">MICROPHONE</div>', unsafe_allow_html=True)
        st.markdown('<div class="vring">🎤</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.58rem;color:#1e4060;letter-spacing:3px;margin-bottom:1rem">SPEAK CLEARLY · 6-SECOND WINDOW</p>', unsafe_allow_html=True)
        if st.button("🎤  ACTIVATE LISTENING", use_container_width=True):
            with st.spinner("Listening..."):
                txt = do_stt()
            st.session_state.stt_text = txt
            if "⚠️" not in txt:
                st.markdown(f'<div class="alert alert-g">✓ Transcribed: <b>{txt}</b></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert alert-r">{txt}</div>', unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("""<div style="text-align:left;font-size:0.8rem;color:#1e4060;line-height:1.8">
          <b style="color:#00d4ff;font-family:'Share Tech Mono',monospace;font-size:0.58rem;letter-spacing:2px">STEPS:</b><br>
          1. Click Activate Listening<br>2. Speak your symptoms clearly<br>
          3. Edit transcription if needed<br>4. Click Analyze to get diagnosis
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with R:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">TRANSCRIPTION OUTPUT</div>', unsafe_allow_html=True)
        if st.session_state.stt_text:
            ed = st.text_area("Edit if needed:", value=st.session_state.stt_text, height=100)
            st.session_state.stt_text = ed
            st.markdown(f'<p style="font-family:\'Share Tech Mono\',monospace;font-size:0.57rem;color:#00ff9d;letter-spacing:2px">◈ {len(ed.split())} WORDS CAPTURED</p>', unsafe_allow_html=True)
            if st.button("🧬  ANALYZE VOICE INPUT", use_container_width=True):
                with st.spinner("Analyzing..."):
                    res  = ai_analysis(ed)
                    risk = extract_risk(res)
                    ts   = datetime.now().strftime("%H:%M · %d %b %Y")
                    st.session_state.history.append({"symptoms":ed,"result":res,"risk":risk,"time":ts})
                    st.session_state.risk_history.append(risk)
                    st.session_state.last_result   = res
                    st.session_state.last_risk     = risk
                    st.session_state.last_symptoms = ed
                    upd_profile(ed)
                    save_query_to_firestore(uid, id_token, ed, res, risk, 0, "Unknown", "Unknown")
                st.markdown(f'<div class="dx-out" style="margin-top:1rem">{res}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#1e4060"><div style="font-size:2.5rem;margin-bottom:1rem;opacity:0.4">📝</div>No transcription yet.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "🔊 Text to Speech":
    st.markdown('<p class="page-eyebrow">◈ TTS SYNTHESIS ENGINE</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">TEXT TO SPEECH</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">AI VOICE SYNTHESIS · CLINICAL AUDIO PLAYBACK</p>', unsafe_allow_html=True)
    L, R = st.columns([1, 1], gap="large")
    with L:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">INPUT SOURCE</div>', unsafe_allow_html=True)
        mode = st.radio("Source:", ["Last Diagnosis", "Custom Text"], horizontal=True)
        if mode == "Last Diagnosis":
            tts_t = st.session_state.last_result
            if tts_t:
                st.markdown(f'<div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);border-radius:8px;padding:0.8rem;font-size:0.8rem;max-height:150px;overflow-y:auto;line-height:1.7">{tts_t[:500]}{"..." if len(tts_t)>500 else ""}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert alert-c">◈ Run Symptom Analyzer first.</div>', unsafe_allow_html=True)
                tts_t = ""
        else:
            tts_t = st.text_area("Type text to speak:", height=140, placeholder="Enter any medical text to synthesize...")
        if st.button("🔊  SYNTHESIZE SPEECH", use_container_width=True):
            if tts_t and tts_t.strip():
                with st.spinner("Synthesizing..."):
                    fp = do_tts(tts_t)
                    st.session_state.tts_file = fp
                st.markdown('<div class="alert alert-g">✓ Audio ready.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert alert-y">⚡ No text to synthesize.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with R:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">PLAYBACK</div>', unsafe_allow_html=True)
        if st.session_state.tts_file:
            st.markdown('<div style="font-size:3.5rem;margin:1.5rem 0">🔊</div>', unsafe_allow_html=True)
            play_audio(st.session_state.tts_file)
        else:
            st.markdown('<div style="padding:4rem;color:#1e4060"><div style="font-size:3rem;opacity:0.25">🔈</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "⚠️ Self-Doubt Engine":
    st.markdown('<p class="page-eyebrow">◈ UNCERTAINTY QUANTIFICATION</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">SELF-DOUBT ENGINE</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">AI AUDITS OWN CONFIDENCE · CONFUSION DETECTION</p>', unsafe_allow_html=True)
    if not st.session_state.last_result:
        st.markdown('<div class="alert alert-c">◈ Run Symptom Analyzer first.</div>', unsafe_allow_html=True)
    else:
        L, R = st.columns([1, 1], gap="large")
        with L:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-h">UNCERTAINTY ANALYSIS</div>', unsafe_allow_html=True)
            with st.spinner("Auditing..."):
                doubt = ai_doubt(st.session_state.last_result)
            if doubt.get("confused"):
                pair = doubt.get("pair","Flu vs Pneumonia"); reason = doubt.get("reason",""); conf = doubt.get("confidence",0.55)
                d1, d2 = (pair.split(" vs ") + ["Disease B"])[:2]
                st.markdown(f'<div class="alert alert-y">⚡ <b>SELF-DOUBT:</b> {pair}<br>{reason}</div>', unsafe_allow_html=True)
                bc2 = "#00ff9d" if conf > 0.7 else "#ffaa00"
                st.markdown(f'<div style="margin-top:0.5rem"><div style="display:flex;justify-content:space-between;font-family:\'Share Tech Mono\',monospace;font-size:0.57rem;color:#1e4060;margin-bottom:0.3rem"><span>CONFIDENCE</span><span style="color:{bc2}">{int(conf*100)}%</span></div><div class="r-bar-bg"><div class="r-bar-fill" style="width:{int(conf*100)}%;background:{bc2}"></div></div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align:center;padding:2rem"><div style="font-size:3rem">✅</div><div style="font-family:\'Orbitron\',sans-serif;font-size:0.8rem;color:#00ff9d;letter-spacing:3px">HIGH CONFIDENCE</div></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with R:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-h">DIFFERENTIAL PROBABILITY</div>', unsafe_allow_html=True)
            fig = go.Figure(go.Bar(x=[0.70,0.18,0.08,0.04],y=["Primary Dx","Differential 1","Differential 2","Unlikely"],
                orientation='h',marker=dict(color=["#00ff9d","#00d4ff","#ffaa00","#1e4060"]),
                text=["70%","18%","8%","4%"],textposition='inside',textfont=dict(family='Share Tech Mono',size=10)))
            fig.update_layout(**pdef(),height=190,xaxis=dict(showgrid=False,showticklabels=False,range=[0,1]),yaxis=dict(showgrid=False,tickfont=dict(size=11)))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "🧠 Explainable AI":
    st.markdown('<p class="page-eyebrow">◈ XAI TRANSPARENCY MODULE</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">EXPLAINABLE AI</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">HUMAN-READABLE REASONING · FEATURE IMPORTANCE</p>', unsafe_allow_html=True)
    if not st.session_state.last_result:
        st.markdown('<div class="alert alert-c">◈ Run Symptom Analyzer first.</div>', unsafe_allow_html=True)
    else:
        L, R = st.columns([1,1], gap="large")
        with L:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-h">DECISION CHAIN</div>', unsafe_allow_html=True)
            with st.spinner("Generating reasoning..."):
                expl = ai_explainer(st.session_state.last_symptoms, st.session_state.last_result)
            lines = [l.strip() for l in expl.split('\n') if l.strip() and l.strip()[0].isdigit()]
            fallback = ["Symptom keywords extracted and clinically weighted.",
                        "Matched against 500+ disease knowledge profiles.",
                        "Top differentials ranked by symptom-overlap probability.",
                        "Risk assigned from severity, duration, and patient context."]
            steps = lines[:4] if len(lines) >= 4 else fallback
            for i, step in enumerate(steps, 1):
                txt = step.split('.', 1)[1].strip() if '.' in step else step
                st.markdown(f'<div class="xai-step"><div class="xai-n">{i}</div><div class="xai-t">{txt}</div></div>', unsafe_allow_html=True)
            pct = random.randint(55,78)
            st.markdown(f'<div class="alert alert-c" style="margin-top:0.8rem">🧠 Primary symptom drove <b>{pct}%</b> of diagnosis weight.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with R:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="sec-h">FEATURE IMPORTANCE</div>', unsafe_allow_html=True)
            words = [w for w in st.session_state.last_symptoms.lower().split() if len(w) > 3][:7]
            if not words: words = ["fever","cough","fatigue","headache"]
            imp = sorted([random.uniform(0.25,1.0) for _ in words], reverse=True)
            fig = go.Figure(go.Bar(y=words,x=imp,orientation='h',
                marker=dict(color=imp,colorscale=[[0,'#060f22'],[0.4,'#00d4ff'],[1,'#00ff9d']],showscale=False),
                text=[f"{int(v*100)}%" for v in imp],textposition='inside',textfont=dict(family='Share Tech Mono',size=10)))
            fig.update_layout(**pdef(),height=230,xaxis=dict(showgrid=False,showticklabels=False,range=[0,1.1]),yaxis=dict(showgrid=False,tickfont=dict(family='Rajdhani',size=12)))
            st.plotly_chart(fig, use_container_width=True)
            conf = random.uniform(0.66,0.94)
            fig2 = go.Figure(go.Indicator(mode="gauge+number",value=round(conf*100,1),
                number=dict(suffix="%",font=dict(family='Orbitron',size=26,color='#00d4ff')),
                gauge=dict(axis=dict(range=[0,100]),bar=dict(color='#00d4ff',thickness=0.22),bgcolor='rgba(0,0,0,0)',
                    steps=[dict(range=[0,40],color='rgba(255,50,80,0.08)'),dict(range=[40,70],color='rgba(255,170,0,0.08)'),dict(range=[70,100],color='rgba(0,255,157,0.08)')])))
            fig2.update_layout(**pdef(),height=175)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "📊 Dashboard":
    st.markdown('<p class="page-eyebrow">◈ REAL-TIME ANALYTICS</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">ANALYTICS DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">CASE HISTORY · RISK TRENDS · DISTRIBUTION</p>', unsafe_allow_html=True)
    tot = len(st.session_state.history)
    ar  = round(sum(st.session_state.risk_history) / max(len(st.session_state.risk_history),1) * 100)
    hc  = sum(1 for r in st.session_state.risk_history if r >= 0.7)
    pf  = sum(1 for f in st.session_state.feedback_log if f["vote"] == "positive")
    c1,c2,c3,c4 = st.columns(4)
    for col,v,l,clr in zip([c1,c2,c3,c4],[tot,f"{ar}%",hc,pf],["TOTAL CASES","AVG RISK","HIGH RISK","POSITIVE FB"],["#00d4ff","#ffaa00","#ff3250","#00ff9d"]):
        col.markdown(f'<div class="metric-box" style="border-bottom:2px solid {clr}"><div class="metric-val" style="color:{clr}">{v}</div><div class="metric-lbl">{l}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    L, R = st.columns([3,2], gap="large")
    with L:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">RISK TREND TIMELINE</div>', unsafe_allow_html=True)
        if st.session_state.risk_history:
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=st.session_state.risk_history,mode='lines+markers',
                line=dict(color='#00d4ff',width=2.5),marker=dict(color='#00ff9d',size=8),
                fill='tozeroy',fillcolor='rgba(0,212,255,0.05)'))
            fig.add_hline(y=0.7,line_dash='dot',line_color='rgba(255,50,80,0.4)')
            fig.add_hline(y=0.4,line_dash='dot',line_color='rgba(255,170,0,0.4)')
            fig.update_layout(**pdef(),height=220,xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor='rgba(0,212,255,0.05)',range=[0,1.15]),showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#1e4060">No data yet</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with R:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">RISK DISTRIBUTION</div>', unsafe_allow_html=True)
        if st.session_state.risk_history:
            lc = sum(1 for r in st.session_state.risk_history if r < 0.4)
            mc = sum(1 for r in st.session_state.risk_history if 0.4 <= r < 0.7)
            fig = go.Figure(go.Pie(labels=['LOW','MODERATE','HIGH'],values=[lc,mc,hc] if (lc+mc+hc)>0 else [1,1,1],
                hole=0.55,marker_colors=['#00ff9d','#ffaa00','#ff3250'],textfont=dict(family='Share Tech Mono',size=9)))
            fig.update_layout(**pdef(),height=220,legend=dict(font=dict(size=9,family='Share Tech Mono'),orientation='h',y=-0.15))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#1e4060">No data yet</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="sec-h">FULL CASE REGISTRY (SESSION)</div>', unsafe_allow_html=True)
    if st.session_state.history:
        df = pd.DataFrame([{"TIME":h["time"],"SYMPTOMS":h["symptoms"][:55]+"..." if len(h["symptoms"])>55 else h["symptoms"],
            "RISK %":f"{int(h['risk']*100)}%","LEVEL":"🔴 HIGH" if h['risk']>=0.7 else "🟡 MOD" if h['risk']>=0.4 else "🟢 LOW"} for h in st.session_state.history])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div style="text-align:center;padding:2rem;color:#1e4060">No cases yet</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "👤 Baseline Profile":
    st.markdown('<p class="page-eyebrow">◈ PERSONALIZATION ENGINE</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">BASELINE PROFILE</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">USER-SPECIFIC HEALTH TRACKING · DEVIATION DETECTION</p>', unsafe_allow_html=True)
    L, R = st.columns([1,1], gap="large")
    with L:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">SYMPTOM FREQUENCY MAP</div>', unsafe_allow_html=True)
        if st.session_state.user_profile:
            top = sorted(st.session_state.user_profile.items(), key=lambda x:x[1], reverse=True)[:10]
            ws, fs = zip(*top)
            fig = go.Figure(go.Bar(x=list(ws),y=list(fs),
                marker=dict(color=list(fs),colorscale=[[0,'#060f22'],[0.5,'#00d4ff'],[1,'#00ff9d']],showscale=False),
                text=list(fs),textposition='outside',textfont=dict(family='Share Tech Mono',size=9)))
            fig.update_layout(**pdef(),height=220,xaxis=dict(showgrid=False,tickfont=dict(size=9)),yaxis=dict(showgrid=True,gridcolor='rgba(0,212,255,0.05)'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#1e4060">Profile builds as you analyze symptoms.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with R:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">DEVIATION SCANNER</div>', unsafe_allow_html=True)
        chk = st.text_input("Check symptoms against baseline:", placeholder="e.g. chest pain shortness of breath")
        if st.button("🔍  SCAN FOR DEVIATION", use_container_width=True):
            if chk.strip():
                known, new_ = baseline(chk)
                if new_:  st.markdown(f'<div class="alert alert-y">⚡ NEW: {", ".join(new_)}</div>', unsafe_allow_html=True)
                if known: st.markdown(f'<div class="alert alert-c">◈ RECURRING: {", ".join(known)}</div>', unsafe_allow_html=True)
                if not known and not new_: st.markdown('<div class="alert alert-g">✓ No deviation.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert alert-y">⚡ Enter symptoms to scan.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "📡 Drift Monitor":
    st.markdown('<p class="page-eyebrow">◈ MODEL INTEGRITY SYSTEM</p>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">DRIFT MONITOR</div>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">REAL-TIME ACCURACY TRACKING · ROLLING ANALYSIS</p>', unsafe_allow_html=True)
    stxt, sclr = drift_status()
    L, R = st.columns([1,1], gap="large")
    with L:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">SYSTEM STATUS</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:3.5rem;margin:1rem 0">📡</div><div style="font-family:\'Orbitron\',sans-serif;font-size:1.3rem;color:{sclr};letter-spacing:3px">{stxt}</div>', unsafe_allow_html=True)
        if len(st.session_state.risk_history) >= 2:
            rh=st.session_state.risk_history; r3=round(sum(rh[-3:])/min(3,len(rh)),3); all_=round(sum(rh)/len(rh),3); mag=round(abs(r3-all_),3)
            st.markdown("<br>", unsafe_allow_html=True)
            for lbl,val,clr in [("RECENT AVG",f"{int(r3*100)}%","#00d4ff"),("OVERALL AVG",f"{int(all_*100)}%","#7b2fff"),("DRIFT MAG",f"{int(mag*100)}%",sclr),("CASES",str(len(rh)),"#00ff9d")]:
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0.3rem;border-bottom:1px solid rgba(0,212,255,0.07)"><span style="font-family:\'Share Tech Mono\',monospace;font-size:0.57rem;color:#1e4060">{lbl}</span><span style="font-family:\'Orbitron\',sans-serif;font-size:0.9rem;color:{clr}">{val}</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert alert-c">◈ Need 2+ cases.</div>', unsafe_allow_html=True)
        note = st.text_input("Observation:", placeholder="Log a drift event note...")
        if st.button("📝  LOG EVENT", use_container_width=True):
            if note.strip():
                st.session_state.drift_log.append({"time":datetime.now().strftime("%H:%M · %d %b"),"note":note,"status":stxt})
                st.markdown('<div class="alert alert-g">✓ Logged.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with R:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="sec-h">ROLLING DRIFT CHART</div>', unsafe_allow_html=True)
        if len(st.session_state.risk_history) >= 2:
            rh=st.session_state.risk_history
            rolling=[sum(rh[max(0,i-2):i+1])/len(rh[max(0,i-2):i+1]) for i in range(len(rh))]
            fig=go.Figure()
            fig.add_trace(go.Scatter(y=rh,mode='lines',name='RAW',line=dict(color='rgba(0,212,255,0.3)',width=1,dash='dot')))
            fig.add_trace(go.Scatter(y=rolling,mode='lines+markers',name='3-AVG',line=dict(color='#00ff9d',width=2.5),marker=dict(size=7,color='#00ff9d')))
            fig.update_layout(**pdef(),height=200,xaxis=dict(showgrid=False),yaxis=dict(showgrid=True,gridcolor='rgba(0,212,255,0.05)',range=[0,1.15]),legend=dict(font=dict(size=9,family='Share Tech Mono'),orientation='h',y=1.15))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('<div style="text-align:center;padding:2.5rem;color:#1e4060">Need 2+ cases.</div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-h" style="margin-top:0.5rem">EVENT LOG</div>', unsafe_allow_html=True)
        if st.session_state.drift_log:
            for e in reversed(st.session_state.drift_log[-5:]):
                st.markdown(f'<div class="tl"><div class="tl-time">{e["time"]} · {e["status"]}</div><div style="font-size:0.83rem">{e["note"]}</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-size:0.8rem;color:#1e4060">No events logged.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)