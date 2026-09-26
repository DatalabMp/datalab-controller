"""Deterministic daily scheduling for meaningful DataLab work slots."""

from __future__ import annotations

import hashlib
import random
from datetime import date


def daily_work_hours(
    day: date,
    *,
    secret_seed: str,
    minimum: int = 10,
    maximum: int = 15,
) -> tuple[int, ...]:
    """Choose 10–15 distinct hourly slots reproducibly for a given day.

    The schedule is randomized, but stable across repeated workflow invocations on the same day.
    It represents opportunities for meaningful work, not a requirement to manufacture commits.
    """

    if not 1 <= minimum <= maximum <= 24:
        raise ValueError("Expected 1 <= minimum <= maximum <= 24")
    if not secret_seed:
        raise ValueError("A non-empty scheduling seed is required")

    digest = hashlib.sha256(f"{day.isoformat()}:{secret_seed}".encode()).hexdigest()
    rng = random.Random(digest)
    target = rng.randint(minimum, maximum)
    return tuple(sorted(rng.sample(range(24), target)))
