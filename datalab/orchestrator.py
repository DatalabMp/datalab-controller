"""Gera o snapshot público e sem segredos da Central de Operações do DataLab."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from datalab.state import load_runtime

ROOT = Path(__file__).resolve().parents[1]
AGENT_RUNTIME_ALIASES = {"data": "data_engineering"}

STATUS_LABELS = {
    "active": "ativo",
    "initialized": "inicializado",
    "queued": "na fila",
    "passed": "aprovado",
    "blocked": "bloqueado",
    "failed": "falhou",
    "failure": "falha",
    "idle": "ocioso",
    "running": "em execução",
    "reviewing": "em revisão",
    "testing": "em testes",
    "waiting": "aguardando",
    "not_applicable": "não aplicável",
    "created": "criado",
    "dry_run": "simulação",
}

PROVIDER_MODE_LABELS = {
    "disabled": "desativado",
    "local": "local",
    "remote_free": "remoto gratuito",
}


def _load_yaml(relative_path: str) -> dict:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _numeric(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _integer(value: Any, default: int = 0) -> int:
    return int(_numeric(value, float(default)))


def _runtime_agent(runtime_agents: dict, name: str) -> dict:
    direct = runtime_agents.get(name)
    if isinstance(direct, dict):
        return direct
    alias = AGENT_RUNTIME_ALIASES.get(name)
    aliased = runtime_agents.get(alias) if alias else None
    return aliased if isinstance(aliased, dict) else {}


def _provider_snapshot(providers: list[dict]) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    totals = {
        "requests": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cached_tokens": 0,
        "total_tokens": 0,
        "cost_usd": 0.0,
    }

    for raw in providers:
        if not isinstance(raw, dict):
            continue
        input_tokens = _integer(raw.get("input_tokens"))
        output_tokens = _integer(raw.get("output_tokens"))
        cached_tokens = _integer(raw.get("cached_tokens"))
        total_tokens = _integer(
            raw.get("total_tokens"), input_tokens + output_tokens + cached_tokens
        )
        requests = _integer(raw.get("requests", raw.get("request_count", 0)))
        cost_usd = _numeric(raw.get("cost_usd"))
        quota_limit = raw.get("quota_limit")
        quota_used = raw.get("quota_used")
        quota_remaining = raw.get("quota_remaining")

        row = {
            "name": str(raw.get("name", raw.get("provider", "desconhecido"))),
            "mode": str(raw.get("mode", "unknown")),
            "status": str(raw.get("status", "unknown")),
            "requests": requests,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost_usd,
            "quota_limit": quota_limit,
            "quota_used": quota_used,
            "quota_remaining": quota_remaining,
        }
        rows.append(row)
        totals["requests"] += requests
        totals["input_tokens"] += input_tokens
        totals["output_tokens"] += output_tokens
        totals["cached_tokens"] += cached_tokens
        totals["total_tokens"] += total_tokens
        totals["cost_usd"] += cost_usd

    return rows, totals


def _next_project_eligible(last_started_at: str | None, interval_days: int) -> str | None:
    if not last_started_at:
        return None
    try:
        parsed = datetime.fromisoformat(last_started_at)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return (parsed + timedelta(days=interval_days)).isoformat()


def build_status_snapshot() -> dict:
    settings = _load_yaml("config/settings.yaml")
    project_config = _load_yaml("config/projects.yaml").get("projects", [])
    agent_config = _load_yaml("config/agents.yaml")
    agent_specs = agent_config.get("agents", {})
    pipeline_order = agent_config.get("pipeline", list(agent_specs))
    runtime = load_runtime()

    runtime_agents = runtime.get("agents", {})
    progress = runtime.get("project_progress", {})
    providers, provider_totals = _provider_snapshot(runtime.get("providers", []))

    projects = []
    for project in project_config:
        live = progress.get(project["slug"], {})
        status = str(live.get("status", project["status"]))
        projects.append(
            {
                "slug": project["slug"],
                "title": project["title"],
                "source": project.get("source", "desconhecida"),
                "dashboard": project.get("dashboard", "desconhecido"),
                "status": status,
                "status_label": STATUS_LABELS.get(status, status),
                "priority": int(project["priority"]),
                "progress": int(live.get("progress_percent", live.get("progress", 0))),
                "blocker": live.get("blocker"),
                "repository_url": f"https://github.com/{settings['organization']}/{project['slug']}",
            }
        )

    agents = {}
    pipeline = []
    for index, name in enumerate(pipeline_order, start=1):
        spec = agent_specs[name]
        live = _runtime_agent(runtime_agents, name)
        state = str(live.get("status", live.get("state", "idle")))
        row = {
            "order": index,
            "name": name,
            "display_name": str(spec.get("display_name", name)),
            "state": state,
            "state_label": STATUS_LABELS.get(state, state),
            "detail": str(live.get("detail", "Nenhuma atividade registrada ainda.")),
            "responsibility": str(spec.get("responsibility", "")),
            "can_write": bool(spec.get("can_write", False)),
            "veto": bool(spec.get("veto", False)),
        }
        agents[name] = row
        pipeline.append(row)

    external_cost = _numeric(runtime.get("external_ai_cost_usd")) + provider_totals["cost_usd"]
    max_cost = _numeric(settings["execution"].get("external_ai_max_cost_usd"))
    reporting_status = "tracked" if providers else "unavailable"
    reporting_status_label = "monitorado" if providers else "indisponível"
    token_note = (
        "Solicitações e tokens são contabilizados somente quando o provedor configurado "
        "reporta telemetria. O consumo interno de tokens do produto ChatGPT não é exposto "
        "ao controlador e nunca é estimado."
    )

    interval_days = int(settings["execution"]["new_project_interval_days"])
    last_project_started_at = runtime.get("last_project_started_at")
    provider_mode = str(settings["provider_policy"]["default_mode"])

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "language": settings.get("localization", {}).get("language", "pt-BR"),
        "organization": settings["organization"],
        "controller_repository": settings["controller_repository"],
        "controller_url": (
            f"https://github.com/{settings['organization']}/{settings['controller_repository']}"
        ),
        "active_project": runtime.get("active_project"),
        "last_project_started_at": last_project_started_at,
        "next_project_eligible_at": _next_project_eligible(last_project_started_at, interval_days),
        "metrics": {
            "tasks_today": int(runtime.get("tasks_today", 0)),
            "commits_today": int(runtime.get("commits_today", 0)),
            "failures_today": int(runtime.get("failures_today", 0)),
            "active_projects": sum(
                1 for project in projects if project["status"] in {"active", "initialized"}
            ),
            "passed_agents": sum(1 for agent in pipeline if agent["state"] == "passed"),
        },
        "telemetry": {
            "provider_mode": provider_mode,
            "provider_mode_label": PROVIDER_MODE_LABELS.get(provider_mode, provider_mode),
            "reporting_status": reporting_status,
            "reporting_status_label": reporting_status_label,
            "requests": provider_totals["requests"],
            "input_tokens": provider_totals["input_tokens"],
            "output_tokens": provider_totals["output_tokens"],
            "cached_tokens": provider_totals["cached_tokens"],
            "total_tokens": provider_totals["total_tokens"],
            "confirmed_external_cost_usd": external_cost,
            "max_external_cost_usd": max_cost,
            "note": token_note,
        },
        "daily_plan": runtime.get("daily_plan", {}),
        "operator_control": runtime.get(
            "operator_control",
            {"mode": "normal", "directive": None, "issue_number": None, "updated_at": None},
        ),
        "projects": projects,
        "agents": agents,
        "pipeline": pipeline,
        "providers": providers,
        "quality_gates": settings.get("quality_gates", {}),
        "recent_events": runtime.get("recent_events", []),
        "policy": {
            "allowed_owner": settings["repository_policy"]["allowed_owner"],
            "public_projects_only": bool(settings["repository_policy"]["public_projects_only"]),
            "required_manifest": settings["repository_policy"]["required_manifest"],
            "forbidden_operations": settings["repository_policy"].get("forbidden_operations", []),
            "paid_models_allowed": bool(settings["execution"]["allow_paid_models"]),
            "paid_fallback_allowed": bool(settings["execution"]["allow_paid_fallback"]),
            "require_meaningful_changes": bool(
                settings["execution"]["require_meaningful_changes"]
            ),
            "commit_messages_language": settings.get("localization", {}).get(
                "commit_messages_language", "pt-BR"
            ),
            "new_project_interval_days": interval_days,
            "daily_task_target_min": int(settings["execution"]["daily_task_target_min"]),
            "daily_task_target_max": int(settings["execution"]["daily_task_target_max"]),
        },
    }


def main() -> None:
    print(json.dumps(build_status_snapshot(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
