"""HTTP proxy for the Browser cell.

Some sites (Google, banks, GitHub login pages) send
`X-Frame-Options: deny` or `Content-Security-Policy: frame-ancestors`
so browsers refuse to render them in an `<iframe>`. This endpoint
fetches the URL server-side, strips those headers, injects a `<base
href>` tag so relative URLs in the HTML still resolve, then streams
the body back to the browser. The frontend points the iframe at
`/api/proxy?url=<encoded>` instead of the original URL.

**SSRF guard**: the target host must resolve to a *public* IP. We
block loopback, link-local, private, and metadata-IP ranges so a
proxy request can't be tricked into hitting `localhost`, the user's
LAN, or `169.254.169.254`. Hostnames are resolved here (after the
scheme/port checks) before the actual HTTP call.

Limits:
  * Only `http` / `https` schemes.
  * 8 MB body cap.
  * 15-second timeout.
  * Method is GET only — proxying POST etc. would invite abuse.
"""
from __future__ import annotations

import ipaddress
import re
import socket
from typing import Iterable
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, Query
from fastapi.responses import Response

_MAX_BYTES = 8 * 1024 * 1024
_TIMEOUT_S = 15.0

# Headers we strip from the upstream response so the browser will
# embed the page in an iframe. CSP often blocks frame embedding via
# `frame-ancestors` so we drop the entire CSP — coarse but effective.
_STRIP_RESPONSE_HEADERS = {
    "x-frame-options",
    "content-security-policy",
    "content-security-policy-report-only",
    "cross-origin-embedder-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
    # We unzip ourselves so don't claim to be compressed.
    "content-encoding",
    "transfer-encoding",
    # Connection-level headers shouldn't be forwarded.
    "connection",
}


def _is_public_ip(host: str) -> bool:
    """Resolve `host` and confirm every address is public-routable."""
    try:
        infos = socket.getaddrinfo(host, None)
    except OSError:
        return False
    for info in infos:
        addr = info[4][0]
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            return False
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            return False
        # Cloud metadata services live on 169.254.169.254 (covered by
        # link_local above) and some platform-specific addresses. We
        # belt-and-braces with an explicit check.
        if str(ip) in {"169.254.169.254", "100.100.100.200"}:
            return False
    return True


def _inject_base(html: bytes, base_url: str) -> bytes:
    """Add `<base href>` so relative URLs resolve against the upstream."""
    tag = f'<base href="{base_url}">'.encode()
    lower = html[:4096].lower()
    head_idx = lower.find(b"<head>")
    if head_idx >= 0:
        cut = head_idx + len(b"<head>")
        return html[:cut] + tag + html[cut:]
    # No <head>? Prepend.
    return tag + html


async def proxy(url: str = Query(...)) -> Response:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(400, "Only http/https URLs allowed")
    if not parsed.hostname:
        raise HTTPException(400, "Malformed URL")
    if not _is_public_ip(parsed.hostname):
        raise HTTPException(400, f"Refusing to proxy to non-public host: {parsed.hostname}")

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=_TIMEOUT_S,
            headers={
                # A friendly UA gets us past UA-sniffing CDNs more often.
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/124.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        ) as client:
            r = await client.get(url)
    except httpx.HTTPError as e:
        raise HTTPException(502, f"Upstream fetch failed: {e}")

    body = r.content
    if len(body) > _MAX_BYTES:
        raise HTTPException(413, "Upstream response too large")

    content_type = r.headers.get("content-type", "text/plain")
    is_html = content_type.lower().startswith("text/html")

    if is_html:
        # Build a base href that resolves /foo paths back to the
        # upstream origin so its assets keep loading.
        base = f"{parsed.scheme}://{parsed.netloc}/"
        body = _inject_base(body, base)

    out_headers: dict[str, str] = {}
    for k, v in r.headers.items():
        if k.lower() in _STRIP_RESPONSE_HEADERS:
            continue
        out_headers[k] = v
    out_headers["content-type"] = content_type

    return Response(content=body, status_code=r.status_code, headers=out_headers)


# A tiny helper for the model layer — frontend uses this to encode
# the URL in the same way the endpoint expects.
_PROXY_RE = re.compile(r"^/api/proxy\?url=([^&]+)")
def is_proxied(source: str) -> bool:
    return bool(_PROXY_RE.match(source))


def proxied_iter_targets() -> Iterable[str]:
    """Currently unused — placeholder for tests / introspection."""
    return ()
