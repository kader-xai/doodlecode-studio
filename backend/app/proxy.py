"""Optional iframe-bypass proxy.

When a public site sends `X-Frame-Options: DENY` or a
`Content-Security-Policy: frame-ancestors 'none'`, the browser refuses
to render it inside our Browser cell. That's the browser doing its job
— there's no client-side bypass. The hack:

  1. The Browser cell asks our backend to fetch the URL.
  2. We re-emit the response with those framing headers stripped.
  3. We inject a `<base href>` into the HTML so the page's own
     relative URLs still resolve back to its original origin.

LIMITS (be honest with the user):
  - Cookies / login state from the user's regular browser DO NOT
    carry over. Each request is a fresh, unauthenticated GET.
  - JS that does its own fetch() to its origin will hit the user's
    *real* origin if `<base>` resolves; CORS may still block it.
  - Anti-bot / Cloudflare-protected sites will see our server's IP
    and likely show a challenge or 403.
  - Works well for: static docs, marketing pages, blog posts.
  - Works poorly for: SaaS apps, search engines, anything with
    sensitive auth.

SSRF GUARD:
  - Block file://, data:, gopher://, etc.
  - Resolve hostname → reject private / loopback / link-local IPs.
"""
from __future__ import annotations

import html
import ipaddress
import re
import socket
from urllib.parse import urlparse
from urllib.request import Request as URLRequest
from urllib.request import urlopen

from fastapi import HTTPException
from fastapi.responses import Response

# Drop these from the upstream response — they break iframing.
_BLOCKED_RESPONSE_HEADERS = {
    "x-frame-options",
    "content-security-policy",
    "content-security-policy-report-only",
    "strict-transport-security",
    "cross-origin-opener-policy",
    "cross-origin-embedder-policy",
    "cross-origin-resource-policy",
}

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)
_MAX_BYTES = 8 * 1024 * 1024     # 8 MB cap
_TIMEOUT_SEC = 15


def _is_private_address(host: str) -> bool:
    """True if a hostname resolves to a loopback / private / link-local IP."""
    if not host:
        return True
    if host.lower() in {"localhost"}:
        return True
    try:
        for fam, _typ, _proto, _canon, sa in socket.getaddrinfo(host, None):
            ip_str = sa[0]
            ip = ipaddress.ip_address(ip_str)
            if (ip.is_private or ip.is_loopback or ip.is_link_local
                    or ip.is_multicast or ip.is_reserved or ip.is_unspecified):
                return True
    except socket.gaierror:
        return True
    return False


def _inject_base(html_text: str, original_url: str) -> str:
    """Insert a <base href=...> so the page's relative URLs resolve back
    to its real origin even though it's being served from us."""
    base = f'<base href="{html.escape(original_url, quote=True)}">'
    # Insert right after the first <head>, otherwise prepend.
    m = re.search(r"<head[^>]*>", html_text, flags=re.IGNORECASE)
    if m:
        idx = m.end()
        return html_text[:idx] + "\n" + base + html_text[idx:]
    return base + html_text


def fetch_proxied(url: str) -> Response:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(status_code=400, detail="Only http(s) URLs are supported.")
    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="Missing hostname.")
    if _is_private_address(parsed.hostname):
        raise HTTPException(
            status_code=400,
            detail="Refusing to proxy private / loopback addresses (SSRF guard).",
        )

    req = URLRequest(
        url,
        headers={
            "User-Agent": _UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urlopen(req, timeout=_TIMEOUT_SEC) as upstream:
            body = upstream.read(_MAX_BYTES + 1)
            if len(body) > _MAX_BYTES:
                raise HTTPException(status_code=502, detail=f"Upstream payload > {_MAX_BYTES} bytes.")
            content_type = upstream.headers.get("Content-Type", "text/html; charset=utf-8")
            upstream_headers = {k.lower(): v for k, v in upstream.headers.items()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream fetch failed: {e}") from e

    # If the response is HTML, inject <base href> so resources resolve.
    if "text/html" in content_type:
        try:
            text = body.decode("utf-8", errors="replace")
        except Exception:
            text = body.decode(errors="replace")
        text = _inject_base(text, url)
        body_bytes = text.encode("utf-8")
        content_type = "text/html; charset=utf-8"
    else:
        body_bytes = body

    # Build response headers: keep cache hints, strip framing headers.
    out_headers: dict[str, str] = {}
    for k, v in upstream_headers.items():
        if k in _BLOCKED_RESPONSE_HEADERS:
            continue
        if k in {"content-length", "transfer-encoding", "connection", "set-cookie"}:
            continue
        out_headers[k] = v

    return Response(content=body_bytes, media_type=content_type, headers=out_headers)
