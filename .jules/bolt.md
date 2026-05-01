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
## 2024-05-24 - Streamlit Page Routing Optimization
**Learning:** In Streamlit applications where page navigation uses `if/elif` blocks on `st.radio` input, defining shared data variables like `all_tasks` at the root/module scope ensures they are fetched exactly once per rerun and are safely accessible to all subsequent page blocks. Redundant data fetches inside specific page blocks (like `ROI Dashboard`) bypass this cache and cause unnecessary file I/O operations.
**Action:** When optimizing Streamlit apps for performance, always hoist shared database queries or file reads to the top-level script scope (or use `@st.cache_data`) before the page routing conditional logic.
