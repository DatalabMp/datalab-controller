"""Hard repository-scope policy for the DataLab controller."""

from __future__ import annotations

from collections.abc import Iterable

AUTHORIZED_OWNER = "DatalabMp"
CONTROLLER_REPOSITORY = "datalab-controller"

FORBIDDEN_OPERATIONS = frozenset(
    {
        "delete_repository",
        "transfer_repository",
        "change_repository_owner",
        "manage_billing",
        "manage_members",
        "modify_account",
        "write_outside_allowed_owner",
    }
)


class ScopeViolation(PermissionError):
    """Raised when an operation would leave the DataLab authorization boundary."""


def split_repository(full_name: str) -> tuple[str, str]:
    parts = full_name.split("/", maxsplit=1)
    if len(parts) != 2 or not all(parts):
        raise ScopeViolation(f"Invalid repository name: {full_name!r}")
    return parts[0], parts[1]


def assert_owner(full_name: str) -> tuple[str, str]:
    owner, repository = split_repository(full_name)
    if owner != AUTHORIZED_OWNER:
        raise ScopeViolation(
            f"Repository outside DataLab scope: {full_name}. "
            f"Allowed owner is {AUTHORIZED_OWNER}."
        )
    return owner, repository


def assert_operation_allowed(operation: str) -> None:
    if operation in FORBIDDEN_OPERATIONS:
        raise ScopeViolation(f"Operation is permanently forbidden: {operation}")


def assert_repository_write_allowed(
    full_name: str,
    *,
    registered_projects: Iterable[str],
    manifest_managed: bool,
    allow_controller: bool = False,
) -> None:
    """Authorize a repository write only after all deterministic scope checks pass."""

    _, repository = assert_owner(full_name)

    if allow_controller and repository == CONTROLLER_REPOSITORY:
        return

    registered = set(registered_projects)
    if repository not in registered:
        raise ScopeViolation(f"Repository is not registered in projects.yaml: {repository}")
    if not manifest_managed:
        raise ScopeViolation(
            f"Repository {full_name} does not declare managed=true in its DataLab manifest."
        )
