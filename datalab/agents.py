"""Specialist-agent registry and deterministic release gates."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from datalab.cost_guard import ZERO


@dataclass(frozen=True)
class AgentSpec:
    name: str
    can_write: bool
    can_veto: bool
    responsibility: str


AGENTS: dict[str, AgentSpec] = {
    "requirements": AgentSpec(
        "requirements", False, False, "Define research question, scope and acceptance criteria."
    ),
    "architecture": AgentSpec(
        "architecture", False, True, "Validate boundaries, modules, dependencies and deployment."
    ),
    "data": AgentSpec(
        "data", False, True, "Validate provenance, schema, quality and transformations."
    ),
    "statistics": AgentSpec(
        "statistics", False, True, "Validate methods, assumptions, uncertainty and interpretation."
    ),
    "modeling": AgentSpec(
        "modeling", False, False, "Justify predictive tasks, baselines, metrics and leakage controls."
    ),
    "visualization": AgentSpec(
        "visualization", False, False, "Design truthful, accessible and question-driven dashboards."
    ),
    "qa": AgentSpec("qa", False, True, "Run tests, linting, smoke checks and edge-case validation."),
    "security": AgentSpec(
        "security", False, True, "Enforce repository scope, secret hygiene and command safety."
    ),
    "reviewer": AgentSpec(
        "reviewer", False, True, "Independently cross-check evidence before release."
    ),
    "executor": AgentSpec(
        "executor", True, False, "Apply only approved changes and create meaningful commits."
    ),
}

PIPELINE = tuple(AGENTS)
REQUIRED_APPROVALS = frozenset(
    {"architecture", "data", "statistics", "qa", "security", "reviewer"}
)


class ReleaseGateViolation(RuntimeError):
    """Raised when a proposed write has not passed every required gate."""


def assert_agent_may_write(agent_name: str) -> None:
    agent = AGENTS[agent_name]
    if not agent.can_write:
        raise ReleaseGateViolation(f"Agent {agent_name} is not allowed to write to GitHub.")


def assert_release_ready(
    approvals: dict[str, bool],
    *,
    meaningful_change: bool,
    external_cost_usd: Decimal,
) -> None:
    if not meaningful_change:
        raise ReleaseGateViolation("Artificial/empty changes are never releasable.")
    if external_cost_usd != ZERO:
        raise ReleaseGateViolation("External model/API cost must remain USD 0.00.")

    missing = sorted(role for role in REQUIRED_APPROVALS if approvals.get(role) is not True)
    if missing:
        raise ReleaseGateViolation(f"Missing required approvals: {', '.join(missing)}")
