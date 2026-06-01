"""SSRF-guard tests for the /api/proxy endpoint (iter 215).

`_is_public_ip` is the security boundary: the browser-cell proxy must
refuse to fetch from any host that resolves to a loopback / private /
link-local / metadata address, or the server could be turned into an
SSRF pivot into the user's LAN or a cloud metadata service. IP literals
don't hit DNS via getaddrinfo, so these assertions are deterministic.
"""
from app.proxy import _is_public_ip, is_proxied


def test_rejects_loopback():
    assert _is_public_ip("127.0.0.1") is False
    assert _is_public_ip("::1") is False


def test_rejects_private_ranges():
    for ip in ("10.0.0.1", "192.168.1.1", "172.16.0.1"):
        assert _is_public_ip(ip) is False, ip


def test_rejects_link_local_and_cloud_metadata():
    # 169.254.169.254 (AWS/GCP/Azure) and 100.100.100.200 (Alibaba).
    assert _is_public_ip("169.254.169.254") is False
    assert _is_public_ip("100.100.100.200") is False
    assert _is_public_ip("169.254.1.1") is False  # link-local generally


def test_rejects_unspecified_and_multicast():
    assert _is_public_ip("0.0.0.0") is False
    assert _is_public_ip("224.0.0.1") is False


def test_rejects_unresolvable_host():
    # A name that can't resolve → getaddrinfo raises → guard returns False
    # (fail closed). `.invalid` is reserved to never resolve (RFC 2606).
    assert _is_public_ip("nonexistent-host.invalid") is False


def test_allows_a_public_ip():
    assert _is_public_ip("8.8.8.8") is True
    assert _is_public_ip("1.1.1.1") is True


def test_is_proxied_matches_only_the_proxy_path():
    assert is_proxied("/api/proxy?url=https%3A%2F%2Fexample.com") is True
    assert is_proxied("https://example.com") is False
    assert is_proxied("") is False
