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

## 2024-05-23 - JSON LRU In-Memory Cache Optimization
**Learning:** To prevent severe N+1 I/O bottlenecks in a flat-file architecture, implementing an in-memory cache is crucial. We must cache the `raw_string` instead of deeply nested dictionary objects to save processing time on `copy.deepcopy()` since native C `json.loads()` is much faster, while naturally avoiding accidental in-memory mutations. Additionally, `os.path.getmtime()` resolution might not be fast enough during synchronous writes, so manually updating the cache with `json.dumps()` *after* renaming the file is required to prevent immediate read race conditions where test framework speeds exceed `mtime` resolution.
**Action:** Always manually update in-memory cache representations alongside explicit disk-writes to bypass mtime constraints on fast executing processes like unit-tests.
