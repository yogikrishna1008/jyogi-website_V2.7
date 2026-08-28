"""
api.py — Jyogi AI FastAPI Backend (v3)
=======================================
All proprietary calculation logic lives in vedic_engine.py.
This file only defines API endpoints and request/response models.

NEW ENDPOINTS (v3):
  POST /api/planets    — get all planetary positions, lagna, dasha
  POST /api/panchang   — get full panchang for a date
  POST /api/muhurta    — get 7-day activity scoring grid
  POST /api/chart-full — chart + yogas + navamsha + numerology + remedies

EXISTING ENDPOINTS (unchanged):
  POST /api/compatibility
  POST /api/geocode
  POST /api/insight
  POST /api/log
  GET  /api/logs
  GET  /api/logs/count
  GET  /api/logs/stats
  GET  /health
"""

from __future__ import annotations
import os, uuid, time, json, csv, io, tempfile, logging, sqlite3
from collections import defaultdict
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone, timedelta, date
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Request, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from secrets import compare_digest as _ct_eq
from pydantic import BaseModel, Field

# ── Proprietary engine (server-side only) ─────────────────────
try:
    from vedic_engine import (
        julian_day, ist_to_ut, get_all_planets, get_lagna, get_dasha,
        calc_numerology, detect_yogas, calc_navamsha,
        calc_panchang, get_muhurta_grid, ACTIVITY_DATA, NAKSH, RASHIS
    )
    _VEDIC_OK = True
except Exception as _ve_err:
    _VEDIC_OK = False
    import logging as _log
    _log.warning("vedic_engine unavailable: %s", _ve_err)
    # Stub functions so app starts even without vedic_engine
    ACTIVITY_DATA = {}
    NAKSH = []; RASHIS = []
    def calc_panchang(*a, **k): raise RuntimeError("vedic_engine not loaded")
    def get_muhurta_grid(*a, **k): raise RuntimeError("vedic_engine not loaded")
    def get_all_planets(*a, **k): raise RuntimeError("vedic_engine not loaded")
    def get_lagna(*a, **k): raise RuntimeError("vedic_engine not loaded")
    def get_dasha(*a, **k): raise RuntimeError("vedic_engine not loaded")
    def calc_numerology(*a, **k): raise RuntimeError("vedic_engine not loaded")
    def detect_yogas(*a, **k): return []
    def calc_navamsha(*a, **k): return {}
    def julian_day(*a, **k): return 0
    def ist_to_ut(h): return h - 5.5

# ── Ashtakoot engine ──────────────────────────────────────────
from ashtakoot_engine import calculate_ashtakoot

# ══════════════════════════════════════════════════════════════
# APPLICATIONS DB — persists consultation applications from apply.html
# BEFORE the visitor's browser opens WhatsApp, so a submission is never
# lost to a missed notification or a closed tab.
#
# NOTE ON PERSISTENCE: Render's free-tier filesystem is ephemeral — this
# file (like LOG_FILE below) is wiped on every redeploy/restart. Set
# APPLICATIONS_DB_PATH to a mounted persistent disk once one exists; until
# then, treat this as "durable between requests" but not "durable forever".
# ══════════════════════════════════════════════════════════════
APPLICATIONS_DB_PATH = os.getenv("APPLICATIONS_DB_PATH", "/tmp/jyogi_applications.db")

def _apps_db():
    conn = sqlite3.connect(APPLICATIONS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_applications_db():
    with _apps_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id           TEXT PRIMARY KEY,
                created_at   TEXT NOT NULL,
                name         TEXT NOT NULL,
                topic        TEXT NOT NULL,
                question     TEXT NOT NULL,
                tried        TEXT NOT NULL,
                birth_details TEXT,
                source       TEXT,
                ip_hash      TEXT,
                status       TEXT NOT NULL DEFAULT 'new'
            )
        """)
        conn.commit()

# ══════════════════════════════════════════════════════════════
# ANALYTICS DB — visitor/page-view/event tracking for jyogi.in.
#
# Privacy: we never store a raw IP. Each visit gets a one-way
# visitor_hash = SHA256(ip + user_agent + VISITOR_SALT)[:16], which lets us
# estimate unique visitors without keeping anything that identifies a person.
# Country comes from Cloudflare's CF-IPCountry header (no geo lookup, no IP
# ever touches disk). Same ephemeral-storage caveat as APPLICATIONS_DB_PATH
# applies here — see note above. Move both to a persistent disk / Postgres
# together when that upgrade happens.
# ══════════════════════════════════════════════════════════════
ANALYTICS_DB_PATH = os.getenv("ANALYTICS_DB_PATH", "/tmp/jyogi_analytics.db")

VISITOR_SALT = os.getenv("VISITOR_SALT", "").strip()
if not VISITOR_SALT:
    import secrets as _sec3
    VISITOR_SALT = _sec3.token_hex(16)
    logging.getLogger("jyogi_api").warning(
        "⚠ VISITOR_SALT not set in env — using a random per-process value. "
        "Unique-visitor counts will reset across restarts until VISITOR_SALT "
        "is set in Render env vars.")

def _analytics_db():
    conn = sqlite3.connect(ANALYTICS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_analytics_db():
    with _analytics_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id            TEXT PRIMARY KEY,
                ts            TEXT NOT NULL,
                ts_iso        TEXT NOT NULL,
                event         TEXT NOT NULL,
                path          TEXT,
                title         TEXT,
                referrer      TEXT,
                utm_source    TEXT,
                utm_medium    TEXT,
                utm_campaign  TEXT,
                visitor_hash  TEXT NOT NULL,
                session_id    TEXT,
                country       TEXT,
                device_type   TEXT,
                browser       TEXT,
                os            TEXT,
                screen_w      INTEGER,
                lang          TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_ts_iso ON events(ts_iso)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_visitor ON events(visitor_hash)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_event ON events(event)")
        conn.commit()

def _visitor_hash(ip: str, ua: str) -> str:
    import hashlib
    return hashlib.sha256(f"{ip}|{ua}|{VISITOR_SALT}".encode()).hexdigest()[:16]

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("jyogi_api")

# ── Config ────────────────────────────────────────────────────
LOG_FILE       = Path("/tmp/jyogi_submissions.json")
# LOG_SECRET now FAILS CLOSED (2026-08-14 rebase): a random per-process value
# silently changed on every Render restart and became an unusable operational
# credential. If unset, privileged log functionality is rejected until the env
# var is configured. (X-Log-Secret header auth from R1 is preserved below.)
LOG_SECRET     = os.getenv("LOG_SECRET", "").strip()
if not LOG_SECRET:
    logging.getLogger("jyogi_api").warning(
        "LOG_SECRET not set — log read/ingest endpoints will reject all "
        "requests until LOG_SECRET is configured in the environment.")

# SESSION_SECRET signs admin session cookies (added in rebase). Fails closed:
# without it, admin login returns 503 and no admin route can be reached.
SESSION_SECRET = os.getenv("SESSION_SECRET", "").strip()

# Server-side secret for the daily paid-report download token.
# NEVER shipped to the browser. If unset, a random per-process value is used
# (so the daily token is unknowable until REPORT_TOKEN_SECRET is set in env).
REPORT_TOKEN_SECRET = os.getenv("REPORT_TOKEN_SECRET", "")
if not REPORT_TOKEN_SECRET:
    import secrets as _sec2
    REPORT_TOKEN_SECRET = _sec2.token_hex(16)
    logging.getLogger("jyogi_api").warning(
        "⚠ REPORT_TOKEN_SECRET not set in env — using random token. "
        "Paid reports will be unlockable only after you set REPORT_TOKEN_SECRET in Render env vars.")

SHEETS_WEBHOOK = os.getenv("SHEETS_WEBHOOK_URL", "")
IST            = timedelta(hours=5, minutes=30)

_MEM_LOG: list[dict] = []
_MAX_MEM = 2000

_rate_state: dict[str, tuple[int, float]] = defaultdict(lambda: (0, time.time()))
MAX_CALLS = 20

pdf_store: dict[str, str] = {}

# ── Geocoder ──────────────────────────────────────────────────
_geocoder  = None
_geocache: dict[str, dict] = {}
try:
    from geopy.geocoders import Nominatim
    _geocoder = Nominatim(user_agent="jyogi_api_v3")
except ImportError:
    log.warning("geopy not installed — geocoding disabled")


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def check_rate(ip: str) -> bool:
    count, start = _rate_state[ip]
    now = time.time()
    if now - start > 3600:
        _rate_state[ip] = (1, now); return True
    if count >= MAX_CALLS: return False
    _rate_state[ip] = (count + 1, start); return True

def client_ip(request: Request) -> str:
    return (request.headers.get("X-Forwarded-For","").split(",")[0].strip()
            or (request.client.host if request.client else "unknown"))

def now_ist() -> str:
    return (datetime.now(timezone.utc)+IST).strftime("%d %b %Y %I:%M:%S %p IST")

def geocode(city: str) -> dict | None:
    if not city or not _geocoder: return None
    if city in _geocache: return _geocache[city]
    try:
        loc = _geocoder.geocode(city.strip(), timeout=8)
        if not loc: return None
        r = {"lat": loc.latitude, "lon": loc.longitude, "address": loc.address}
        _geocache[city] = r; return r
    except Exception as e:
        log.warning("Geocode error '%s': %s", city, e); return None

def read_log():
    try:
        if LOG_FILE.exists():
            return json.loads(LOG_FILE.read_text())
    except: pass
    return []

def write_log(data):
    try: LOG_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e: log.warning("Log write error: %s", e)

def _hash_ip(ip: str) -> str:
    """One-way hash IP for privacy — cannot be reversed."""
    import hashlib
    return hashlib.sha256(ip.encode()).hexdigest()[:12]

def _minimise_entry(entry: dict) -> dict:
    """Strip or hash sensitive fields before logging."""
    e = dict(entry)
    # Hash IP — store pseudonymous identifier only
    if "ip" in e:
        e["ip"] = _hash_ip(e["ip"])
    # Store year only from DOB, not full date
    if "dob" in e and e["dob"]:
        try:
            e["dob"] = e["dob"].split("-")[0]  # keep year only: "1990" not "1990-05-15"
        except Exception:
            e["dob"] = "—"
    return e

def append_log(entry: dict):
    global _MEM_LOG
    entry["ts"] = now_ist()
    safe_entry = _minimise_entry(entry)
    _MEM_LOG.insert(0, safe_entry)
    if len(_MEM_LOG) > _MAX_MEM: _MEM_LOG = _MEM_LOG[:_MAX_MEM]
    disk = read_log(); disk.insert(0, safe_entry); write_log(disk[:_MAX_MEM])
    if SHEETS_WEBHOOK:
        try:
            import requests as _req
            _req.post(SHEETS_WEBHOOK, json=entry, timeout=8, allow_redirects=True)
        except: pass


# ══════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _MEM_LOG
    _MEM_LOG = read_log()[:_MAX_MEM]
    log.info("🪐 Jyogi API v3 starting — %d log entries loaded", len(_MEM_LOG))
    init_applications_db()
    init_analytics_db()
    yield
    for path in pdf_store.values():
        try: Path(path).unlink(missing_ok=True)
        except: pass

app = FastAPI(
    title="Jyogi AI API",
    description="Vedic Astrology · Tarot · Crystal — Backend (v3)",
    version="3.0.0",
    lifespan=lifespan,
)

_ALLOWED_ORIGINS = [
    "https://jyogi.in",
    "https://www.jyogi.in",
    "https://v2.jyogi.in",                # Cloudflare Pages staging subdomain
    "https://yogikrishna1008.github.io",  # Cloudflare preview / GitHub Pages
]
# Allow localhost in development
if os.getenv("ENVIRONMENT", "production") == "development":
    _ALLOWED_ORIGINS += ["http://localhost:5500", "http://127.0.0.1:5500"]

app.add_middleware(CORSMiddleware,
    allow_credentials=True,   # required so the admin session cookie is sent cross-site
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Log-Secret", "X-Report-Token"],
)


# ══════════════════════════════════════════════════════════════
# REQUEST / RESPONSE MODELS
# ══════════════════════════════════════════════════════════════

class GeocodeReq(BaseModel):
    city: str = Field(..., min_length=2, max_length=100)

class PlanetsReq(BaseModel):
    year: int; month: int; day: int
    hour: float = 12.0          # IST decimal (e.g. 8.333 for 8:20 AM)
    lat:  float = 20.0          # birth latitude
    lon:  float = 78.0          # birth longitude
    city: Optional[str] = None  # if provided, geocode for lat/lon

class PanchangReq(BaseModel):
    year: int; month: int; day: int

class MuhurtaReq(BaseModel):
    activity: str
    year:  int; month: int; day: int   # start date
    days:  int = 7

class ChartFullReq(BaseModel):
    name:  str = Field(..., min_length=1, max_length=80)
    year:  int; month: int; day: int
    hour:  float = 12.0        # IST decimal
    city:  str = Field(..., min_length=2)
    question: Optional[str] = Field(None, max_length=500)

class CompatReq(BaseModel):
    y1: int; m1: int; d1: int
    h1: int = 12; min1: int = 0
    y2: int; m2: int; d2: int
    h2: int = 12; min2: int = 0
    name1: str = "Person A"
    name2: str = "Person B"

class LogReq(BaseModel):
    secret: str; entry: dict

class ApplyReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    topic: str = Field(..., min_length=1, max_length=120)
    question: str = Field(..., min_length=30, max_length=2000)
    tried: str = Field(..., min_length=1, max_length=2000)
    birth_details: str = Field("", max_length=300)
    source: str = Field("", max_length=120)
    # Honeypot — real visitors never fill this field (hidden via CSS on the form).
    website: str = Field("", max_length=200)

class ApplyStatusReq(BaseModel):
    status: str = Field(..., pattern="^(new|contacted|confirmed|completed|declined)$")

class AnalyticsEventReq(BaseModel):
    event:        str = Field(..., min_length=1, max_length=40)   # page_view, whatsapp_click, ...
    path:         str = Field("", max_length=300)
    title:        str = Field("", max_length=200)
    referrer:     str = Field("", max_length=500)
    utm_source:   str = Field("", max_length=100)
    utm_medium:   str = Field("", max_length=100)
    utm_campaign: str = Field("", max_length=100)
    session_id:   str = Field("", max_length=64)
    device_type:  str = Field("", max_length=20)   # mobile | desktop | tablet
    browser:      str = Field("", max_length=40)
    os:           str = Field("", max_length=40)
    screen_w:     int = 0
    lang:         str = Field("", max_length=10)

class InsightReq(BaseModel):
    # Legacy field — still accepted for backward compatibility during deploy
    prompt: str = ""
    max_tokens: int = 300
    # NEW structured fields — browser sends facts, server builds the prompt
    kind: str = ""            # "tarot_question" | "tarot_spread" | "chart_question" | "chart_insight"
    question: str = ""        # user's question (optional)
    cards: str = ""           # comma-separated card names with positions
    spread: str = ""          # spread name
    lagna: str = ""
    moon: str = ""
    nakshatra: str = ""
    dasha: str = ""
    dasha_yrs: str = ""
    lang: str = "en"          # "en" | "hi" — controls AI response language


# ══════════════════════════════════════════════════════════════
# ENDPOINTS
# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
# ADMIN AUTH — Basic Auth on a hidden URL.
# Credentials live in Render env vars ADMIN_USER and ADMIN_PASS.
# Without those env vars set, the admin route returns 503.
# ══════════════════════════════════════════════════════════════
_admin_security = HTTPBasic(auto_error=False, realm="Jyogi Admin")

def verify_admin(credentials: HTTPBasicCredentials = Depends(_admin_security)):
    """Constant-time-compare username and password against env vars."""
    correct_user = os.getenv("ADMIN_USER", "").strip()
    correct_pass = os.getenv("ADMIN_PASS", "").strip()
    if not correct_user or not correct_pass:
        raise HTTPException(
            status_code=503,
            detail="Admin access not configured on server",
        )
    if credentials is None:
        # No credentials supplied → prompt the browser
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": 'Basic realm="Jyogi Admin"'},
        )
    user_ok = _ct_eq(credentials.username.encode("utf-8"), correct_user.encode("utf-8"))
    pass_ok = _ct_eq(credentials.password.encode("utf-8"), correct_pass.encode("utf-8"))
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": 'Basic realm="Jyogi Admin"'},
        )
    return credentials.username


@app.get("/p/y4k7", response_class=HTMLResponse, include_in_schema=False)
def admin_paste_page(_user: str = Depends(verify_admin)):
    """Serve the admin paste page — only visible to authenticated admin."""
    try:
        return open(os.path.join(os.path.dirname(__file__), "admin_paste.html"),
                    encoding="utf-8").read()
    except FileNotFoundError:
        raise HTTPException(500, "Admin page file missing on server")


# ══════════════════════════════════════════════════════════════
# ADMIN SESSIONS (rebase 2026-08-14) — HMAC-signed cookie, no framework.
#
# Reconciles with the EXISTING dev security rather than replacing it:
#   - REPORT_TOKEN_SECRET / X-Report-Token gating on /api/report is PRESERVED.
#   - X-Log-Secret log auth is PRESERVED.
#   - This ADDS a real server-side admin session so the browser no longer
#     needs any client-derived token. The old client _localToken()/jyogi1008om
#     scheme and the /api/admin-token minter are removed.
#
#   POST /api/admin/login {user,pass} → __Host- session cookie
#   GET  /api/admin/session           → {authenticated}
#   POST /api/admin/logout            → clears cookie
#
# Cookie: __Host-jyogi_admin — the prefix forces Secure + Path=/ + host-only
# (no Domain), ideal for the api.jyogi.in target. SameSite is env-driven:
# "none" today (cross-site vs jyogi.in), "lax" after the api.jyogi.in cutover.
# ══════════════════════════════════════════════════════════════
import hmac as _hmac, hashlib as _hashlib, base64 as _b64

SESSION_COOKIE   = "__Host-jyogi_admin"
SESSION_TTL_SECS = 8 * 60 * 60
COOKIE_SAMESITE  = (os.getenv("COOKIE_SAMESITE", "none") or "none").strip().lower()

def _b64u(raw: bytes) -> str:
    return _b64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
def _b64u_dec(s: str) -> bytes:
    return _b64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

def _sign_session(user: str, ttl: int = SESSION_TTL_SECS) -> str:
    if not SESSION_SECRET:
        raise HTTPException(503, "Admin sessions not configured on server")
    exp = int(time.time()) + ttl
    payload = json.dumps({"u": user, "exp": exp}, separators=(",", ":")).encode()
    sig = _hmac.new(SESSION_SECRET.encode(), payload, _hashlib.sha256).digest()
    return f"{_b64u(payload)}.{_b64u(sig)}"

def _verify_session(token: str):
    if not token or not SESSION_SECRET or "." not in token:
        return None
    try:
        p_b64, s_b64 = token.split(".", 1)
        payload = _b64u_dec(p_b64)
        expect = _hmac.new(SESSION_SECRET.encode(), payload, _hashlib.sha256).digest()
        if not _hmac.compare_digest(expect, _b64u_dec(s_b64)):
            return None
        data = json.loads(payload)
        if int(data.get("exp", 0)) < int(time.time()):
            return None
        return str(data.get("u") or "")
    except Exception:
        return None

def verify_admin_session(request: Request) -> str:
    user = _verify_session(request.cookies.get(SESSION_COOKIE, ""))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Admin authentication required")
    return user

_login_attempts: dict = {}
def _login_allowed(ip: str) -> bool:
    count, start = _login_attempts.get(ip, (0, time.time()))
    now = time.time()
    if now - start > 900:
        _login_attempts[ip] = (1, now); return True
    if count >= 8:
        return False
    _login_attempts[ip] = (count + 1, start); return True

class AdminLoginReq(BaseModel):
    user: str = Field(..., min_length=1, max_length=120)
    password: str = Field(..., min_length=1, max_length=200)

@app.post("/api/admin/login", include_in_schema=False)
def admin_login(body: AdminLoginReq, request: Request):
    from fastapi.responses import JSONResponse
    ip = client_ip(request)
    if not _login_allowed(ip):
        raise HTTPException(429, "Too many login attempts. Please wait and try again.")
    correct_user = os.getenv("ADMIN_USER", "").strip()
    correct_pass = os.getenv("ADMIN_PASS", "").strip()
    if not correct_user or not correct_pass:
        raise HTTPException(503, "Admin access not configured on server")
    u_ok = _ct_eq((body.user or "").encode(), correct_user.encode())
    p_ok = _ct_eq((body.password or "").encode(), correct_pass.encode())
    if not (u_ok and p_ok):
        raise HTTPException(401, "Invalid credentials")
    resp = JSONResponse({"authenticated": True})
    resp.set_cookie(key=SESSION_COOKIE, value=_sign_session(body.user.strip()),
                    max_age=SESSION_TTL_SECS, httponly=True, secure=True,
                    samesite=COOKIE_SAMESITE, path="/")
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp

@app.get("/api/admin/session", include_in_schema=False)
def admin_session(request: Request):
    from fastapi.responses import JSONResponse
    user = _verify_session(request.cookies.get(SESSION_COOKIE, ""))
    resp = JSONResponse({"authenticated": bool(user)})
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp

@app.post("/api/admin/logout", include_in_schema=False)
def admin_logout():
    from fastapi.responses import JSONResponse
    resp = JSONResponse({"authenticated": False})
    resp.delete_cookie(key=SESSION_COOKIE, path="/", samesite=COOKIE_SAMESITE, secure=True)
    resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp

# Admin crystal catalogue — READ-ONLY (no CRUD; no durable store on free tier).
@app.get("/api/admin/crystals", include_in_schema=False)
def admin_crystals_status(_admin: str = Depends(verify_admin_session)):
    from fastapi.responses import JSONResponse
    return JSONResponse({"canonical_source": "crystals_data.js", "writable": False,
                         "persistence": "none (Render /tmp ephemeral) — edit crystals_data.js"},
                        headers={"X-Robots-Tag": "noindex, nofollow"})


# ══════════════════════════════════════════════════════════════
# CONSULTATION APPLICATIONS (apply.html)
#
#   POST /api/apply                    — public, rate-limited submit
#   GET  /api/admin/applications       — admin queue, newest first
#   POST /api/admin/applications/{id}  — admin: update status
# ══════════════════════════════════════════════════════════════

_apply_rate_state: dict[str, tuple[int, float]] = defaultdict(lambda: (0, time.time()))
APPLY_MAX_PER_HOUR = 5

def _apply_rate_ok(ip: str) -> bool:
    count, start = _apply_rate_state[ip]
    now = time.time()
    if now - start > 3600:
        _apply_rate_state[ip] = (1, now); return True
    if count >= APPLY_MAX_PER_HOUR: return False
    _apply_rate_state[ip] = (count + 1, start); return True

@app.post("/api/apply")
def api_apply(body: ApplyReq, request: Request):
    ip = client_ip(request)

    # Honeypot: a real visitor never sees or fills this field.
    if body.website.strip():
        log.warning("Apply honeypot triggered from %s", _hash_ip(ip))
        return {"received": True, "id": str(uuid.uuid4())}  # fake success, no write

    if not _apply_rate_ok(ip):
        raise HTTPException(429, "Too many applications from this connection. Please try again later.")

    app_id = str(uuid.uuid4())
    with _apps_db() as conn:
        conn.execute(
            "INSERT INTO applications (id, created_at, name, topic, question, tried, "
            "birth_details, source, ip_hash, status) VALUES (?,?,?,?,?,?,?,?,?,'new')",
            (app_id, now_ist(), body.name.strip(), body.topic.strip(),
             body.question.strip(), body.tried.strip(), body.birth_details.strip(),
             body.source.strip(), _hash_ip(ip)),
        )
        conn.commit()

    log.info("New application %s — topic: %s", app_id, body.topic)
    return {"received": True, "id": app_id}

@app.get("/api/admin/applications")
def admin_list_applications(status: str = "", _admin: str = Depends(verify_admin_session)):
    from fastapi.responses import JSONResponse
    with _apps_db() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM applications WHERE status=? ORDER BY created_at DESC",
                (status,)).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM applications ORDER BY created_at DESC").fetchall()
    return JSONResponse({"applications": [dict(r) for r in rows]},
                        headers={"X-Robots-Tag": "noindex, nofollow"})

@app.post("/api/admin/applications/{app_id}")
def admin_update_application(app_id: str, body: ApplyStatusReq,
                             _admin: str = Depends(verify_admin_session)):
    with _apps_db() as conn:
        cur = conn.execute("UPDATE applications SET status=? WHERE id=?",
                          (body.status, app_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(404, "Application not found")
    return {"updated": True, "id": app_id, "status": body.status}

@app.get("/admin/applications", response_class=HTMLResponse, include_in_schema=False)
def admin_applications_page():
    # No auth dependency here: the page itself renders a login form and
    # checks /api/admin/session client-side — the data underneath (the
    # /api/admin/applications endpoints) stays behind verify_admin_session.
    try:
        return open(os.path.join(os.path.dirname(__file__), "admin_applications.html"),
                    encoding="utf-8").read()
    except FileNotFoundError:
        raise HTTPException(500, "Admin applications page file missing on server")


# ══════════════════════════════════════════════════════════════
# VISITOR ANALYTICS
#
#   POST /api/analytics/event            — public, rate-limited beacon
#   GET  /api/analytics/count            — public, footer counter (this month)
#   GET  /api/admin/analytics/summary    — admin dashboard data
#   GET  /admin/analytics                — admin dashboard page
# ══════════════════════════════════════════════════════════════

_analytics_rate_state: dict[str, tuple[int, float]] = defaultdict(lambda: (0, time.time()))
ANALYTICS_MAX_PER_MIN = 60   # generous — one page can fire several events (view + clicks)

def _analytics_rate_ok(ip: str) -> bool:
    count, start = _analytics_rate_state[ip]
    now = time.time()
    if now - start > 60:
        _analytics_rate_state[ip] = (1, now); return True
    if count >= ANALYTICS_MAX_PER_MIN: return False
    _analytics_rate_state[ip] = (count + 1, start); return True

# Closed event vocabulary — anything else is silently dropped. Keeps the table
# queryable (no free-text event soup) and stops a client from writing whatever
# it wants into the analytics DB.
ALLOWED_EVENTS = {
    "page_view", "whatsapp_click", "consultation_click", "apply_click",
    "book_now_click", "buy_click", "crystal_view", "kundli_generate",
    "report_generate", "share_click", "language_change", "search",
}

# Server-side bot filter — a beacon fired by a crawler or uptime monitor that
# happens to run JS (or hits the endpoint directly) should never inflate the
# counter. Client-side JS already keeps most non-browser bots out (they don't
# execute the tracker), this is the backstop for the ones that do.
_BOT_UA_MARKERS = (
    "bot", "spider", "crawl", "slurp", "bingpreview", "facebookexternalhit",
    "pingdom", "uptimerobot", "statuscake", "monitor", "headlesschrome",
    "phantomjs", "curl/", "wget/", "python-requests", "go-http-client",
)

def _looks_like_bot(ua: str) -> bool:
    u = (ua or "").lower()
    if not u:
        return True   # no UA at all — not a real browser visit
    return any(marker in u for marker in _BOT_UA_MARKERS)

@app.post("/api/analytics/event")
def api_analytics_event(body: AnalyticsEventReq, request: Request):
    ip = client_ip(request)
    if not _analytics_rate_ok(ip):
        # Silent no-op — a tracking beacon should never surface an error to the visitor.
        return {"ok": True}

    event_name = body.event.strip()
    if event_name not in ALLOWED_EVENTS:
        return {"ok": True}   # silently dropped — not a recognised event

    ua = request.headers.get("User-Agent", "")[:300]
    if _looks_like_bot(ua):
        return {"ok": True}   # silently dropped — bot/crawler/monitor traffic

    country = request.headers.get("CF-IPCountry", "") or ""
    vhash = _visitor_hash(ip, ua)   # ip used transiently for the hash, never stored

    with _analytics_db() as conn:
        conn.execute(
            "INSERT INTO events (id, ts, ts_iso, event, path, title, referrer, utm_source, "
            "utm_medium, utm_campaign, visitor_hash, session_id, country, device_type, "
            "browser, os, screen_w, lang) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (str(uuid.uuid4()), now_ist(), datetime.now(timezone.utc).isoformat(),
             event_name, body.path.strip(),
             body.title.strip(), body.referrer.strip()[:500], body.utm_source.strip(),
             body.utm_medium.strip(), body.utm_campaign.strip(), vhash,
             body.session_id.strip(), country, body.device_type.strip(),
             body.browser.strip(), body.os.strip(), body.screen_w, body.lang.strip()),
        )
        conn.commit()
    return {"ok": True}

@app.get("/api/analytics/count")
def api_analytics_count():
    """Public, lightweight — powers the subtle footer counter only.
    Deliberately minimal: no page-level, device, or source breakdown here —
    that detail stays behind /api/admin/analytics/summary."""
    from fastapi.responses import JSONResponse
    now = datetime.now(timezone.utc) + IST
    today_str = now.strftime("%d %b %Y")
    month_str = now.strftime("%b %Y")   # matches now_ist() format: "28 Aug 2026 ..."
    with _analytics_db() as conn:
        today_n = conn.execute(
            "SELECT COUNT(DISTINCT visitor_hash) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ?", (f"{today_str}%",)
        ).fetchone()["n"]
        month_n = conn.execute(
            "SELECT COUNT(DISTINCT visitor_hash) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ?", (f"__ {month_str}%",)
        ).fetchone()["n"]
    return JSONResponse({"today": today_n, "month": month_n},
                        headers={"Cache-Control": "public, max-age=300"})

@app.get("/api/admin/analytics/summary")
def admin_analytics_summary(range: str = "today", _admin: str = Depends(verify_admin_session)):
    """range: today | 7d | 30d | month"""
    from fastapi.responses import JSONResponse
    now = datetime.now(timezone.utc) + IST
    today_str = now.strftime("%d %b %Y")
    month_str = now.strftime("%b %Y")
    five_min_ago_iso = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()

    with _analytics_db() as conn:
        today_visitors = conn.execute(
            "SELECT COUNT(DISTINCT visitor_hash) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ?", (f"{today_str}%",)).fetchone()["n"]
        today_views = conn.execute(
            "SELECT COUNT(*) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ?", (f"{today_str}%",)).fetchone()["n"]
        online_now = conn.execute(
            "SELECT COUNT(DISTINCT visitor_hash) AS n FROM events WHERE ts_iso >= ?",
            (five_min_ago_iso,)).fetchone()["n"]
        month_visitors = conn.execute(
            "SELECT COUNT(DISTINCT visitor_hash) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ?", (f"__ {month_str}%",)).fetchone()["n"]
        month_views = conn.execute(
            "SELECT COUNT(*) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ?", (f"__ {month_str}%",)).fetchone()["n"]

        top_pages = conn.execute(
            "SELECT path, COUNT(*) AS n FROM events WHERE event='page_view' "
            "AND ts LIKE ? GROUP BY path ORDER BY n DESC LIMIT 10",
            (f"__ {month_str}%",)).fetchall()

        # Traffic source bucketing: utm_source wins, else referrer domain, else Direct.
        source_rows = conn.execute(
            "SELECT utm_source, referrer FROM events WHERE event='page_view' AND ts LIKE ?",
            (f"__ {month_str}%",)).fetchall()

        devices = conn.execute(
            "SELECT device_type, COUNT(DISTINCT visitor_hash) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ? AND device_type != '' "
            "GROUP BY device_type ORDER BY n DESC", (f"__ {month_str}%",)).fetchall()

        countries = conn.execute(
            "SELECT country, COUNT(DISTINCT visitor_hash) AS n FROM events "
            "WHERE event='page_view' AND ts LIKE ? AND country != '' "
            "GROUP BY country ORDER BY n DESC LIMIT 10", (f"__ {month_str}%",)).fetchall()

        campaigns = conn.execute(
            "SELECT utm_campaign, utm_source, COUNT(DISTINCT visitor_hash) AS n FROM events "
            "WHERE event='page_view' AND utm_campaign != '' AND ts LIKE ? "
            "GROUP BY utm_campaign, utm_source ORDER BY n DESC LIMIT 10",
            (f"__ {month_str}%",)).fetchall()

        event_totals = conn.execute(
            "SELECT event, COUNT(*) AS n FROM events WHERE ts LIKE ? "
            "GROUP BY event ORDER BY n DESC", (f"__ {month_str}%",)).fetchall()

    import urllib.parse as _up
    source_counts: dict[str, int] = defaultdict(int)
    for r in source_rows:
        if r["utm_source"]:
            source_counts[r["utm_source"]] += 1
        elif r["referrer"]:
            try:
                domain = _up.urlparse(r["referrer"]).netloc.replace("www.", "") or "Direct"
            except Exception:
                domain = "Direct"
            source_counts[domain] += 1
        else:
            source_counts["Direct"] += 1

    return JSONResponse({
        "today": {"visitors": today_visitors, "page_views": today_views, "online_now": online_now},
        "month": {"visitors": month_visitors, "page_views": month_views},
        "top_pages": [{"path": r["path"], "views": r["n"]} for r in top_pages],
        "sources": sorted([{"source": k, "visits": v} for k, v in source_counts.items()],
                          key=lambda x: -x["visits"])[:10],
        "devices": [{"device": r["device_type"], "visitors": r["n"]} for r in devices],
        "countries": [{"country": r["country"], "visitors": r["n"]} for r in countries],
        "campaigns": [{"campaign": r["utm_campaign"], "source": r["utm_source"], "visitors": r["n"]}
                      for r in campaigns],
        "events": [{"event": r["event"], "count": r["n"]} for r in event_totals],
    }, headers={"X-Robots-Tag": "noindex, nofollow"})

@app.get("/admin/analytics", response_class=HTMLResponse, include_in_schema=False)
def admin_analytics_page():
    try:
        return open(os.path.join(os.path.dirname(__file__), "admin_analytics.html"),
                    encoding="utf-8").read()
    except FileNotFoundError:
        raise HTTPException(500, "Admin analytics page file missing on server")


@app.get("/health")
@app.get("/api/health")
def health():
    return {"status":"ok","version":"3.0.0","sweph":True,"ts":now_ist()}

@app.get("/")
@app.get("/api/ping")
def root():
    return {"status":"ok","service":"Jyogi AI API v3"}


# ── Geocode ───────────────────────────────────────────────────
@app.post("/api/geocode")
def api_geocode(body: GeocodeReq, request: Request):
    if not check_rate(client_ip(request)):
        raise HTTPException(429, "Too many requests")
    r = geocode(body.city)
    if not r: raise HTTPException(404, f"City not found: {body.city!r}")
    return r


# ── NEW: Planetary positions ──────────────────────────────────
@app.post("/api/planets")
def api_planets(body: PlanetsReq, request: Request):
    """
    Returns all 9 graha sidereal longitudes, lagna, and dasha.
    This is the core chart engine — stays on server.
    """
    if not check_rate(client_ip(request)):
        raise HTTPException(429, "Too many requests")

    # Resolve lat/lon
    lat, lon = body.lat, body.lon
    if body.city:
        geo = geocode(body.city)
        if geo:
            lat, lon = geo['lat'], geo['lon']

    ut = ist_to_ut(body.hour)
    jd = julian_day(body.year, body.month, body.day, ut)

    planets = get_all_planets(jd)
    lagna   = get_lagna(jd, lat, lon)
    dasha   = get_dasha(planets['Moon'], jd)

    # Import retrograde detection
    try:
        from vedic_engine import get_planet_retrograde
    except Exception:
        def get_planet_retrograde(p, j): return False

    # Enrich with nakshatra/rashi info + retrograde flag + HOUSE (Whole Sign from Lagna)
    lagna_sign = int(lagna / 30) % 12
    enriched = {}
    for p, lon_val in planets.items():
        nk_idx    = int(lon_val / (360/27))
        ms_idx    = int(lon_val / 30) % 12
        # Whole Sign house: ((planet_sign - lagna_sign) mod 12) + 1
        house_num = ((ms_idx - lagna_sign) % 12) + 1
        enriched[p] = {
            'lon':        round(lon_val, 3),
            'rashi':      RASHIS[ms_idx],
            'rashi_idx':  ms_idx,
            'house':      house_num,
            'nakshatra':  NAKSH[nk_idx],
            'nk_idx':     nk_idx,
            'pada':       int((lon_val % (360/27)) / (360/27/4)) + 1,
            'retrograde': get_planet_retrograde(p, jd),
        }

    lagna_ms = int(lagna / 30)
    return {
        'planets': enriched,
        'lagna': {
            'lon':       round(lagna, 3),
            'rashi':     RASHIS[lagna_ms],
            'rashi_idx': lagna_ms,
        },
        'dasha': dasha,
        'lat': lat, 'lon': lon,
    }


# ── NEW: Full chart (chart + yogas + navamsha + numerology) ───
@app.post("/api/chart-full")
def api_chart_full(body: ChartFullReq, request: Request):
    """
    Complete birth chart analysis — all proprietary calculations server-side.
    """
    if not check_rate(client_ip(request)):
        raise HTTPException(429, "Too many requests")

    geo = geocode(body.city)
    if not geo: raise HTTPException(404, f"City not found: {body.city!r}")

    ut = ist_to_ut(body.hour)
    jd = julian_day(body.year, body.month, body.day, ut)

    planets  = get_all_planets(jd)
    lagna    = get_lagna(jd, geo['lat'], geo['lon'])
    dasha    = get_dasha(planets['Moon'], jd)
    yogas    = detect_yogas(planets, lagna)
    # Pass lagna so the D9 lagna sign is included in the response
    planets_clean = {k: v for k, v in planets.items() if k != 'jd'}
    navamsha = calc_navamsha(planets_clean, lagna_lon=lagna)
    numerology = calc_numerology(body.day, body.month, body.year)

    enriched = {}
    for p, lon_val in planets.items():
        nk_idx = int(lon_val / (360/27))
        ms_idx    = int(lon_val / 30) % 12
        house_num = ((ms_idx - int(lagna/30) % 12) % 12) + 1
        enriched[p] = {
            'lon': round(lon_val,3),
            'rashi': RASHIS[ms_idx], 'rashi_idx': ms_idx,
            'house': house_num,
            'nakshatra': NAKSH[nk_idx], 'nk_idx': nk_idx,
            'pada': int((lon_val%(360/27))/(360/27/4))+1,
        }

    lagna_ms = int(lagna/30)

    append_log({'type':'chart','name':body.name,'dob':f"{body.year}-{body.month:02d}-{body.day:02d}",
                'city':body.city,'lagna':RASHIS[lagna_ms],'moon':enriched['Moon']['rashi']})

    return {
        'name':      body.name,
        'planets':   enriched,
        'lagna':     {'lon':round(lagna,3),'rashi':RASHIS[lagna_ms],'rashi_idx':lagna_ms},
        'dasha':     dasha,
        'yogas':     yogas,
        'navamsha':  navamsha,
        'numerology':numerology,
        'geo':       geo,
    }


# ── NEW: Panchang ─────────────────────────────────────────────
@app.post("/api/panchang")
def api_panchang(body: PanchangReq, request: Request):
    """Returns full Panchang for a given date using Swiss Ephemeris."""
    if not check_rate(client_ip(request)):
        raise HTTPException(429, "Too many requests")
    if not _VEDIC_OK:
        raise HTTPException(503, "Calculation engine loading — try again in 30 seconds")
    try:
        return calc_panchang(body.year, body.month, body.day)
    except Exception as e:
        raise HTTPException(500, str(e))


# ── NEW: Muhurta grid ─────────────────────────────────────────
@app.post("/api/muhurta")
def api_muhurta(body: MuhurtaReq, request: Request):
    """Returns scored Muhurta grid for activity over N days."""
    if not check_rate(client_ip(request)):
        raise HTTPException(429, "Too many requests")
    if body.activity not in ACTIVITY_DATA:
        raise HTTPException(400, f"Unknown activity: {body.activity!r}. "
                            f"Valid: {list(ACTIVITY_DATA.keys())}")
    try:
        from_date = date(body.year, body.month, body.day)
        grid = get_muhurta_grid(body.activity, from_date, min(body.days, 30))
        return {'activity': body.activity, 'grid': grid}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Compatibility (existing, already working) ─────────────────
@app.post("/api/compatibility")
def api_compatibility(body: CompatReq, request: Request):
    if not check_rate(client_ip(request)):
        raise HTTPException(429, "Too many requests")
    try:
        result = calculate_ashtakoot(
            dob_male        = (body.y1, body.m1, body.d1),
            dob_female      = (body.y2, body.m2, body.d2),
            time_male_ist   = (body.h1, body.min1),
            time_female_ist = (body.h2, body.min2),
            name_male       = body.name1,
            name_female     = body.name2,
        )
        return result
    except Exception as e:
        log.error("Compat error: %s", e)
        raise HTTPException(500, str(e))


# ── AI Insight (existing) ─────────────────────────────────────
# ══════════════════════════════════════════════════════════════
# PROMPT TEMPLATES — proprietary, server-side only (never sent to browser)
# ══════════════════════════════════════════════════════════════
def _build_insight_prompt(body: "InsightReq") -> str:
    """Build the full AI prompt server-side from structured browser data.
    The instruction text lives here, not in the browser source."""
    k = (body.kind or "").strip()
    # Language directive — appended to whichever prompt is built below.
    _lang = (getattr(body, "lang", "en") or "en").strip().lower()
    _hindi_suffix = (
        "\n\nIMPORTANT: Respond ENTIRELY in natural, warm Hindi (Devanagari script). "
        "Use respectful, simple Hindi that a common devotee would understand. "
        "Keep Sanskrit/astrological terms (Lagna, Nakshatra, Dasha, etc.) in their "
        "standard Devanagari forms. Do not mix English sentences."
    ) if _lang == "hi" else (
        "\n\nIMPORTANT: Respond ENTIRELY in natural, warm Odia/Oriya (ଓଡ଼ିଆ script). "
        "Use respectful, simple Odia that a common Odia devotee would understand. "
        "Keep Sanskrit/astrological terms (Lagna, Nakshatra, Dasha, etc.) in their "
        "standard Odia forms. Do not mix English or Hindi sentences."
    ) if _lang == "or" else ""

    if k == "tarot_question":
        return (f'USER QUESTION: "{body.question}"\n\n'
                f'CARDS DRAWN: {body.cards}\n'
                f'SPREAD: {body.spread}\n\n'
                'INSTRUCTION: You are Jyogi, an intuitive tarot reader. Answer the USER QUESTION '
                'directly using these cards as your guide. Speak in second person. Be specific to '
                'their question — not generic spiritual advice. Keep it to 3-4 warm, personal '
                'sentences. End with one clear action or guidance.' + _hindi_suffix)

    if k == "tarot_spread":
        return (f'CARDS DRAWN: {body.cards}\n'
                f'SPREAD: {body.spread}\n\n'
                'INSTRUCTION: You are Jyogi. Give a warm 3-sentence energy reading of this spread. '
                'What energy is present? What should this person be aware of? Be poetic but grounded.' + _hindi_suffix)

    if k == "chart_question":
        return (f'USER QUESTION: "{body.question}"\n\n'
                f'CONTEXT: {body.lagna} Lagna, {body.moon} Moon ({body.nakshatra} nakshatra), '
                f'{body.dasha} Mahadasha ({body.dasha_yrs} yrs remaining).\n\n'
                'INSTRUCTION: You are Jyogi, a warm Vedic astrologer. Answer the USER QUESTION '
                'directly using the CONTEXT. Be personal and specific. Keep it to 3-4 sentences. '
                'End with one practical guidance. Never mention names.' + _hindi_suffix)

    if k == "chart_insight":
        return (f'CONTEXT: {body.lagna} Lagna, {body.moon} Moon ({body.nakshatra} nakshatra), '
                f'{body.dasha} Mahadasha ({body.dasha_yrs} yrs remaining).\n\n'
                'INSTRUCTION: You are Jyogi. Give a warm, poetic 3-sentence Vedic insight. '
                'Be encouraging. Never mention names.' + _hindi_suffix)

    # Fallback: legacy clients that still send a raw prompt
    return body.prompt or ""


@app.post("/api/insight")
def api_insight(body: InsightReq, request: Request):
    if not check_rate(client_ip(request)):
        raise HTTPException(429, "Too many requests")
    # Build the full prompt server-side from structured data.
    # Legacy clients sending raw `prompt` still work via the fallback in _build_insight_prompt.
    effective_prompt = _build_insight_prompt(body)
    if len(effective_prompt.strip()) < 5:
        raise HTTPException(400, "Insufficient data for insight")
    # Override body.prompt so the rest of the handler uses the server-built prompt
    body.prompt = effective_prompt
    api_key = os.getenv("OPENAI_API_KEY","").strip()
    if not api_key:
        raise HTTPException(500, "OPENAI_API_KEY not set")
    # ── Try rule engine first (free, private, instant) ──────────
    try:
        from jyogi_rules import generate_chart_insight, get_tarot_card, get_life_path
        prompt_lower = body.prompt.lower()
        rule_insight = None

        # Chart insight trigger
        if "lagna" in prompt_lower and "mahadasha" in prompt_lower:
            import re
            lagna_m = re.search(r"(\w+)\s+lagna", body.prompt, re.IGNORECASE)
            moon_m  = re.search(r"(\w+)\s+moon", body.prompt, re.IGNORECASE)
            nak_m   = re.search(r"(\w+)\s+nakshatra", body.prompt, re.IGNORECASE)
            dasha_m = re.search(r"(\w+)\s+mahadasha", body.prompt, re.IGNORECASE)
            yrs_m   = re.search(r"([\d.]+)\s+yrs", body.prompt, re.IGNORECASE)
            if lagna_m and dasha_m:
                rule_insight = generate_chart_insight(
                    lagna   = lagna_m.group(1),
                    moon    = moon_m.group(1)  if moon_m  else "unknown",
                    nakshatra = nak_m.group(1) if nak_m   else "unknown",
                    dasha   = dasha_m.group(1),
                    dasha_years_left = float(yrs_m.group(1)) if yrs_m else 5.0
                )

        if rule_insight:
            return {"insight": rule_insight, "status": "ok", "source": "rule_engine"}
    except Exception:
        pass  # Fall through to OpenAI if rule engine fails

    # ── Fallback to OpenAI for complex questions ──────────────
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are Jyogi — a warm Vedic astrologer. Answer directly in 3-4 sentences."},
                {"role":"user","content":body.prompt[:3000]},
            ],
            temperature=0.82,
            max_tokens=min(body.max_tokens, 400),
        )
        return {"insight": resp.choices[0].message.content or "", "status":"ok", "source": "openai"}
    except Exception as e:
        raise HTTPException(500, str(e))


# ── Logging endpoints (existing) ──────────────────────────────
@app.post("/api/log")
def api_save_log(body: LogReq, request: Request):
    if body.secret != LOG_SECRET:
        raise HTTPException(403, "Invalid secret")
    entry = dict(body.entry)
    entry["ip"] = client_ip(request)
    append_log(entry)
    return {"saved": True}

def _check_log_secret(x_log_secret: str):
    if not x_log_secret or not _ct_eq(
            x_log_secret.encode("utf-8"), LOG_SECRET.encode("utf-8")):
        raise HTTPException(403, "Invalid secret")

@app.get("/api/logs")
def api_get_logs(format: str = "json",
                 x_log_secret: str = Header("", alias="X-Log-Secret")):
    _check_log_secret(x_log_secret)
    data = read_log()
    if format == "csv":
        output = io.StringIO()
        if data:
            fields = ["ts","type","name","dob","city","lagna","moon","score","ip"]
            writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
            writer.writeheader(); writer.writerows(data)
        return StreamingResponse(iter([output.getvalue().encode("utf-8-sig")]),
            media_type="text/csv",
            headers={"Content-Disposition":"attachment; filename=jyogi_logs.csv"})
    return StreamingResponse(iter([json.dumps(data, ensure_ascii=False, indent=2).encode()]),
        media_type="application/json",
        headers={"Content-Disposition":"attachment; filename=jyogi_logs.json"})

@app.get("/api/logs/count")
def api_log_count(x_log_secret: str = Header("", alias="X-Log-Secret")):
    _check_log_secret(x_log_secret)
    return {"count": len(read_log()), "mem": len(_MEM_LOG), "ts": now_ist()}

@app.get("/api/logs/stats")
def api_log_stats(x_log_secret: str = Header("", alias="X-Log-Secret")):
    _check_log_secret(x_log_secret)
    data = read_log()
    types = {}; cities = {}
    for e in data:
        t=e.get("type","chart"); types[t]=types.get(t,0)+1
        c=e.get("city","");
        if c: cities[c]=cities.get(c,0)+1
    return {"total":len(data),"by_type":types,
            "top_cities":dict(sorted(cities.items(),key=lambda x:-x[1])[:10]),
            "latest":data[0] if data else None}

# ══════════════════════════════════════════════════════════════
# PDF REPORT GENERATION
# ══════════════════════════════════════════════════════════════
from fastapi.responses import FileResponse
import tempfile, os as _os

class ReportReq(BaseModel):
    year:        int
    month:       int
    day:         int
    hour:        float          # IST decimal (e.g. 3.017 for 03:01 AM)
    lat:         float
    lon:         float
    name:        str   = "Client"
    city:        str   = ""
    report_type: str   = "full"   # "full" or "saturn"

# Per-IP rate limit for expensive PDF generation (3/hour)
_report_rate: dict = {}
_MAX_REPORT_CALLS = 3

def check_report_rate(ip: str) -> bool:
    import time
    count, start = _report_rate.get(ip, (0, time.time()))
    now = time.time()
    if now - start > 3600:
        _report_rate[ip] = (1, now); return True
    if count >= _MAX_REPORT_CALLS: return False
    _report_rate[ip] = (count + 1, start); return True

# ── Paid-report authorization ─────────────────────────────────
# Report types that require a valid daily token. "navamsha" is the free,
# ungated lead-magnet snapshot and is intentionally excluded.
_PAID_REPORT_TYPES = {"full", "saturn"}

def _today_ist_str() -> str:
    import datetime
    try:
        import pytz
        return datetime.datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d")
    except Exception:
        return (datetime.datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d")

def expected_report_token(date_ist: str = "") -> str:
    """Daily-rotating 4-digit token derived from the server-only secret.
    The secret never leaves the server, so this value cannot be recomputed
    in the browser."""
    import hashlib
    d = date_ist or _today_ist_str()
    hval = int(hashlib.sha256((REPORT_TOKEN_SECRET + d).encode()).hexdigest(), 16)
    return str(hval % 9000 + 1000)

# Per-IP failed-token lockout: caps brute-force against the 4-digit space.
# After _MAX_AUTH_FAILS bad tokens in an hour, that IP is blocked for the hour.
_report_auth_fail: dict = {}
_MAX_AUTH_FAILS = 5

def _auth_locked(ip: str) -> bool:
    fails, start = _report_auth_fail.get(ip, (0, time.time()))
    if time.time() - start > 3600:
        _report_auth_fail[ip] = (0, time.time()); return False
    return fails >= _MAX_AUTH_FAILS

def _record_auth_fail(ip: str):
    fails, start = _report_auth_fail.get(ip, (0, time.time()))
    if time.time() - start > 3600:
        _report_auth_fail[ip] = (1, time.time())
    else:
        _report_auth_fail[ip] = (fails + 1, start)

def check_report_auth(report_type: str, token: str, ip: str) -> bool:
    """Return True if this report may be generated.
    Free 'navamsha' → always allowed. Paid types → constant-time token check
    with per-IP failure lockout."""
    if report_type not in _PAID_REPORT_TYPES:
        return True
    if _auth_locked(ip):
        return False
    supplied = (token or "").strip()
    if supplied and _ct_eq(supplied.encode("utf-8"), expected_report_token().encode("utf-8")):
        return True
    _record_auth_fail(ip)
    return False

@app.post("/api/report")
async def generate_report(req: ReportReq, request: Request):
    """
    Generate a Jyogi AI PDF Kundali report and return it as a download.
    report_type = "full"   → 10-page Full Kundali
    report_type = "saturn" → 7-page Saturn Intelligence
    Rate limited: 3 reports per IP per hour.
    """
    _ip = client_ip(request)
    # Authorization for paid report types (full / saturn). Free navamsha is exempt.
    # Reconciled auth (rebase): a valid ADMIN SESSION cookie is accepted, OR the
    # PRESERVED X-Report-Token path (REPORT_TOKEN_SECRET-derived). The browser now
    # uses the session, so it no longer needs any client-derived token.
    # Same generic 403 for missing/invalid/expired/lockout — no oracle.
    if req.report_type in _PAID_REPORT_TYPES:
        _has_session = bool(_verify_session(request.cookies.get(SESSION_COOKIE, "")))
        if not _has_session:
            _report_token = request.headers.get("X-Report-Token", "")
            if not check_report_auth(req.report_type, _report_token, _ip):
                raise HTTPException(403, "Not authorised")
    if not check_report_rate(_ip):
        raise HTTPException(429, "Too many report requests. Please wait before generating another PDF.")
    try:
        import swisseph as swe
        from vedic_engine import (
            julian_day, ist_to_ut, get_all_planets, get_lagna,
            get_planet_retrograde, get_house, lahiri
        )

        # ── Compute chart ───────────────────────────────────────
        ut  = ist_to_ut(req.hour)
        jd  = julian_day(req.year, req.month, req.day, ut)
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

        planets_raw = get_all_planets(jd)
        lagna_lon   = get_lagna(jd, req.lat, req.lon)
        lagna_sign  = int(lagna_lon / 30) % 12
        ayan_val    = lahiri(jd)

        RASHIS_LIST = [
            'Aries','Taurus','Gemini','Cancer','Leo','Virgo',
            'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces'
        ]
        NAKSH_LIST = [
            'Ashwini','Bharani','Krittika','Rohini','Mrigashira','Ardra',
            'Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni',
            'Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha',
            'Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana',
            'Dhanishtha','Shatabhisha','Purva Bhadrapada',
            'Uttara Bhadrapada','Revati'
        ]

        def _enrich(pname, lon):
            sign    = int(lon / 30) % 12
            nk_idx  = int(lon / (360/27))
            pada    = int((lon % (360/27)) / (360/27/4)) + 1
            house   = ((sign - lagna_sign) % 12) + 1
            retro   = get_planet_retrograde(pname, jd)
            speed   = "—"
            try:
                SWE_MAP = {
                    'Sun': swe.SUN,'Moon': swe.MOON,'Mars': swe.MARS,
                    'Mercury': swe.MERCURY,'Jupiter': swe.JUPITER,
                    'Venus': swe.VENUS,'Saturn': swe.SATURN,
                    'Rahu': swe.MEAN_NODE,
                }
                if pname in SWE_MAP:
                    res, _ = swe.calc_ut(
                        jd, SWE_MAP[pname],
                        swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
                    )
                    speed = f"{res[3]:+.4f}"
            except Exception:
                pass
            return {
                'lon': round(lon, 4), 'sign': sign,
                'rashi': RASHIS_LIST[sign], 'rashi_idx': sign,
                'nakshatra': NAKSH_LIST[nk_idx], 'nk_idx': nk_idx,
                'pada': pada, 'house': house,
                'retrograde': retro, 'speed': speed,
            }

        enriched = {
            p: _enrich(p, lon)
            for p, lon in planets_raw.items() if p != 'jd'
        }

        moon_lon    = planets_raw['Moon']
        moon_sign   = int(moon_lon / 30)
        moon_nk     = int(moon_lon / (360/27))

        # ── Build DOB string ────────────────────────────────────
        MON = ['','Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']
        dob_str = f"{req.day:02d} {MON[req.month]} {req.year}"
        ampm    = 'AM' if req.hour < 12 else 'PM'
        h12     = int(req.hour) % 12 or 12
        mn      = int((req.hour % 1) * 60)
        tob_str = f"{h12:02d}:{mn:02d} {ampm} IST"

        # ── Dignity lookup (simple rules) ───────────────────────
        EXALT = {'Sun':0,'Moon':1,'Mars':9,'Mercury':5,'Jupiter':3,
                 'Venus':11,'Saturn':6}   # sign index of exaltation
        DEBIL = {'Sun':6,'Moon':7,'Mars':3,'Mercury':11,'Jupiter':9,
                 'Venus':5,'Saturn':0}
        OWN   = {'Sun':[4],'Moon':[3],'Mars':[0,7],'Mercury':[2,5],
                 'Jupiter':[8,11],'Venus':[1,6],'Saturn':[9,10]}

        def _dignity(pname, sign):
            if EXALT.get(pname) == sign: return "Exalted"
            if DEBIL.get(pname) == sign: return "Debil."
            if sign in OWN.get(pname, []): return "Own"
            return "Neutral"

        # ── Build planet rows for report ────────────────────────
        planet_rows = []
        for pname in ['Sun','Moon','Mars','Mercury','Jupiter',
                      'Venus','Saturn','Rahu','Ketu']:
            if pname not in enriched: continue
            v = enriched[pname]
            deg_in_sign = v['lon'] % 30
            lon_str = f"{RASHIS_LIST[v['sign']][:6]} {deg_in_sign:05.2f}'"
            dig = _dignity(pname, v['sign'])
            planet_rows.append((
                pname, pname[:2],
                lon_str, round(v['lon'], 3),
                RASHIS_LIST[v['sign']], NAKSH_LIST[v['nk_idx']],
                str(v['pada']), v['speed'], dig, v['retrograde']
            ))

        # ── Assemble report data dict ───────────────────────────
        sat_v = enriched.get('Saturn', {})
        report_id = (f"JYG-{req.year}{req.month:02d}{req.day:02d}"
                     f"-{int(jd) % 10000:04d}")

        from jyogi_full_report import D as _D_TMPL, build as _build_full
        from jyogi_saturn_report import REPORT_DATA as _SAT_TMPL, build_report as _build_sat
        from jyogi_navamsha_report import build as _build_navamsha

        D_LIVE = dict(_D_TMPL)
        sat_deg_str = f"{sat_v.get('lon', 0) % 30:.2f}"
        sat_house_str = f"{sat_v.get('house', '—')}th House"
        sat_status = "Retrograde" if sat_v.get('retrograde') else "Direct"
        sat_naksh  = sat_v.get('nakshatra', '—')
        sat_speed  = sat_v.get('speed', '—')
        sat_rashi  = sat_v.get('rashi', '—')

        saturn_natal_block = {
            "rashi"        : sat_rashi,
            "deg"          : f"{sat_deg_str}°",
            "nk"           : sat_naksh,
            "house"        : sat_house_str,
            "status"       : sat_status,
            "speed"        : f"{sat_speed}°/day" if sat_speed != "—" else "—",
            "degree"       : f"{sat_deg_str}°",
            "nakshatra"    : sat_naksh,
            "pada"         : "—",
            "tropical_lon" : f"{sat_v.get('lon', 0):.2f}°",
        }

        D_LIVE.update({
            "name"       : req.name,
            "dob"        : dob_str,
            "tob"        : tob_str,
            "pob"        : req.city or f"{req.lat:.4f}N {req.lon:.4f}E",
            "lagna"      : RASHIS_LIST[lagna_sign],
            "lagna_deg"  : f"{lagna_lon % 30:.2f}",
            "moon"       : RASHIS_LIST[moon_sign],
            "moon_deg"   : f"{moon_lon % 30:.2f}",
            "nakshatra"  : NAKSH_LIST[moon_nk],
            "report_id"  : report_id,
            "planets"    : planet_rows,
            "saturn_natal": saturn_natal_block,
        })

        SAT_LIVE = dict(_SAT_TMPL)
        SAT_LIVE.update({
            "client_name"     : req.name,
            "dob"             : dob_str,
            "report_id"       : report_id,
            "saturn_position" : saturn_natal_block,
            "saturn_transit"  : saturn_natal_block,
        })

        # ── Generate to temp file ───────────────────────────────
        # Sanitize name for safe filename — remove anything except letters/numbers/spaces
        import re as _re
        _safe_name = _re.sub(r'[^a-zA-Z0-9 ]', '', req.name)[:40].strip().replace(' ', '_') or 'Client'
        suffix  = f"_{_safe_name}_{report_id}"
        tmp     = tempfile.NamedTemporaryFile(
            suffix='.pdf', prefix='jyogi', delete=False
        )
        tmp.close()

        if req.report_type == "saturn":
            _build_sat(tmp.name, SAT_LIVE)
            filename = f"Jyogi_Saturn_{_safe_name}.pdf"
        elif req.report_type == "navamsha":
            _build_navamsha(tmp.name, D_LIVE)
            filename = f"Jyogi_Navamsha_Free_{_safe_name}.pdf"
        else:
            _build_full(tmp.name, D_LIVE)
            filename = f"Jyogi_Kundali_{_safe_name}.pdf"

        return FileResponse(
            tmp.name,
            media_type='application/pdf',
            filename=filename,
        )

    except Exception as ex:
        import traceback
        log.error("PDF report error: %s", traceback.format_exc())
        raise HTTPException(500, "Report generation failed. Please try again.")

# ══════════════════════════════════════════════════════════════
# NUMEROLOGY REPORT ENDPOINT
# ══════════════════════════════════════════════════════════════
class NumerologyReportReq(BaseModel):
    name:   str
    year:   int
    month:  int
    day:    int
    gender: str = 'M'

@app.post("/api/numerology-report")
async def numerology_report_endpoint(req: NumerologyReportReq):
    """Generate and return a Jyogi AI Numerology PDF report."""
    try:
        import tempfile
        dob_str = f"{req.year:04d}-{req.month:02d}-{req.day:02d}"
        tmp     = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, prefix='jyogi_num_')
        tmp.close()
        from jyogi_numerology_report import build_numerology_report_safe
        build_numerology_report_safe(tmp.name, req.name, dob_str, req.gender)
        import re as _re2
        _safe_name2 = _re2.sub(r'[^a-zA-Z0-9 ]', '', req.name)[:40].strip().replace(' ', '_') or 'Client'
        filename = f"Jyogi_Numerology_{_safe_name2}.pdf"
        return FileResponse(tmp.name, media_type='application/pdf', filename=filename)
    except Exception as ex:
        import traceback
        log.error("Endpoint error: %s", traceback.format_exc())
        raise HTTPException(500, "Request failed. Please try again.")

@app.post("/api/numerology")
async def numerology_calculate(req: NumerologyReportReq):
    """Return numerology data as JSON (for frontend use)."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from numerology_engine import (
            life_path, destiny_pythagorean, soul_urge_pythagorean,
            personality_pythagorean, personal_year,
            chaldean_value, chaldean_soul_urge,
            vedic_moolank, vedic_bhagyank, vedic_namank,
            kabbalah_value, lo_shu_grid, name_correction,
            karmic_analysis, planes_of_expression, forecast,
        )
        import datetime
        dob_str = f"{req.year:04d}-{req.month:02d}-{req.day:02d}"
        today   = datetime.date.today()
        return {
            "life_path"     : life_path(dob_str),
            "destiny"       : destiny_pythagorean(req.name),
            "soul_urge"     : soul_urge_pythagorean(req.name),
            "personality"   : personality_pythagorean(req.name),
            "personal_year" : personal_year(dob_str, today.year),
            "chaldean"      : chaldean_value(req.name),
            "chaldean_su"   : chaldean_soul_urge(req.name),
            "vedic_moolank" : vedic_moolank(dob_str),
            "vedic_bhagyank": vedic_bhagyank(dob_str),
            "vedic_namank"  : vedic_namank(req.name),
            "kabbalah"      : kabbalah_value(req.name.split()[0]),
            "lo_shu"        : lo_shu_grid(dob_str),
            "name_correction": name_correction(req.name, dob_str),
            "karmic"        : karmic_analysis(req.name, dob_str),
            "planes"        : planes_of_expression(req.name),
            "forecast"      : forecast(dob_str, today.year, today.month, today.day),
        }
    except Exception as ex:
        return {"error": str(ex)}

# ══════════════════════════════════════════════════════════════
# JYOGI LOGIC — 5-RULE INTERPRETATION ENGINE
# ══════════════════════════════════════════════════════════════
class JyogiLogicReq(BaseModel):
    year:   int
    month:  int
    day:    int
    hour:   float
    lat:    float
    lon:    float
    mode:   str = "general"   # general | career | relationship

@app.post("/api/jyogi-logic")
async def jyogi_logic_endpoint(req: JyogiLogicReq):
    """
    Apply all 5 Jyogi Logic rules to a live chart.
    Returns structured interpretation data + narrative report.
    """
    try:
        from vedic_engine import (
            julian_day, ist_to_ut, get_all_planets,
            get_lagna, lahiri, calc_navamsha
        )
        from jyogi_logic import JyogiLogic

        ut  = ist_to_ut(req.hour)
        jd  = julian_day(req.year, req.month, req.day, ut)
        planets_raw = get_all_planets(jd)
        lagna_lon   = get_lagna(jd, req.lat, req.lon)

        # Compute D9 with lagna for accurate D9 lagna sign
        planet_lons = {k: v for k, v in planets_raw.items() if k != 'jd'}
        d9 = calc_navamsha(planet_lons, lagna_lon=lagna_lon)

        # Apply Jyogi Logic
        logic  = JyogiLogic(planet_lons, lagna_lon, d9)
        result = logic.full_analysis(mode=req.mode)
        report = logic.narrative_report(result)

        return {
            "lagna_lon":       round(lagna_lon, 4),
            "lagna_sign":      result["lagna_sign"],
            "seventh_lord":    result["seventh_lord"],
            "composite_scores": result["composite_scores"],
            "planets_in_7th":  result["planets_in_7th"],
            "rule1_navamsha":  {
                p: {
                    "d1_dignity":     r["d1_dignity"],
                    "d9_dignity":     r["d9_dignity"],
                    "combined_score": r["combined_score"],
                    "final_strength": r["final_strength"],
                    "note":           r["note"],
                } for p, r in result["rule1_navamsha"].items()
            },
            "rule2_yogas":     result["rule2_yogas"],
            "rule3_yoni":      {
                "layers":        result["rule3_yoni"]["layers"],
                "harmonies":     result["rule3_yoni"]["harmonies"],
                "conflicts":     result["rule3_yoni"]["conflicts"],
                "flip_warnings": result["rule3_yoni"]["flip_warnings"],
                "summary":       result["rule3_yoni"]["summary"],
            },
            "rule4_career":    result["rule4_career"],
            "rule5_smoke":     result["rule5_smoke"],
            "narrative_report": report,
        }
    except Exception as ex:
        import traceback
        log.error("Endpoint error: %s", traceback.format_exc())
        raise HTTPException(500, "Request failed. Please try again.")

# ══════════════════════════════════════════════════════════════
# ADMIN TOKEN — Time-based session password for PDF downloads
# ══════════════════════════════════════════════════════════════
import hashlib, time as _time

# ── /api/admin-token REMOVED (rebase 2026-08-14) ──────────────────────
# The endpoint minted the paid-report token for the client. It is replaced by
# the admin SESSION: once logged in, the browser downloads paid reports using
# the session cookie (see /api/report). REPORT_TOKEN_SECRET / expected_report_token
# / X-Report-Token remain in place for the header-token path, so no dev security
# was reverted — only the client-facing token minter was removed.
