"""HTTP integration tests for the non-kernel endpoints.
/execute and /install are excluded — they hit the real kernel / pip and
belong in a slower integration suite."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app import __version__ as APP_VERSION
from app.main import app
from app.models import FILE_FORMAT_VERSION

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_version_matches_constants():
    r = client.get("/api/version")
    assert r.status_code == 200
    assert r.json() == {"app": APP_VERSION, "format_version": FILE_FORMAT_VERSION}


def test_upload_py_with_callouts():
    src = (
        b'# %% kind=function color=mint title="Demo"\n'
        b"# @explain: do the thing\n"
        b"def f(): pass\n"
    )
    r = client.post("/api/upload", files={"file": ("demo.py", src, "text/x-python")})
    assert r.status_code == 200
    nb = r.json()
    assert nb["cells"][0]["meta"]["color"] == "mint"
    assert nb["cells"][0]["meta"]["title"] == "Demo"


def test_upload_ipynb():
    raw = b'{"cells":[{"cell_type":"markdown","source":"# H\\n"},'\
          b'{"cell_type":"code","source":"x=1\\n"}]}'
    r = client.post("/api/upload", files={"file": ("x.ipynb", raw, "application/json")})
    assert r.status_code == 200
    nb = r.json()
    assert len(nb["cells"]) == 2


def test_upload_bad_ipynb_returns_400():
    r = client.post("/api/upload", files={"file": ("x.ipynb", b"not json", "application/json")})
    assert r.status_code == 400


def test_export_round_trips_via_http():
    src = (
        b'# %% kind=function color=mint title="x"\n'
        b"# @explain: body\n"
        b"def f(): pass\n"
    )
    nb = client.post("/api/upload", files={"file": ("x.py", src, "text/x-python")}).json()
    exported = client.post("/api/export", json=nb).text
    assert exported.startswith("# doodlecode format-version:")
    again = client.post("/api/upload", files={"file": ("x.py", exported.encode(), "text/x-python")}).json()
    assert again["cells"][0]["meta"]["title"] == "x"
    assert again["cells"][0]["meta"]["color"] == "mint"


def test_explain_user_authored_only():
    """No meta → no explanations (CLAUDE.md rule 1)."""
    r = client.post("/api/explain", json={"code": "x = 1", "meta": None})
    assert r.status_code == 200
    assert r.json()["explanations"] == []


def test_explain_returns_callout_from_meta():
    r = client.post("/api/explain", json={
        "code": "x = 1",
        "meta": {"title": "Set x", "explain": "Body.", "color": "peach"},
    })
    body = r.json()
    assert body["explanations"][0]["title"] == "Set x"
    assert body["explanations"][0]["color"] == "peach"


def test_install_rejects_shell_metacharacters():
    r = client.post("/api/install", json={"packages": "pkg; rm -rf /"})
    assert r.status_code == 400


def test_autosave_writes_file(tmp_path, monkeypatch):
    # Redirect WORKSPACE to a tmp dir so the test doesn't touch ~/.doodlecode
    from app import main as m
    monkeypatch.setattr(m, "WORKSPACE", tmp_path)
    nb = {
        "name": "unit-test.py",
        "cells": [{"id": "1", "kind": "code", "source": "x = 1\n", "meta": None}],
    }
    r = client.post("/api/autosave", json=nb)
    assert r.status_code == 200
    written = tmp_path / "unit-test.py"
    assert written.exists()
    assert "x = 1" in written.read_text()
