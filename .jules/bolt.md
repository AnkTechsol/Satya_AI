## 2024-05-23 - Flat-file N+1 file reads
**Learning:** In a flat-file architecture, calling functions that scan the entire data directory (like `get_stale_tasks` or `list_all`) multiple times per request leads to an N+1 disk I/O problem.
**Action:** Always allow passing already-loaded data into secondary checkers or metrics calculators to reuse in-memory state.

## 2024-05-23 - Caching TOCTOU on file writes
**Learning:** In `mtime`-based caching architectures, if you call `os.path.getmtime(file)` immediately after `save_json(file)`, another process might modify the file in between the write and the mtime check, causing you to store the *new* mtime with your *old* data, resulting in stale reads.
**Action:** The safest way to handle cache-after-write is to either use the `mtime` returned directly by the atomic file system write operation (if available), or accept the slight TOCTOU risk for non-critical file updates while keeping the lock as tight as possible around the write-and-stat.
