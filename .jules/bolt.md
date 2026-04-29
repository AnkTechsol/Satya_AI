# Bolt's Performance Journal

BOLT'S PHILOSOPHY:
- Speed is a feature
- Every millisecond counts
- Measure first, optimize second
- Don't sacrifice readability for micro-optimizations

## Critical Learnings

## 2024-05-23 - Flat-file N+1 file reads
**Learning:** In a flat-file architecture, calling functions that scan the entire data directory (like `get_stale_tasks` or `list_all`) multiple times per request leads to an N+1 disk I/O problem.
**Action:** Always allow passing already-loaded data into secondary checkers or metrics calculators to reuse in-memory state.
## 2026-04-19 - Mitigate DB connection overhead during loop operations
**Learning:** Initializing an SQLite DB schema (`CREATE TABLE IF NOT EXISTS`) and establishing connections on every single method invocation for an append operation causes substantial performance bottlenecks in Python, particularly when appending continuous logs or events.
**Action:** When designing a fallback DB or storage utility meant to be called repeatedly, establish connection logic or schema-check logic as a singleton or behind a global `_DB_INITIALIZED` state flag to ensure it evaluates only once per process.
## 2026-04-19 - Batching Streamlit markdown calls
**Learning:** Rendering many lines individually via `st.markdown` causes heavy Streamlit communication overhead and blocks the UI thread.
**Action:** Batch HTML/Markdown strings and render them using a single `st.markdown` call.
## 2024-05-23 - Reuse global variables across Streamlit pages
**Learning:** Variables fetched/computed at the root level of `app.py` (like `all_tasks`, `stats`, `agent_metrics`) are in scope for the subsequent page-specific conditionals.
**Action:** Do not re-fetch the same data from disk (e.g. `tasks_manager.list_all()`) inside specific page blocks (like "ROI Dashboard") when the same data has already been fetched and aggregated at the root level. Reuse the root-level variables.
