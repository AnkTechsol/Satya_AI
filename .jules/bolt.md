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

## 2024-05-24 - O(N log N) Sorting for Top K elements
**Learning:** Python's `sorted()` function creates a full copy of the list and sorts it in O(N log N) time, which is inefficient when we only need a small slice of the top elements for rendering dashboard tables.
**Action:** Always replace `sorted(lst, reverse=True)[:k]` or `lst.sort(reverse=True); lst[:k]` with `heapq.nlargest(k, lst)` to achieve O(N log K) time complexity and prevent unnecessary full array sorts during frontend renders.
