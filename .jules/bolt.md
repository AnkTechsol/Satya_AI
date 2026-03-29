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

## 2026-03-29 - Cache mutability in Python
**Learning:** When implementing an in-memory cache that returns dictionaries, returning the exact cached dictionary reference causes cross-contamination if the caller modifies the dictionary. This breaks data isolation.
**Action:** Always use `copy.deepcopy()` when returning mutable structures from an in-memory cache, ensuring deep copy happens outside thread locks to minimize contention.
