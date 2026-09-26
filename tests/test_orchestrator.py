from datalab.orchestrator import build_status_snapshot


def test_snapshot_reflects_runtime_agent_and_progress_schema() -> None:
    snapshot = build_status_snapshot()

    assert snapshot["organization"] == "DatalabMp"
    assert snapshot["active_project"] == "brazil-road-safety"

    road_safety = next(
        project for project in snapshot["projects"] if project["slug"] == "brazil-road-safety"
    )
    assert road_safety["progress"] == 5
    assert road_safety["status"] == "initialized"

    assert snapshot["agents"]["data"]["state"] == "passed"
    assert snapshot["agents"]["executor"]["state"] == "passed"
    assert snapshot["agents"]["executor"]["can_write"] is True
    assert snapshot["agents"]["statistics"]["veto"] is True


def test_snapshot_never_invents_provider_token_usage() -> None:
    snapshot = build_status_snapshot()
    telemetry = snapshot["telemetry"]

    assert telemetry["confirmed_external_cost_usd"] == 0.0
    assert telemetry["max_external_cost_usd"] == 0.0
    assert telemetry["total_tokens"] == 0
    assert telemetry["reporting_status"] == "unavailable"
    assert "não é exposto" in telemetry["note"]
