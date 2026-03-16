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

## 2026-03-16 - Flat-file JSON Read Caching
**Learning:** Repeated reads of large numbers of flat-file JSONs without a database cause significant disk I/O bottlenecks. Caching the raw JSON string and parsing it with native C `json.loads` is significantly faster than using `copy.deepcopy()` on parsed objects. Furthermore, when using `mtime` cache invalidation, tests often fail due to test execution speed exceeding file system `mtime` resolution.
**Action:** Implement bounded, `mtime`-based in-memory caching for JSON reads that stores the raw string payload. Proactively and manually update the cache during write operations (like `save_json` or `delete_task_file`) to ensure cache consistency and prevent test framework race conditions.
