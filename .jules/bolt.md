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

## 2024-05-15 - [Flat-file Storage Read Optimization via Mtime string caching]
**Learning:** In flat-file architecture systems like Satya, iterating directories recursively triggers an O(N) read bottleneck. Loading and returning shared dictionaries directly can cause severe thread safety issues (shared mutable state across components loading the same dict).
**Action:** Next time when implementing a file-system cache in python, instead of `copy.deepcopy()`, use native string caching via `json.dumps()` on the `_json_cache` when writing to it, and parse with `json.loads()` locally inside `load_json`. This leverages C-level speed while avoiding global mutable state bugs, and use `os.path.getmtime` for cache invalidation.
