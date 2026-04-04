# Changelog

## [Unreleased]
- **2026-04-04 14:45 UTC**: Implemented a Durable Append-Only Audit Store using SQLite to securely track agent events, adding enterprise readiness while maintaining a zero-infrastructure fallback to JSONL (`src/satya/core/audit_db.py`, `src/satya/auth.py`). (Risk: Low - fully backward compatible with fallback mechanism).
- **2026-04-04 14:40 UTC**: Updated Repository Analytics and `COMPETITOR_MATRIX.md` as part of Jules' regular analytics scan.

### Added
- Implemented **Agent Self-Test Harness + CI Analytics Job** to continuously test agent workflows, mock the simulation environment for CI, and auto-update performance traces into `repo_analytics.json` and `REPO_ANALYTICS.md` automatically on push.
- Created `repo_analytics.json` and updated `REPO_ANALYTICS.md` with recent execution telemetry via the snapshot branch.
- Initial **Repo Analytics** script (`repo_analytics.json`, `REPO_ANALYTICS.md`) to measure repo health.
- Added **Competitor Matrix** (`COMPETITOR_MATRIX.md`) to guide strategic roadmap.
- Implemented **Export Adapter Framework** (OTLP/Log export interface) to support enterprise integrations.

### Security
- Evaluated impact of new framework: Low Risk. Opt-in only via environment variables.
