"""Controller entry point. Initial version remains write-safe and observable."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

from datalab.state import load_runtime

ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def build_status_snapshot() -> dict:
    settings = _load_yaml("config/settings.yaml")
    projects = _load_yaml("config/projects.yaml").get("projects", [])
    agents = _load_yaml("config/agents.yaml").get("agents", {})
    runtime = load_runtime()

    runtime_agents = runtime.get("agents", {})
    progress = runtime.get("project_progress", {})

    project_rows = []
    for project in projects:
        live = progress.get(project["slug"], {})
        project_rows.append(
            {
                "slug": project["slug"],
                "title": project["title"],
                "status": live.get("status", project["status"]),
                "priority": project["priority"],
                "progress": int(live.get("progress", 0)),
            }
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "organization": settings["organization"],
        "controller_repository": settings["controller_repository"],
        "external_ai_cost_usd": 0.0,
        "provider_mode": settings["provider_policy"]["default_mode"],
        "metrics": {
            "tasks_today": int(runtime.get("tasks_today", 0)),
            "commits_today": int(runtime.get("commits_today", 0)),
            "failures_today": int(runtime.get("failures_today", 0)),
        },
        "daily_plan": runtime.get("daily_plan", {}),
        "active_project": runtime.get("active_project"),
        "last_project_started_at": runtime.get("last_project_started_at"),
        "projects": project_rows,
        "agents": {
            name: {
                "state": runtime_agents.get(name, {}).get("state", "idle"),
                "can_write": bool(spec["can_write"]),
                "veto": bool(spec["veto"]),
            }
            for name, spec in agents.items()
        },
        "providers": runtime.get("providers", []),
        "recent_events": runtime.get("recent_events", []),
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
