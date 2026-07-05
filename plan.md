1. **Fix Missing Implementations**: Recreate the Export Adapter files (`src/satya/core/adapters/base.py`, `src/satya/core/adapters/langsmith.py`, `src/satya/core/adapters/otlp.py`, `src/satya/core/adapters/__init__.py`) using exact bash commands to ensure they contain the required code.
2. **Update Competitor Matrix**: Use `replace_with_git_merge_diff` to update `COMPETITOR_MATRIX.md` correctly, verifying the exact text before modifying.
3. **Update README**: Update the `SUSTAINABLE_FEATURES` section of `README.md` to document the new adapters, verifying exact text before modifying.
4. **Update Changelog**: Append a new entry for the Export Adapter Framework to `CHANGELOG.md`.
5. **Verify Tests Pass**: Execute `PYTHONPATH=. AUDIT_SECRET=dummy_secret SATYA_AGENT_KEY=DEMO_KEY SATYA_AGENT_KEYS=DEMO_KEY pytest tests/` to verify tests pass and no regressions exist.
6. **Pre-commit**: Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.
7. **Submit changes**: Run `submit` with the feature branch `jules/feature-export-adapters`, including a clear message indicating this is a fix for the CI failures and the completion of the feature.
