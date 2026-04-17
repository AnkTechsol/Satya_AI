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

## 2026-04-17 - Batched st.markdown string rendering
**Learning:** The codebase uses an unpaginated flat-file architecture where entire files (like agent logs) are loaded into memory at once. To prevent Streamlit UI thread blocking, always batch HTML string renders into a single st.markdown call rather than rendering them line-by-line.
**Action:** Replaced loop of multiple st.markdown calls with a single batched call in app.py
