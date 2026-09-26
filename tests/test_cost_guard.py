from decimal import Decimal

import pytest

from datalab.cost_guard import (
    CostPolicyViolation,
    FreeCapacityExhausted,
    ProviderCandidate,
    assert_zero_cost,
    select_zero_cost_provider,
)


def test_rejects_paid_provider() -> None:
    with pytest.raises(CostPolicyViolation):
        assert_zero_cost(
            provider_name="paid",
            mode="remote_free",
            estimated_cost_usd=Decimal("0.01"),
        )


def test_rejects_unknown_pricing() -> None:
    with pytest.raises(CostPolicyViolation):
        assert_zero_cost(
            provider_name="unknown",
            mode="remote_free",
            estimated_cost_usd=None,
        )


def test_selects_only_confirmed_zero_cost_provider() -> None:
    selected = select_zero_cost_provider(
        [
            ProviderCandidate("offline", "local", False, Decimal("0.00")),
            ProviderCandidate("free", "remote_free", True, Decimal("0.00")),
        ]
    )
    assert selected.name == "free"


def test_pauses_when_no_free_capacity_exists() -> None:
    with pytest.raises(FreeCapacityExhausted):
        select_zero_cost_provider([])
