from decimal import Decimal

import pytest

from datalab.agents import (
    ReleaseGateViolation,
    assert_agent_may_write,
    assert_release_ready,
)


def test_only_executor_may_write() -> None:
    with pytest.raises(ReleaseGateViolation):
        assert_agent_may_write("statistics")
    assert_agent_may_write("executor")


def test_release_requires_all_veto_gates() -> None:
    approvals = {
        "architecture": True,
        "data": True,
        "statistics": True,
        "qa": True,
        "security": True,
        "reviewer": True,
    }
    assert_release_ready(
        approvals,
        meaningful_change=True,
        external_cost_usd=Decimal("0.00"),
    )


def test_release_rejects_non_meaningful_change() -> None:
    approvals = {
        "architecture": True,
        "data": True,
        "statistics": True,
        "qa": True,
        "security": True,
        "reviewer": True,
    }
    with pytest.raises(ReleaseGateViolation):
        assert_release_ready(
            approvals,
            meaningful_change=False,
            external_cost_usd=Decimal("0.00"),
        )
