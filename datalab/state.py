"""Runtime state helpers for the DataLab controller."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_PATH = ROOT / "state" / "runtime.json"


def load_runtime(path: Path = DEFAULT_STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_runtime(state: dict[str, Any], path: Path = DEFAULT_STATE_PATH) -> None:
    """Persist runtime state atomically on a local checkout."""

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def append_event(state: dict[str, Any], event: dict[str, Any], *, limit: int = 50) -> None:
    events = list(state.get("recent_events", []))
    events.append(event)
    state["recent_events"] = events[-limit:]
