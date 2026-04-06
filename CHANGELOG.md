# Changelog

## [Unreleased]

### Added
- Implemented **Langfuse Adapter** and finalized **OTLP Adapter** with exact JSON exports (Risk level: Low).
- Implemented **Agent Self-Test Harness + CI Analytics Job** to continuously test agent workflows, mock the simulation environment for CI, and auto-update performance traces into `repo_analytics.json` and `REPO_ANALYTICS.md` automatically on push.
- Created `repo_analytics.json` and updated `REPO_ANALYTICS.md` with recent execution telemetry via the snapshot branch.
- Initial **Repo Analytics** script (`repo_analytics.json`, `REPO_ANALYTICS.md`) to measure repo health.
- Added **Competitor Matrix** (`COMPETITOR_MATRIX.md`) to guide strategic roadmap.
- Implemented **Export Adapter Framework** (OTLP/Log export interface) to support enterprise integrations.

### Security
- Evaluated impact of new framework: Low Risk. Opt-in only via environment variables.
