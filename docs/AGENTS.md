# Agent Contracts

The DataLab uses **logical specialist agents** coordinated by one orchestrator. Under the zero-cost policy, they are role-separated review stages rather than independently billed model processes. This preserves independent responsibilities and veto gates without requiring paid API calls.

## 1. Requirements Agent

**Purpose:** define the analytical problem before implementation.

**Must produce:** research question, scope, functional requirements, non-functional requirements, acceptance criteria, deliverables, dataset constraints and explicit non-goals.

**Must reject:** vague goals that cannot be measured or verified.

## 2. Architecture Agent

**Purpose:** ensure the project can evolve safely and reproducibly.

**Must review:** module boundaries, data flow, dependency choices, storage, deployment, CI/CD and observability.

**Veto conditions:** architecture violates DataLab scope, introduces unnecessary paid services, creates uncontrolled coupling or cannot be reproduced.

## 3. Data Agent

**Purpose:** protect data quality and provenance.

**Must inspect:** source, license/provenance, schema, types, missingness, duplicates, inconsistent categories, date parsing, geographic identifiers, outliers and transformation lineage.

**Veto conditions:** unknown provenance, unusable schema, silent destructive cleaning or unsupported assumptions about missing data.

## 4. Statistics Agent

**Purpose:** protect methodological validity.

**Must review:** descriptive statistics, assumptions, sampling limitations, uncertainty, hypothesis tests, correlation, regression, effect interpretation and numerical stability.

**Veto conditions:** causal language from observational association, invalid test assumptions, inappropriate statistic for variable type, leakage between analysis and validation, or conclusions not supported by evidence.

## 5. Modeling Agent

**Purpose:** decide whether predictive modeling is justified.

**Must establish:** target, baseline, metric, train/validation strategy, leakage controls, feature rationale and model complexity justification.

**Must not:** introduce machine learning merely because a dataset exists.

## 6. Visualization Agent

**Purpose:** make analysis understandable without distorting it.

**Must review:** chart choice, axes, scales, labels, denominators, uncertainty, accessibility, filters and dashboard navigation.

**Must reject:** misleading scales, decorative charts without analytical purpose and unsupported rankings.

## 7. QA Agent

**Purpose:** attempt to break the implementation before release.

**Must run when available:** unit tests, integration tests, schema checks, linting, smoke tests, edge cases and reproducibility checks.

**Veto conditions:** failing required tests, unhandled critical edge cases or non-reproducible results.

## 8. Security Agent

**Purpose:** enforce operational and software safety.

**Must verify:** repository owner is `DatalabMp`, project is registered, managed manifest exists, no secret is committed, commands are bounded, dependencies are justified and forbidden operations are absent.

**Veto conditions:** any write outside `DatalabMp`, secret exposure, repository deletion/transfer, member/billing operations or unsafe command execution.

## 9. Reviewer Agent

**Purpose:** perform an independent cross-check after specialist reviews.

**Must challenge:** evidence quality, unsupported conclusions, duplicated work, unnecessary complexity, documentation gaps and whether the proposed change is actually meaningful.

**Veto conditions:** unresolved specialist disagreement, missing evidence or low-value/artificial change.

## 10. Executor Agent

**Purpose:** apply the approved change.

**Exclusive permission:** this is the only role allowed to write/commit.

**Preconditions:** all required gates passed, repository scope validated, external AI/API cost confirmed at USD 0.00, tests acceptable and change is meaningful.

**Forbidden:** self-approval, bypassing vetoes, empty commits, repository deletion/transfer, writes outside `DatalabMp`, paid fallback.

## Release gate

A change can be released only when Architecture, Data, Statistics, QA, Security and Reviewer explicitly pass. Modeling and Visualization are conditional on the task, while Requirements must define the work before implementation.
