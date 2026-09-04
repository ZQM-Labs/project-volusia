"""Contribution front-end for Project Volusia (P1-025).

Standalone FastAPI app implementing the WEB_FORM_DESIGN.md URL structure
(/f, /i, /status plus /es/* mirrors) with a server-side submission path
into the contribution API. Coexists with portal_app.py (mountable router)
and runs standalone via ``python portal_contribute.py`` (port 8791).

Integration strategy — contribute logic is never duplicated:
  1. HTTP first: POST/GET against the contribution API
     (VOLUSIA_CONTRIBUTION_API, default http://127.0.0.1:8790) — the
     stable, versioned /api/v1 contract.
  2. In-process fallback: if no API process is reachable, calls go
     through FastAPI's TestClient against contribution_api.app directly.
     Same validation, same SQLite DB, same response shapes.

Collaboration note: contribution_api.py is owned by another writer
(in-flight edits all session). This module only imports it and speaks its
HTTP contract; it never modifies that file.
"""

from __future__ import annotations

import html
import os
import uuid

import requests
from fastapi import APIRouter, FastAPI, Form
from fastapi.responses import HTMLResponse

# ------------------------------------------------------------------ config
API_BASE_URL = os.environ.get(
    "VOLUSIA_CONTRIBUTION_API", ""
).rstrip("/")
STANDALONE_PORT = int(os.environ.get("VOLUSIA_CONTRIBUTE_PORT", "8791"))
HTTP_TIMEOUT = 3.0  # seconds; keep the UI responsive before fallback
CONTENT_MAX = 5000
BASIS_MAX = 2000

# WEB_FORM_DESIGN.md §3/§4: each portal pathway maps to one contribution type.
# The contribution API remains the single source of truth for valid types and
# re-validates every payload; unknown types pass through and get its 400.
PATHWAY_TYPE = {"f": "community", "i": "direct"}

router = APIRouter()
app = FastAPI(title="Project Volusia — Contribute", version="1.0.0")

# ------------------------------------------------------------- page shell
BRAND = "Project Volusia"
NAV_EN = [
    ("/", "Home"),
    ("/contribute", "Contribute"),
    ("/f", "Share knowledge"),
    ("/i", "Share a thought"),
    ("/status", "Check status"),
]
NAV_ES = [
    ("/es", "Inicio"),
    ("/es/contribute", "Contribuya"),
    ("/es/f", "Compartir conocimiento"),
    ("/es/i", "Compartir una idea"),
    ("/es/status", "Consultar estado"),
]


def _esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def _page(title: str, body: str, lang: str = "en") -> str:
    nav = NAV_ES if lang == "es" else NAV_EN
    prefix = "/es" if lang == "es" else ""
    other = f'<a href="{_esc(_alt(prefix))}">EN</a>' if lang == "es" else (
        '<a href="/es">ES</a>'
    )
    items = "".join(
        f'<a href="{_esc(href)}">{_esc(label)}</a>' for href, label in nav
    )
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_esc(title)} — {BRAND}</title>
<style>
 body {{ font-family: system-ui, sans-serif; margin: 0; color: #1a1a1a; }}
 header {{ background: #0b3d59; color: #fff; padding: 1rem 1.5rem; }}
 header a {{ color: #cfe3ee; margin-right: 1rem; text-decoration: none; }}
 header .brand {{ font-weight: 700; color: #fff; margin-right: 1.5rem; }}
 main {{ max-width: 640px; margin: 2rem auto; padding: 0 1rem; }}
 label {{ display: block; margin: 1rem 0 .25rem; font-weight: 600; }}
 textarea, input {{ width: 100%; box-sizing: border-box; padding: .5rem;
   font: inherit; border: 1px solid #999; }}
 button {{ margin-top: 1.25rem; padding: .6rem 1.4rem; font: inherit;
   background: #0b3d59; color: #fff; border: 0; cursor: pointer; }}
 .hint {{ color: #555; font-size: .9rem; }}
 .error {{ border-left: 4px solid #b00020; background: #fdecef;
   padding: .75rem 1rem; margin: 1rem 0; }}
 .ok {{ border-left: 4px solid #1b7f3b; background: #e9f7ee;
   padding: .75rem 1rem; margin: 1rem 0; }}
 code {{ background: #eef2f4; padding: .1rem .3rem; }}
 dl {{ display: grid; grid-template-columns: max-content 1fr; gap: .35rem 1rem; }}
 dt {{ font-weight: 600; }}
</style>
</head>
<body>
<header>
 <span class="brand">{BRAND}</span>{items}<span style="float:right">{other}</span>
</header>
<main>
{body}
</main>
</body>
</html>"""


def _alt(prefix: str) -> str:
    # The EN↔ES toggle lives in _page; this keeps hrefs honest when lang=es.
    return "/"


def _landing(lang: str = "en") -> str:
    if lang == "es":
        title = "Contribuya"
        body = """
<h1>Contribuya a Project Volusia</h1>
<p>Dos formas de aportar:</p>
<dl>
<dt><a href="/es/f">Vía F — Conocimiento comunitario</a></dt>
<dd>Datos locales concretos: aperturas, cierres, precios, condiciones.</dd>
<dt><a href="/es/i">Vía I — Idea o inquietud</a></dt>
<dd>Lo que cree que deberíamos estudiar o reportar.</dd>
</dl>
<p>Después puede seguir su envío en <a href="/es/status">Consultar estado</a>.</p>
<p class="hint">Revisión humana en días hábiles; seguimos el principio de
anonimato primero (el correo es opcional).</p>"""
    else:
        title = "Contribute"
        body = """
<h1>Contribute to Project Volusia</h1>
<p>Two ways to contribute:</p>
<dl>
<dt><a href="/f">Pathway F — Community knowledge</a></dt>
<dd>Concrete local data: openings, closings, prices, conditions.</dd>
<dt><a href="/i">Pathway I — Idea or concern</a></dt>
<dd>What you think we should study or report.</dd>
</dl>
<p>Afterwards, follow your submission at <a href="/status">Check status</a>.</p>
<p class="hint">Human review on business days; anonymous-first
(email optional).</p>"""
    return _page(title, body, lang)


@router.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(_landing("en"))


@router.get("/es", response_class=HTMLResponse)
def home_es() -> HTMLResponse:
    return HTMLResponse(_landing("es"))


# ------------------------------------------------- contribution API client
def _import_capi():
    """Import contribution_api in both package and standalone modes."""
    try:
        from . import contribution_api as capi  # package mode
    except ImportError:  # standalone: script dir is on sys.path
        import contribution_api as capi  # type: ignore
    return capi


capi = _import_capi()


def _safe_json(resp) -> dict:
    try:
        data = resp.json()
    except ValueError:
        data = {}
    return data if isinstance(data, dict) else {}


def _testclient():
    # Lazy: TestClient needs httpx, which is a dev/test dependency —
    # production users hit the HTTP path and never import this.
    from fastapi.testclient import TestClient

    return TestClient(capi.app)


def _api_post(payload: dict) -> tuple[int, dict, str]:
    """Submit via HTTP; fall back to in-process app if unreachable.
    
    Returns (status_code, body, via) where via is "http" or "local".
    """
    # Use relative URL if API_BASE_URL is empty (same-origin)
    url = f"{API_BASE_URL}/api/v1/contributions" if API_BASE_URL else "/api/v1/contributions"
    try:
        resp = requests.post(
            url,
            json=payload,
            timeout=HTTP_TIMEOUT,
        )
        return resp.status_code, _safe_json(resp), "http"
    except requests.RequestException:
        pass
    try:
        resp = _testclient().post("/api/v1/contributions", json=payload)
        return resp.status_code, _safe_json(resp), "local"
    except Exception:
        return 503, {"detail": "Contribution service unreachable."}, "none"


def _api_get(submission_id: str) -> tuple[int, dict, str]:
    """Fetch one submission via HTTP; same fallback contract as _api_post."""
    url = f"{API_BASE_URL}/api/v1/contributions/{submission_id}" if API_BASE_URL else f"/api/v1/contributions/{submission_id}"
    try:
        resp = requests.get(
            url,
            timeout=HTTP_TIMEOUT,
        )
        return resp.status_code, _safe_json(resp), "http"
    except requests.RequestException:
        pass
    try:
        resp = _testclient().get(f"/api/v1/contributions/{submission_id}")
        return resp.status_code, _safe_json(resp), "local"
    except Exception:
        return 503, {"detail": "Contribution service unreachable."}, "none"


# ---------------------------------------------------------------- forms
def _form_page(pathway: str, lang: str = "en", error: str = "",
               ok_ref: str = "") -> str:
    """Render Pathway F/I form. pathway: 'f' or 'i'."""
    f = pathway.lower()
    pfx = "/es" if lang == "es" else ""
    is_f = f == "f"
    if is_f:
        title = "Compartir conocimiento" if lang == "es" else "Share knowledge"
    else:
        title = "Compartir una idea" if lang == "es" else "Share a thought"

    labels = {
        "en": {
            "f_content": "What changed, where, and when?",
            "f_content_hint": "Be concrete: business, city, date, price, condition.",
            "f_basis": "How do you know? (basis)",
            "f_basis_hint": "First-hand visit, photo, posting, word of mouth…",
            "i_content": "What should we study or report?",
            "submit": "Submit",
            "contact": "Email (optional — for follow-up only)",
            "name": "Display name (optional)",
        },
        "es": {
            "f_content": "¿Qué cambió, dónde y cuándo?",
            "f_content_hint": "Sea concreto: negocio, ciudad, fecha, precio, estado.",
            "f_basis": "¿Cómo lo sabe? (fundamento)",
            "f_basis_hint": "Visita directa, foto, publicación, boca a boca…",
            "i_content": "¿Qué deberíamos estudiar o reportar?",
            "submit": "Enviar",
            "contact": "Correo (opcional — solo para seguimiento)",
            "name": "Nombre visible (opcional)",
        },
    }["es" if lang == "es" else "en"]

    content_label = labels["f_content"] if is_f else labels["i_content"]
    err_html = f'<div class="error">{_esc(error)}</div>' if error else ""
    ok_html = (
        f'<div class="ok">Reference code: <code>{_esc(ok_ref)}</code> — '
        f'<a href="{pfx}/status?id={_esc(ok_ref)}">'
        + ("Check its status" if lang != "es" else "Consultar estado")
        + "</a></div>"
        if ok_ref else ""
    )
    basis_html = (
        f'<label for="basis">{_esc(labels["f_basis"])}</label>\n'
        f'<textarea id="basis" name="basis" rows="3" maxlength="{BASIS_MAX}"></textarea>\n'
        f'<p class="hint">{_esc(labels["f_basis_hint"])}</p>'
        if is_f else ""
    )
    idem = uuid.uuid4().hex
    return _page(title, f"""
{err_html}{ok_html}
<form method="post" action="{pfx}/{f}">
<input type="hidden" name="idempotency_key" value="{idem}">
<input type="hidden" name="pathway" value="{f}">
<label for="content">{_esc(content_label)}</label>
<textarea id="content" name="content" rows="6" required
 maxlength="{CONTENT_MAX}"></textarea>
<p class="hint">{_esc(labels["f_content_hint"] if is_f else labels["i_content"])}</p>
{basis_html}
<label for="author_name">{_esc(labels["name"])}</label>
<input id="author_name" name="author_name" maxlength="80" autocomplete="off">
<label for="author_email">{_esc(labels["contact"])}</label>
<input id="author_email" name="author_email" type="email" maxlength="200"
 autocomplete="off">
<button type="submit">{_esc(labels["submit"])}</button>
</form>
""", lang)


def _handle_form(pathway: str, lang: str, content: str, basis: str,
                 author_name: str, author_email: str,
                 idempotency_key: str) -> str:
    """Validate, submit to the contribution API, return HTML result.

    The contribution API has no ``basis`` field (writer's contract), so
    basis is folded into content as a trailing block when present.
    """
    f = pathway.lower()
    pfx = "/es" if lang == "es" else ""
    content = (content or "").strip()
    if not content:
        return _form_page(f, lang,
                          error="Content is required." if lang != "es"
                                else "El contenido es obligatorio.")
    if len(content) > CONTENT_MAX:
        return _form_page(f, lang,
                          error="Content is too long." if lang != "es"
                                else "El contenido es demasiado largo.")
    basis = (basis or "").strip()
    if basis:
        block = f"{content}\n\nBasis: {basis}" if lang != "es" \
            else f"{content}\n\nFundamento: {basis}"
    else:
        block = content
    payload = {
        "contribution_type": PATHWAY_TYPE[f],
        "content": block,
        "author_name": (author_name or "").strip(),
        "author_email": (author_email or "").strip(),
        "idempotency_key": (idempotency_key or "").strip() or uuid.uuid4().hex,
    }
    code, body, _via = _api_post(payload)
    if code == 201:
        ref = body.get("submission_id", "")
        return _form_page(f, lang, ok_ref=ref)
    if code == 200:
        # Idempotent retry — already submitted.
        ref = body.get("submission_id", "")
        return _form_page(f, lang, ok_ref=ref)
    # 400 / 401 / 503
    detail = body.get("detail", "Submission failed.")
    return _form_page(f, lang, error=detail)


@router.get("/f", response_class=HTMLResponse)
def form_f() -> HTMLResponse:
    return HTMLResponse(_form_page("f", "en"))


@router.post("/f", response_class=HTMLResponse)
def form_f_post(
    content: str = Form(""),
    basis: str = Form(""),
    author_name: str = Form(""),
    author_email: str = Form(""),
    idempotency_key: str = Form(""),
) -> HTMLResponse:
    return HTMLResponse(_handle_form("f", "en", content, basis, author_name,
                                     author_email, idempotency_key))


@router.get("/es/f", response_class=HTMLResponse)
def form_f_es() -> HTMLResponse:
    return HTMLResponse(_form_page("f", "es"))


@router.post("/es/f", response_class=HTMLResponse)
def form_f_es_post(
    content: str = Form(""),
    basis: str = Form(""),
    author_name: str = Form(""),
    author_email: str = Form(""),
    idempotency_key: str = Form(""),
) -> HTMLResponse:
    return HTMLResponse(_handle_form("f", "es", content, basis, author_name,
                                     author_email, idempotency_key))


@router.get("/i", response_class=HTMLResponse)
def form_i() -> HTMLResponse:
    return HTMLResponse(_form_page("i", "en"))


@router.post("/i", response_class=HTMLResponse)
def form_i_post(
    content: str = Form(""),
    author_name: str = Form(""),
    author_email: str = Form(""),
    idempotency_key: str = Form(""),
) -> HTMLResponse:
    return HTMLResponse(_handle_form("i", "en", content, "", author_name,
                                     author_email, idempotency_key))


@router.get("/es/i", response_class=HTMLResponse)
def form_i_es() -> HTMLResponse:
    return HTMLResponse(_form_page("i", "es"))


@router.post("/es/i", response_class=HTMLResponse)
def form_i_es_post(
    content: str = Form(""),
    author_name: str = Form(""),
    author_email: str = Form(""),
    idempotency_key: str = Form(""),
) -> HTMLResponse:
    return HTMLResponse(_handle_form("i", "es", content, "", author_name,
                                     author_email, idempotency_key))


# ------------------------------------------------------------------ status
def _status_page(submission_id: str, body: dict, lang: str) -> str:
    """Render the status/lookup page with an optional result block."""
    pfx = "/es" if lang == "es" else ""
    result = ""
    if body:
        status = body.get("status", "unknown")
        ack = body.get("acknowledged_at", "")
        eta = body.get("estimated_review_by", "")
        ref = body.get("submission_id", submission_id)
        result = (
            f'<div class="ok">Reference: <code>{_esc(ref)}</code><br>'
            f'Status: <strong>{_esc(status)}</strong><br>'
            f'Acknowledged: {_esc(ack)}<br>'
            f'Review by: {_esc(eta)}</div>'
        )
    title = "Check submission status" if lang != "es" else "Consultar estado"
    return _page(title, f"""
{result}
<form method="get" action="{pfx}/status">
<label for="id">Submission ID</label>
<input id="id" name="id" maxlength="64" autocomplete="off"
 value="{_esc(submission_id)}" required>
<button type="submit">{"Check" if lang != "es" else "Consultar"}</button>
</form>
""", lang)


@router.get("/status", response_class=HTMLResponse)
def status(req: Request) -> HTMLResponse:
    sid = req.query_params.get("id", "").strip()
    if sid:
        code, body, _via = _api_get(sid)
        if code == 200:
            return HTMLResponse(_status_page(sid, body, "en"))
    return HTMLResponse(_status_page(sid, {}, "en"))


@router.get("/es/status", response_class=HTMLResponse)
def status_es(req: Request) -> HTMLResponse:
    sid = req.query_params.get("id", "").strip()
    if sid:
        code, body, _via = _api_get(sid)
        if code == 200:
            return HTMLResponse(_status_page(sid, body, "es"))
    return HTMLResponse(_status_page(sid, {}, "es"))


# --------------------------------------------------------------- runner
def main():
    """Run the contribute portal (python -m ...portal_contribute)."""
    import uvicorn
    port = int(os.environ.get("CONTRIBUTE_PORT", "8791"))
    uvicorn.run("volusia_data.portal_contribute:app", host="127.0.0.1",
                port=port, reload=False)


if __name__ == "__main__":
    main()
