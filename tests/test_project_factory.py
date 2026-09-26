from datetime import UTC, datetime, timedelta

from datalab.project_factory import (
    ProjectSpec,
    interval_elapsed,
    repository_payload,
    scaffold_files,
    select_next_queued,
)


def _project(slug: str, priority: int, status: str = "queued") -> ProjectSpec:
    return ProjectSpec(
        slug=slug,
        title=slug.replace("-", " ").title(),
        source="Example Source",
        status=status,
        priority=priority,
        dashboard="github-pages",
    )


def test_select_next_queued_uses_priority() -> None:
    projects = [_project("later", 9), _project("next", 1), _project("active", 0, "active")]
    selected = select_next_queued(projects)
    assert selected is not None
    assert selected.slug == "next"


def test_interval_allows_first_project() -> None:
    assert interval_elapsed(None, interval_days=3)


def test_interval_requires_full_72_hours() -> None:
    now = datetime(2026, 9, 26, 12, tzinfo=UTC)
    too_soon = (now - timedelta(hours=71, minutes=59)).isoformat()
    ready = (now - timedelta(hours=72)).isoformat()
    assert not interval_elapsed(too_soon, interval_days=3, now=now)
    assert interval_elapsed(ready, interval_days=3, now=now)


def test_repository_payload_is_public_and_scoped() -> None:
    payload = repository_payload(_project("brazil-road-safety", 1))
    assert payload["name"] == "brazil-road-safety"
    assert payload["private"] is False
    assert payload["auto_init"] is True


def test_scaffold_contains_management_and_quality_files() -> None:
    project = _project("brazil-road-safety", 1)
    files = scaffold_files(project, "2026-09-26T12:00:00+00:00")
    assert ".datalab/manifest.json" in files
    assert '"managed": true' in files[".datalab/manifest.json"]
    assert ".github/workflows/ci.yml" in files
    assert ".github/workflows/pages.yml" in files
    assert "tests/test_smoke.py" in files
    assert "docs/index.html" in files
