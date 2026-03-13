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

## 2025-02-16 - File Caching and Object Mutation
**Learning:** When building an in-memory cache for JSON files, caching the parsed `dict` and returning it directly leads to object mutation bugs if the caller modifies the dictionary. Using `copy.deepcopy()` is slow. However, caching the `raw_str` (the JSON string) and parsing it on demand via native C `json.loads(cached_str)` is both safe from mutation and significantly faster.
**Action:** Always cache the raw string and parse on demand rather than caching the parsed dictionary or using `deepcopy`. Furthermore, update the cache during file save operations to prevent `mtime` race conditions in fast test suites.
