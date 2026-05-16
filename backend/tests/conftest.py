"""Pytest configuration: add the backend root to sys.path so `import app`
works regardless of where pytest is invoked from."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
