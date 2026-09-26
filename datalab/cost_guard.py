"""Zero-cost enforcement for model/provider selection."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

ZERO = Decimal("0.00")
ALLOWED_MODES = frozenset({"local", "remote_free"})


class CostPolicyViolation(RuntimeError):
    """Raised when a request could create external model/API cost."""


class FreeCapacityExhausted(RuntimeError):
    """Raised when no confirmed zero-cost provider is currently available."""


@dataclass(frozen=True)
class ProviderCandidate:
    name: str
    mode: str
    available: bool
    confirmed_cost_usd: Decimal | None


def assert_zero_cost(*, provider_name: str, mode: str, estimated_cost_usd: Decimal | None) -> None:
    if mode not in ALLOWED_MODES:
        raise CostPolicyViolation(f"Provider mode is not permitted: {mode}")
    if estimated_cost_usd is None:
        raise CostPolicyViolation(
            f"Unknown pricing is rejected for provider {provider_name}; zero cost must be explicit."
        )
    if estimated_cost_usd != ZERO:
        raise CostPolicyViolation(
            f"Provider {provider_name} would cost USD {estimated_cost_usd}; budget is USD 0.00."
        )


def select_zero_cost_provider(candidates: list[ProviderCandidate]) -> ProviderCandidate:
    """Return the first available provider that explicitly reports zero external cost."""

    for candidate in candidates:
        if not candidate.available:
            continue
        try:
            assert_zero_cost(
                provider_name=candidate.name,
                mode=candidate.mode,
                estimated_cost_usd=candidate.confirmed_cost_usd,
            )
        except CostPolicyViolation:
            continue
        return candidate

    raise FreeCapacityExhausted(
        "All confirmed zero-cost providers are unavailable. The controller must pause."
    )
