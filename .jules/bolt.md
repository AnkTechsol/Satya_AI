## 2023-10-27 - Flat-file N+1 file reads
**Learning:** In zero-database, flat-file JSON architectures, calling a list function (like `tasks_manager.list_all()`) reads every file from disk synchronously. Multiple calls in the same render loop cause severe N+1 I/O bottlenecks.
**Action:** Always fetch the complete list once per render cycle and perform all aggregations (stats, metrics, filtering) in a single in-memory pass.

## 2025-03-10 - Fast string parsing vs deepcopy
**Learning:** When building an in-memory cache for JSON files, caching the parsed dictionary directly is dangerous because callers might mutate it. Deep copying the cached dict is safe but slow. Surprisingly, caching the raw JSON string and calling `json.loads(cached_str)` on every cache hit is ~3x faster than `copy.deepcopy()` because `json.loads` is implemented natively in C.
**Action:** When caching JSON objects in memory to avoid disk I/O, cache the raw string and parse it on demand instead of deep copying.
