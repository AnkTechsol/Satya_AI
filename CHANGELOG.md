# Changelog

## [Unreleased]

### Added
- Implemented **Agent Self-Test Harness + CI Analytics Job** to continuously test agent workflows, mock the simulation environment for CI, and auto-update performance traces into `repo_analytics.json` and `REPO_ANALYTICS.md` automatically on push.
- Created `repo_analytics.json` and updated `REPO_ANALYTICS.md` with recent execution telemetry via the snapshot branch.
- Initial **Repo Analytics** script (`repo_analytics.json`, `REPO_ANALYTICS.md`) to measure repo health.
- Added **Competitor Matrix** (`COMPETITOR_MATRIX.md`) to guide strategic roadmap.
- Implemented **Export Adapter Framework** (OTLP/Log export interface) to support enterprise integrations.

### Security
- Evaluated impact of new framework: Low Risk. Opt-in only via environment variables.

## [Unreleased]
### Added
- **Export Adapter Framework (OTLP)** (Risk: Low): Introduced an HTTP-based `OTLPAdapter` in `src/satya/sdk/adapters/otlp.py` allowing developers to stream flat-file telemetry traces directly into OpenTelemetry-compatible enterprise observability stacks without requiring a database.
- **Agent Self-Test Harness + CI Analytics Job** (Risk: Low): Added `.github/workflows/analytics_and_test.yml` to automatically run tests (`pytest`) and generation metrics (`python generate_analytics.py`) on each push to `main`, ensuring real-time `REPO_ANALYTICS.md` and reducing documentation rot.
- **Repo Analytics and Competitor Matrix** (Risk: None): Created `REPO_ANALYTICS.md`, `repo_analytics.json`, and `COMPETITOR_MATRIX.md` to establish project health metrics and a strategic competitive map.
