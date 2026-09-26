# Remaining Setup

The controller is designed to remain at **USD 0.00 external AI/API cost**.

## GitHub Pages

The workflow is already present. GitHub currently requires the Pages site to be enabled once with **GitHub Actions** as the source. Until that is done, the Pages workflow exits without breaking the rest of the controller.

Path in GitHub: `datalab-controller` → **Settings** → **Pages** → **Build and deployment** → Source: **GitHub Actions**.

## Autonomous repository creation

The ChatGPT GitHub connection can edit existing repositories but does not expose repository creation. Creating a new public repository every 72 hours therefore requires a separate GitHub credential available to GitHub Actions, preferably a dedicated GitHub App installation token with least privilege. Do not store raw credentials in the repository.

Until repository-creation authorization exists, the controller must record the 72-hour project transition as blocked rather than attempting to create a repository elsewhere.

## AI/model execution

No paid provider is configured. The scheduled ChatGPT automation is the current reasoning/orchestration layer and must obey the repository policies. Optional future remote providers may be added only when their effective cost is explicitly confirmed as zero and no paid fallback can occur.

## Safety invariant

No setup step is allowed to broaden the working owner beyond `DatalabMp`.
