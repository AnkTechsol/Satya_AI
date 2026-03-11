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

## 2024-05-23 - JSON caching and mtime race conditions
**Learning:** When caching JSON objects in memory to avoid disk I/O, native C JSON parsing (`json.loads(cached_str)`) is significantly faster than using `copy.deepcopy()`. Also, when implementing file-system caching based on `mtime`, test framework execution speeds can exceed `mtime` resolution.
**Action:** Always cache the raw string and parse it on demand. Always manually update the in-memory cache and its `mtime` during file save operations to prevent race conditions and test failures.
