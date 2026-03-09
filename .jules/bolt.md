## 2023-10-27 - Flat-file N+1 file reads
**Learning:** In zero-database, flat-file JSON architectures, calling a list function (like `tasks_manager.list_all()`) reads every file from disk synchronously. Multiple calls in the same render loop cause severe N+1 I/O bottlenecks.
**Action:** Always fetch the complete list once per render cycle and perform all aggregations (stats, metrics, filtering) in a single in-memory pass.
