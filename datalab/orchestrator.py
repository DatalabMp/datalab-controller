"""Controller entry point. Initial version is intentionally read-only."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def build_status_snapshot() -> dict:
    settings = _load_yaml("config/settings.yaml")
    projects = _load_yaml("config/projects.yaml").get("projects", [])
    agents = _load_yaml("config/agents.yaml").get("agents", {})

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "organization": settings["organization"],
        "controller_repository": settings["controller_repository"],
        "external_ai_cost_usd": 0.0,
        "provider_mode": settings["provider_policy"]["default_mode"],
        "projects": [
            {
                "slug": project["slug"],
                "title": project["title"],
                "status": project["status"],
                "priority": project["priority"],
            }
            for project in projects
        ],
        "agents": {
            name: {
                "state": "idle",
                "can_write": bool(spec["can_write"]),
                "veto": bool(spec["veto"]),
            }
            for name, spec in agents.items()
        },
        "safety": {
            "allowed_owner": settings["repository_policy"]["allowed_owner"],
            "paid_models_allowed": settings["execution"]["allow_paid_models"],
            "paid_fallback_allowed": settings["execution"]["allow_paid_fallback"],
        },
    }


def main() -> None:
    print(json.dumps(build_status_snapshot(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
