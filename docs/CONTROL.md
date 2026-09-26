# Operator Controls

The DataLab can be directed without editing code. Create an **open issue** in `DatalabMp/datalab-controller` using one of the supported title forms below. The scheduled orchestrator reads the newest applicable control issue before selecting work.

## Commands

- `[control] pause` — stop project-changing work; monitoring/status checks may continue.
- `[control] resume` — return to normal autonomous operation.
- `[control] focus <project-slug>` — direct the next meaningful work slots to a managed project when safe and justified.
- `[control] priority <project-slug>` — raise a managed project in the work-selection order.
- `[control] review <project-slug>` — prioritize an independent review/audit of the named project.
- `[control] deploy <project-slug>` — prioritize deployment work after normal quality/security gates pass.

Example:

```text
[control] focus brazil-road-safety
```

## Precedence

The newest applicable open control issue is treated as the current operator directive. A control issue **never overrides**:

- owner boundary (`DatalabMp` only);
- zero external AI/API cost;
- forbidden destructive/account operations;
- scientific/statistical quality gates;
- QA/security/reviewer vetoes;
- requirement for meaningful changes.

## Auditability

When a control is applied, the orchestrator records the directive, source issue and timestamp in runtime monitoring state so it can be displayed in the Operations Center.
