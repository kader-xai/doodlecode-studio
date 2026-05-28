"""Installer guard tests — confirm we reject shell-injection attempts."""
from app.installer import _PKG_RE, _split


def test_split_basic():
    assert _split("numpy pandas") == ["numpy", "pandas"]
    assert _split("numpy,pandas") == ["numpy", "pandas"]
    assert _split("numpy\npandas") == ["numpy", "pandas"]
    assert _split("  ") == []


def test_valid_specs_match():
    for spec in ["numpy", "pandas==2.1", "scikit-learn", "matplotlib>=3.8",
                 "package[extra]", "name~=1.0", "x_y.z"]:
        assert _PKG_RE.match(spec), f"should accept: {spec}"


def test_injection_attempts_rejected():
    # Plain bare words like "rm" pass the regex — that's fine because
    # `pip install rm` just looks for a (non-existent) package called
    # "rm". The real guard is keeping out shell metacharacters.
    for bad in ["&&", "-rf", "/", "$(whoami)", "; ls", "`cmd`",
                "pkg;rm", "pkg||echo", "pkg|cat", "../etc", "pkg`x`"]:
        assert not _PKG_RE.match(bad), f"should reject: {bad}"
