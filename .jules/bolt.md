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
## 2026-04-15 - Streamlit st.markdown in loops
**Learning:** Repeatedly calling `st.markdown()` inside a Python loop (e.g., when rendering log files line-by-line) causes severe performance degradation in Streamlit due to IPC communication and React element creation overhead.
**Action:** Always batch HTML/Markdown generation using Python string methods (like `''.join()`) and pass the final composed string into a single `st.markdown()` call.
