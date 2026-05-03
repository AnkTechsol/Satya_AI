# Changelog

## [Unreleased]
- [2026-04-16] **Added:** Repository analytics generation script and CI mock for automated code health checks. (Risk: Low)
- [2026-04-16] **Added:** Competitor analysis matrix (`COMPETITOR_MATRIX.md`). (Risk: Low)
- [2026-04-16] **Added:** OTLP Export Adapter framework for OpenTelemetry support (`satya.sdk.adapters.otlp`). (Risk: Low)

### Added
- Implemented **Durable Append-only Audit Store** providing an opt-in SQLite backend (`SATYA_SQLITE_DB`) for atomic and compliant audit trail storage.
- Expanded `generate_analytics.py` with an **Auto-README Updater Action** that injects real-time telemetry back into the main `README.md`.
- Implemented **Agent Self-Test Harness + CI Analytics Job** to continuously test agent workflows, mock the simulation environment for CI, and auto-update performance traces into `repo_analytics.json` and `REPO_ANALYTICS.md` automatically on push.
- Created `repo_analytics.json` and updated `REPO_ANALYTICS.md` with recent execution telemetry via the snapshot branch.
- Initial **Repo Analytics** script (`repo_analytics.json`, `REPO_ANALYTICS.md`) to measure repo health.
- Added **Competitor Matrix** (`COMPETITOR_MATRIX.md`) to guide strategic roadmap.
- Implemented **Export Adapter Framework** (OTLP/Log export interface) to support enterprise integrations.

### Security
- Evaluated impact of new framework: Low Risk. Opt-in only via environment variables.

## [Unreleased]
- **Added** `repo_analytics.json` and `REPO_ANALYTICS.md` to run runtime analytics in CI. Risk: Low (reads data and executes minimal simulation).
- **Added** `LangfuseAdapter` export adapter to support telemetry streaming to Langfuse. Risk: Low (plugs into existing Adapter framework, isolates failures via timeouts).

## [Unreleased] - 2026-05-03

### Added
- **docs**: Added `COMPETITOR_MATRIX.md` to analyze features vs peers. (Risk: Low)
- **ci**: Added `.github/workflows/analytics.yml` and `self-test.yml` for automated testing and repo analytics updates. (Risk: Low)
- **core**: Added `src/satya/core/telemetry.py` providing an export adapter framework (`OTLPJsonExporter`) to record agent traces and lifecycle events. (Risk: Medium)
- **core**: Integrated telemetry into `project_manager.py` (Orchestrator) and `tasks.py` (Task completion tracking). (Risk: Medium)
- **scripts**: Updated `generate_analytics.py` script to collect deeper system health context (code health, languages). (Risk: Low)
