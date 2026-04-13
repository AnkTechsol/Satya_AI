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

## 2024-05-23 - Top K Retrieval Optimization
**Learning:** In a flat-file architecture, sorting the entire list of tasks or audit events using `sorted(lst, reverse=True)[:k]` is unnecessarily slow ($O(N \log N)$), especially when only the top $K$ items are needed for dashboard rendering.
**Action:** Replace full list sorting with `heapq.nlargest(k, lst)`, which operates in $O(N \log K)$ time, providing a measurable performance boost for dashboard load times.
