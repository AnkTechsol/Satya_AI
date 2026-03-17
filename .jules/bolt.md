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

## 2024-05-23 - AI Orchestrator N+1 Task Scans
**Learning:** In a flat-file backend architecture, checking tasks multiple times per polling loop based on different agent assignees scales poorly (O(Agents * Tasks)).
**Action:** When iterating over distinct entities (like agents), fetch the full data array once (O(Tasks)), build a hash map grouped by the entity key, and pass the pre-filtered subset to the processor function.
