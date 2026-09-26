# Project Factory setup

The Project Factory creates only **public** repositories under `DatalabMp` and initializes the managed DataLab scaffold.

## Required GitHub App

Create a dedicated GitHub App owned by `DatalabMp`, for example **DatalabMp Project Factory**. Keep webhooks disabled unless another feature later requires them.

Install the App on the `DatalabMp` organization with access to **All repositories** so that repositories created later are immediately inside the installation scope.

Minimum repository permissions required by the current factory:

- **Administration: Read and write** — create the organization repository and manage the initial Pages site.
- **Contents: Read and write** — create the manifest, source scaffold, tests and documentation.
- **Workflows: Read and write** — create CI and Pages workflow files under `.github/workflows/`.
- **Pages: Read and write** — enable the initial GitHub Pages site.
- **Metadata: Read-only** — implicit/basic repository metadata access.

Do not grant billing, members, organization administration unrelated to repository creation, account, email, or destructive repository permissions beyond what GitHub couples to Administration. The controller policy still permanently forbids repository deletion, transfer, owner changes, member management, billing changes and writes outside `DatalabMp`.

## Secrets

Generate one private key for the App. Never commit the `.pem` file and never paste it into issues, source files or chat messages.

In `DatalabMp/datalab-controller` open:

`Settings → Secrets and variables → Actions`

Create these repository secrets:

- `DATALAB_APP_ID` — the GitHub App ID.
- `DATALAB_PRIVATE_KEY` — the complete PEM private key contents.

The workflow exchanges these credentials for a short-lived installation token at runtime. The token is scoped to the `DatalabMp` installation.

## Factory behavior

`.github/workflows/project-factory.yml` checks once per hour. It creates nothing unless:

1. both App secrets exist;
2. the 72-hour project interval has elapsed;
3. a project remains `queued` in `config/projects.yaml`;
4. the target owner is exactly `DatalabMp`;
5. the target repository does not already exist.

The first eligible project is selected by priority. The factory refuses to auto-adopt an already-existing repository with the same slug.

Every new repository is created public and starts with:

- `.datalab/manifest.json`;
- `PROJECT_PLAN.md`;
- Python project metadata;
- a package scaffold;
- smoke tests;
- CI;
- GitHub Pages workflow;
- a minimal dashboard landing page.

After successful creation, the controller marks the project `active`, updates `last_project_started_at`, and records the event in `state/runtime.json`.

## Zero-cost rule

The Project Factory does not call any paid AI or external inference API. Standard GitHub-hosted Actions used by these public repositories are intended to remain within the public-repository free execution model. If GitHub changes billing or availability rules, review the controller configuration before continuing automation.

## Emergency stop

Disable `.github/workflows/project-factory.yml`, remove/rotate the App private key, or uninstall the GitHub App from `DatalabMp`. The App must never be installed on `MarcosT2T` personal repositories for this DataLab workflow.
