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

## 2024-05-23 - mtime resolution and JSON cache
**Learning:** When implementing file-system caching based on `mtime`, test framework execution speeds can exceed `mtime` resolution. Caching `copy.deepcopy()` is slow in Python, but caching raw JSON strings and parsing with `json.loads(cached_str)` on demand takes advantage of native C parsing speeds for faster execution while avoiding modification bugs.
**Action:** Always manually update the in-memory cache directly during `save_json` operations with the raw JSON string instead of relying purely on `mtime` invalidation to prevent test failures due to race conditions.
