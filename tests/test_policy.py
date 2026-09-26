import pytest

from datalab.policy import (
    ScopeViolation,
    assert_operation_allowed,
    assert_owner,
    assert_repository_write_allowed,
)


def test_rejects_repository_outside_datalab_owner() -> None:
    with pytest.raises(ScopeViolation):
        assert_owner("MarcosT2T/ceub-mec-sistematizacao")


def test_allows_registered_managed_project() -> None:
    assert_repository_write_allowed(
        "DatalabMp/brazil-road-safety",
        registered_projects={"brazil-road-safety"},
        manifest_managed=True,
    )


def test_rejects_unregistered_project() -> None:
    with pytest.raises(ScopeViolation):
        assert_repository_write_allowed(
            "DatalabMp/random-project",
            registered_projects={"brazil-road-safety"},
            manifest_managed=True,
        )


def test_rejects_unmanaged_project() -> None:
    with pytest.raises(ScopeViolation):
        assert_repository_write_allowed(
            "DatalabMp/brazil-road-safety",
            registered_projects={"brazil-road-safety"},
            manifest_managed=False,
        )


def test_permanently_forbidden_operation() -> None:
    with pytest.raises(ScopeViolation):
        assert_operation_allowed("delete_repository")
