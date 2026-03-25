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

## 2024-05-25 - In-Memory Caching for Flat Files
**Learning:** Reading flat files (e.g. JSON task files) continuously creates a significant I/O bottleneck, especially when acquiring file locks. Furthermore, simply caching parsed Python dictionaries leads to shared mutable state bugs if consumers modify the dictionaries.
**Action:** Implement an in-memory cache that stores the raw string and re-parses it on demand (`json.loads(cached_str)`). To prevent stale reads in a multi-process environment, validate the cache using the file's modification time (`os.path.getmtime`). Always apply a size limit (eviction policy) and wrap eviction logic in `threading.Lock()` to prevent race conditions.
