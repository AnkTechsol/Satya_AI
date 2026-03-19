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

## 2025-02-23 - In-memory JSON caching and shared state bugs
**Learning:** In a zero-database system, `load_json` bottlenecked the application due to repetitive file parsing. Implementing an `mtime`-based cache improves speeds significantly, but caching loaded Python dictionaries creates a shared mutable state bug if the dictionary is accidentally modified by any consumer.
**Action:** Cache the raw JSON string instead, and use `json.loads` upon cache hit. Python's native JSON parser is fast enough that the primary savings come from avoiding disk reads, not avoiding object creation.
