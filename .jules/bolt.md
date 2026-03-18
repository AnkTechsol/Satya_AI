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

## 2024-05-24 - JSON Caching & I/O Optimization
**Learning:** Implementing a process-local in-memory cache for flat-file storage without an invalidation strategy introduces severe cross-process data consistency bugs (stale reads), especially when file locking and atomic renames are used for concurrency. Also, caching JSON objects directly can introduce shared mutable state bugs if the cache is modified.
**Action:** Added `mtime` checking to a bounded in-memory cache (`_MAX_CACHE_SIZE = 1000`) for JSON files. `load_json` now verifies that the cached `mtime` matches the file system's `os.path.getmtime(filepath)` before returning a cached payload, ensuring data consistency across multiple processes while still avoiding N+1 file reads. It stores the raw JSON strings and uses `json.loads` on read to prevent shared mutable state bugs. The cache also updates synchronously on writes (`save_json`) and removes items on deletion (`delete_task_file`) to ensure consistency.
