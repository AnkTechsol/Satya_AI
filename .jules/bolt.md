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

## 2025-02-14 - Optimizing In-Memory Caching for Flat-File JSON Storage
**Learning:** Using deepcopy() when caching JSON objects in-memory adds overhead. Caching the raw string and parsing it using `json.loads(cached_str)` on demand leverages fast, native C JSON parsing while avoiding mutable reference issues. In addition, when implementing filesystem caches with `mtime` as validation keys, testing environments with fast IO can cause race conditions where tests run faster than the `mtime` resolution. Manual update of the cache state on file saving guarantees synchronous consistency. Unbounded memory caches can cause fatal out-of-memory errors over long sessions; implementing bounds (like an LRU or FIFO maximum item limit) is essential.
**Action:** When creating in-memory caching solutions for JSON data from files, cache raw strings and use `json.loads` over caching dicts and running `deepcopy()`. Always manually update validation metadata (`mtime`) in the cache upon any write actions to ensure sync with fast-running test routines, and always strictly bound the cache size to prevent memory leaks.
