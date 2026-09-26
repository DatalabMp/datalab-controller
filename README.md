# DataLab Controller

Control plane for the **DatalabMp** autonomous data-science portfolio.

## Mission

Create and evolve public, reproducible data-science projects based on real datasets, with emphasis on interpretation, statistical rigor, dashboards, testing, security and transparent monitoring.

## Non-negotiable rules

- Authorized GitHub owner: `DatalabMp` only.
- Never modify repositories outside `DatalabMp`.
- Specialist agents do not push code directly.
- Only the Executor may write after required review gates pass.
- No empty/artificial commits.
- External AI/API budget is hard-capped at **USD 0.00**.
- Paid-model fallback is forbidden.
- If all free/local inference options are unavailable, the run pauses rather than spend money.
- Analytical conclusions must distinguish association from causality and document limitations.

## Specialist agents

1. Requirements
2. Data Quality / Engineering
3. Statistics
4. Modeling
5. Architecture
6. Visualization / Dashboard
7. QA / Testing
8. Security
9. Reviewer
10. Executor (the only write-capable role)

## Planned projects

- Brazil Road Safety Analytics — PRF
- Brazil Economic Monitor — Banco Central do Brasil
- ENEM Analytics — INEP
- Brazil Population & Labor Observatory — IBGE
- SUS Health Analytics — DATASUS
- Brazil Agriculture Analytics — IBGE/PAM

## Monitoring

The Agent Operations Center is published through GitHub Pages and is rebuilt from controller state. It shows project progress, agent state, validation gates, failures, commits, provider state and confirmed external-model cost.

Expected URL: `https://datalabmp.github.io/datalab-controller/`

## Project Factory

The controller includes a guarded repository factory for the 72-hour project cadence. It is disabled until the dedicated GitHub App credentials are added as Actions secrets. See [`docs/PROJECT_FACTORY_SETUP.md`](docs/PROJECT_FACTORY_SETUP.md).

The factory can create only public repositories under `DatalabMp`, refuses automatic adoption of pre-existing repositories, initializes the DataLab manifest/CI/tests/Pages scaffold, and records the new project in controller state.

## Status

- Controller foundation: active
- CI: passing
- Operations Center: GitHub Pages deployment enabled
- Project Factory code: prepared
- Project Factory credentials: pending operator setup
