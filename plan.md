1. **Commit Analytics Snapshot**: Create branch `jules/analytics-timestamp`, commit `repo_analytics.json` and `REPO_ANALYTICS.md`, and switch back to `main`.
2. **Update Competitor Matrix**: Edit `COMPETITOR_MATRIX.md` to ensure a concise comparison with LangSmith and Langfuse, highlighting observability depth, agent runtime support, self-host friendliness, enterprise features, export adapters, and pricing model signals.
3. **Implement Export Adapter Framework**:
   - Create `src/satya/core/adapters/base.py` with the abstract base class `ExportAdapter`.
   - Create `src/satya/core/adapters/langsmith.py` with LangSmith integration. It will map 'prompt' to 'inputs', 'response' to 'outputs', ensure trace IDs are valid UUIDs, use 'llm' for run type, include `end_time`, implement SSRF protection (custom HTTP adapter with IP validation via `socket.getaddrinfo`), and use short timeouts.
   - Create `src/satya/core/adapters/otlp.py` for OTLP-compatible exports.
   - Integrate adapters into `src/satya/sdk/client.py` so they are called asynchronously or non-blockingly during task updates and logs.
4. **Write Unit Tests**: Create `tests/test_adapters.py` to test both OTLP and LangSmith adapters. This will include mocking `socket.getaddrinfo` to return globally routable IPs to simulate SSRF protections, and verifying fallback UUIDs.
5. **Update Documentation**: Update `README.md` with the analytics summary and add the "Export Adapter Framework" to the `SUSTAINABLE_FEATURES` section. Update `CHANGELOG.md` with the new feature.
6. **Verification**: Run `python -m pytest tests/` with required environment variables to ensure everything passes and no regressions occur.
7. **Pre-commit**: Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
8. **Submit changes**: Run `submit` with the feature branch `jules/feature-export-adapter`, including the executive report with top risks and actions in the description.
