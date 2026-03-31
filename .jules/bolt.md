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

## 2024-05-24 - Thread-safe Caching & TOCTOU
**Learning:** When manually updating an `mtime`-based cache after a file write (e.g., `save_heartbeat`), calling `os.path.getmtime()` creates a Time-of-Check to Time-of-Use (TOCTOU) race condition. Also, expensive synchronous operations like `copy.deepcopy()` block other threads when done inside `threading.Lock()` blocks.
**Action:** Invalidate or update the cache manually after writing instead of checking `mtime`. And always perform heavy tasks like `copy.deepcopy()` outside the `threading.Lock()` block to reduce lock contention.
