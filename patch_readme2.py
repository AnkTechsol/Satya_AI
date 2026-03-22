import re

with open("README.md", "r") as f:
    content = f.read()

replacement = """## SUSTAINABLE_FEATURES

- **Agent Self-Test Harness + CI Analytics Job** (Added 2026-03)
  - Implements a GitHub Action to continuously test agent deployment workflows and auto-update performance traces into `repo_analytics.json` and `REPO_ANALYTICS.md`, reducing doc rot and catching runtime regressions early.
  - Runbook: Commits on `main` automatically run the suite. For local execution, run `python generate_analytics.py`.
  - Validation: Ensure `.github/workflows/analytics_and_test.yml` runs successfully on pushes.

- **Export Adapter Framework (OTLP/Console)** (Added 2026-03)
  - Enables routing Satya's flat-file telemetry traces into enterprise observability stacks without breaking zero-DB architecture.
  - Runbook: Pass a list of instantiated adapters to `satya.init(adapters=[OTLPAdapter()])`.
  - Validation: `PYTHONPATH=. pytest tests/test_adapters.py`

- **Repo Analytics & Competitor Matrix**
  - View [Repo Analytics](REPO_ANALYTICS.md) and [Competitor Matrix](COMPETITOR_MATRIX.md).

For more details on changes, see our [CHANGELOG](CHANGELOG.md)."""

content = re.sub(r'## SUSTAINABLE_FEATURES.*?(?=\n## |\Z)', replacement, content, flags=re.DOTALL)

with open("README.md", "w") as f:
    f.write(content)
