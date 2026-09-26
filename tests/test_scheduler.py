from datetime import date

from datalab.scheduler import daily_work_hours


def test_daily_schedule_is_stable_and_within_target() -> None:
    first = daily_work_hours(date(2026, 9, 26), secret_seed="test-seed")
    second = daily_work_hours(date(2026, 9, 26), secret_seed="test-seed")

    assert first == second
    assert 10 <= len(first) <= 15
    assert tuple(sorted(set(first))) == first
    assert all(0 <= hour <= 23 for hour in first)


def test_different_day_changes_schedule() -> None:
    first = daily_work_hours(date(2026, 9, 26), secret_seed="test-seed")
    second = daily_work_hours(date(2026, 9, 27), secret_seed="test-seed")
    assert first != second
