"""Fábrica segura para novos repositórios públicos gerenciados pelo DataLab."""

from __future__ import annotations

import argparse
import base64
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import yaml

from datalab.policy import AUTHORIZED_OWNER, assert_owner

ROOT = Path(__file__).resolve().parents[1]
API_BASE = "https://api.github.com"
API_VERSION = "2026-03-10"


class FactoryBlocked(RuntimeError):
    """Indica que a criação do repositório não pode prosseguir com segurança."""


@dataclass(frozen=True)
class ProjectSpec:
    slug: str
    title: str
    source: str
    status: str
    priority: int
    dashboard: str


def _load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_projects(path: Path | None = None) -> list[ProjectSpec]:
    document = _load_yaml(path or ROOT / "config/projects.yaml")
    return [ProjectSpec(**item) for item in document.get("projects", [])]


def select_next_queued(projects: list[ProjectSpec]) -> ProjectSpec | None:
    queued = [project for project in projects if project.status == "queued"]
    return min(queued, key=lambda project: project.priority, default=None)


def interval_elapsed(
    last_started_at: str | None,
    *,
    interval_days: int,
    now: datetime | None = None,
) -> bool:
    if not last_started_at:
        return True
    current = now or datetime.now(UTC)
    previous = datetime.fromisoformat(last_started_at)
    if previous.tzinfo is None:
        previous = previous.replace(tzinfo=UTC)
    return current - previous >= timedelta(days=interval_days)


def repository_payload(project: ProjectSpec) -> dict:
    assert_owner(f"{AUTHORIZED_OWNER}/{project.slug}")
    return {
        "name": project.slug,
        "description": f"{project.title} — projeto DataLab reproduzível com dados de {project.source}",
        "private": False,
        "has_issues": True,
        "has_projects": True,
        "has_wiki": False,
        "auto_init": True,
    }


def scaffold_files(project: ProjectSpec, created_at: str) -> dict[str, str]:
    package_name = project.slug.replace("-", "_")
    manifest = {
        "managed": True,
        "owner": AUTHORIZED_OWNER,
        "repository": project.slug,
        "controller": f"{AUTHORIZED_OWNER}/datalab-controller",
        "project_type": "data-science",
        "source": project.source,
        "dashboard": project.dashboard,
        "created_at": created_at,
        "language": "pt-BR",
    }

    project_readme = f"""# {project.title}

Projeto gerenciado pelo DataLab usando **{project.source}** como fonte de dados registrada.

## Contrato analítico

- Validar a qualidade dos dados antes de qualquer conclusão estatística.
- Distinguir associação de causalidade.
- Documentar dados ausentes, premissas, incertezas e limitações.
- Preferir pipelines reproduzíveis e testes a transformações manuais.
- Publicar resultados analíticos validados por meio do GitHub Pages.
- Escrever documentação, mensagens operacionais e commits em português do Brasil.

O repositório é gerenciado por `DatalabMp/datalab-controller`.
"""

    pyproject = f"""[project]
name = \"{project.slug}\"
version = \"0.1.0\"
requires-python = \">=3.12\"
dependencies = [\"pandas>=2.2,<3\", \"plotly>=6,<7\"]

[project.optional-dependencies]
dev = [\"pytest>=8,<10\", \"ruff>=0.8,<1\"]

[tool.setuptools.packages.find]
where = [\"src\"]

[tool.pytest.ini_options]
testpaths = [\"tests\"]

[tool.ruff]
line-length = 100
target-version = \"py312\"
"""

    ci_workflow = """name: Integração contínua

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  validar:
    runs-on: ubuntu-latest
    steps:
      - name: Baixar repositório
        uses: actions/checkout@v5
      - name: Configurar Python
        uses: actions/setup-python@v6
        with:
          python-version: \"3.12\"
      - name: Instalar dependências
        run: python -m pip install -e \".[dev]\"
      - name: Validar estilo
        run: ruff check .
      - name: Executar testes
        run: pytest -q
"""

    pages_workflow = """name: Publicar dashboard

on:
  push:
    branches: [main]
    paths:
      - \"docs/**\"
      - \".github/workflows/pages.yml\"
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  publicar:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Baixar repositório
        uses: actions/checkout@v5
      - name: Configurar Pages
        uses: actions/configure-pages@v5
      - name: Preparar artefato
        uses: actions/upload-pages-artifact@v4
        with:
          path: docs
      - name: Publicar
        id: deployment
        uses: actions/deploy-pages@v4
"""

    index_html = f"""<!doctype html>
<html lang=\"pt-BR\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>{project.title}</title></head>
<body><main><h1>{project.title}</h1><p>Fonte: {project.source}</p><p>Estrutura inicial do dashboard criada. O conteúdo analítico será publicado somente após a aprovação dos controles de qualidade de dados e da revisão estatística.</p></main></body></html>
"""

    return {
        ".datalab/manifest.json": json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        "PROJECT_PLAN.md": project_readme,
        "pyproject.toml": pyproject,
        f"src/{package_name}/__init__.py": '"""Pacote do projeto gerenciado pelo DataLab."""\n',
        "tests/test_smoke.py": (
            "from pathlib import Path\n\n\n"
            "def test_managed_manifest_exists() -> None:\n"
            "    assert Path('.datalab/manifest.json').is_file()\n"
        ),
        ".github/workflows/ci.yml": ci_workflow,
        ".github/workflows/pages.yml": pages_workflow,
        "docs/index.html": index_html,
    }


class GitHubClient:
    def __init__(self, token: str, *, api_base: str = API_BASE) -> None:
        if not token:
            raise FactoryBlocked("GH_TOKEN é obrigatório para criar repositórios.")
        self.token = token
        self.api_base = api_base.rstrip("/")

    def _request(self, method: str, path: str, payload: dict | None = None) -> dict:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.api_base}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": API_VERSION,
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            raise FactoryBlocked(f"API do GitHub retornou {exc.code} para {path}: {detail}") from exc
        return json.loads(body) if body else {}

    def repository_exists(self, slug: str) -> bool:
        assert_owner(f"{AUTHORIZED_OWNER}/{slug}")
        request = Request(
            f"{self.api_base}/repos/{AUTHORIZED_OWNER}/{slug}",
            method="GET",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": API_VERSION,
            },
        )
        try:
            with urlopen(request, timeout=30):
                return True
        except HTTPError as exc:
            if exc.code == 404:
                return False
            detail = exc.read().decode("utf-8", errors="replace")[:800]
            raise FactoryBlocked(
                f"API do GitHub retornou {exc.code} ao verificar o repositório: {detail}"
            ) from exc

    def create_repository(self, project: ProjectSpec) -> dict:
        return self._request("POST", f"/orgs/{AUTHORIZED_OWNER}/repos", repository_payload(project))

    def put_text_file(self, slug: str, path: str, content: str, message: str) -> None:
        assert_owner(f"{AUTHORIZED_OWNER}/{slug}")
        self._request(
            "PUT",
            f"/repos/{AUTHORIZED_OWNER}/{slug}/contents/{path}",
            {
                "message": message,
                "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            },
        )

    def enable_pages(self, slug: str) -> None:
        assert_owner(f"{AUTHORIZED_OWNER}/{slug}")
        self._request(
            "POST",
            f"/repos/{AUTHORIZED_OWNER}/{slug}/pages",
            {"build_type": "workflow"},
        )


def _write_controller_state(project: ProjectSpec, started_at: str) -> None:
    projects_path = ROOT / "config/projects.yaml"
    projects_doc = _load_yaml(projects_path)
    for item in projects_doc.get("projects", []):
        if item["slug"] == project.slug:
            item["status"] = "active"
    projects_path.write_text(
        yaml.safe_dump(projects_doc, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )

    state_path = ROOT / "state/runtime.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["active_project"] = project.slug
    state["last_project_started_at"] = started_at
    state.setdefault("project_progress", {})[project.slug] = {
        "status": "initialized",
        "progress_percent": 5,
        "blocker": None,
    }
    state.setdefault("recent_events", []).append(
        {
            "timestamp": started_at,
            "type": "project_initialized",
            "detail": (
                f"Repositório público gerenciado {AUTHORIZED_OWNER}/{project.slug} criado; "
                "estrutura inicial e controles de qualidade configurados. "
                "Custo externo de IA/API: USD 0,00."
            ),
        }
    )
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(*, dry_run: bool = False, now: datetime | None = None) -> dict:
    settings = _load_yaml(ROOT / "config/settings.yaml")
    projects = load_projects()
    project = select_next_queued(projects)
    if project is None:
        return {"status": "idle", "reason": "não há projetos na fila"}

    state = json.loads((ROOT / "state/runtime.json").read_text(encoding="utf-8"))
    interval_days = int(settings["execution"]["new_project_interval_days"])
    current = now or datetime.now(UTC)
    if not interval_elapsed(
        state.get("last_project_started_at"), interval_days=interval_days, now=current
    ):
        return {"status": "idle", "reason": "o intervalo entre projetos ainda não foi concluído"}

    assert_owner(f"{AUTHORIZED_OWNER}/{project.slug}")
    if dry_run:
        return {
            "status": "dry_run",
            "repository": f"{AUTHORIZED_OWNER}/{project.slug}",
            "public": True,
        }

    if os.environ.get("DATALAB_FACTORY_ENABLED", "").lower() != "true":
        raise FactoryBlocked("DATALAB_FACTORY_ENABLED deve ser exatamente 'true'.")

    client = GitHubClient(os.environ.get("GH_TOKEN", ""))
    if client.repository_exists(project.slug):
        raise FactoryBlocked(
            f"O repositório {AUTHORIZED_OWNER}/{project.slug} já existe; adoção automática recusada."
        )

    started_at = current.isoformat()
    client.create_repository(project)
    for path, content in scaffold_files(project, started_at).items():
        client.put_text_file(project.slug, path, content, f"manutenção: inicializa {path}")

    pages_status = "enabled"
    try:
        client.enable_pages(project.slug)
    except FactoryBlocked as exc:
        pages_status = f"blocked: {exc}"

    _write_controller_state(project, started_at)
    return {
        "status": "created",
        "repository": f"{AUTHORIZED_OWNER}/{project.slug}",
        "pages": pages_status,
        "external_ai_cost_usd": 0.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(dry_run=args.dry_run), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
