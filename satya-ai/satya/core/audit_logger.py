import asyncio
import json
import uuid
import logging
from typing import AsyncIterator, List, Dict, Any, Optional
from ..schemas.audit import AuditEventSchema, AuditQueryFilters, AuditSummary
from ..database import AsyncSessionLocal
from ..models.audit_event import AuditEvent
from ..models.violation import PolicyViolation

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Writes immutable audit events for every governance decision.
    Uses a background asyncio queue.
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None

    async def start(self):
        """Start the background worker."""
        if not self.worker_task:
            self.worker_task = asyncio.create_task(self._worker())

    async def stop(self):
        """Stop the background worker and flush queue."""
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
            # Process remaining items
            while not self.queue.empty():
                event = self.queue.get_nowait()
                await self._write_to_db(event)

    async def _worker(self):
        while True:
            try:
                event = await self.queue.get()
                await self._write_to_db(event)
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error writing audit event: {e}")

    async def _write_to_db(self, event: AuditEventSchema):
        async with AsyncSessionLocal() as session:
            try:
                db_event = AuditEvent(
                    event_id=event.event_id,
                    timestamp=event.timestamp,
                    agent_id=event.agent_id,
                    decision=event.decision,
                    matched_policies=event.matched_policies,
                    violations=[v.model_dump() for v in event.violations],
                    payload_hash=event.payload_hash,
                    context_metadata=event.context_metadata,
                    latency_ms=event.latency_ms
                )
                session.add(db_event)

                # Also normalize violations for querying if needed, but JSON column is enough for v0.1

                await session.commit()
            except Exception as e:
                logger.error(f"DB insertion failed for audit event {event.event_id}: {e}")
                await session.rollback()

    async def log(self, event: AuditEventSchema) -> None:
        """Enqueue an event to be logged asynchronously."""
        if not self.worker_task:
            await self.start()
        await self.queue.put(event)

    async def query(self, filters: AuditQueryFilters) -> List[AuditEventSchema]:
        """Query audit events from the DB."""
        from sqlalchemy import select, desc

        async with AsyncSessionLocal() as session:
            query = select(AuditEvent).order_by(desc(AuditEvent.timestamp))

            if filters.agent_id:
                query = query.where(AuditEvent.agent_id == filters.agent_id)
            if filters.decision:
                query = query.where(AuditEvent.decision == filters.decision)

            query = query.limit(filters.limit)
            if filters.cursor:
                query = query.offset(filters.cursor)

            result = await session.execute(query)
            db_events = result.scalars().all()

            return [
                AuditEventSchema(
                    event_id=e.event_id,
                    timestamp=e.timestamp,
                    agent_id=e.agent_id,
                    decision=e.decision,
                    matched_policies=e.matched_policies,
                    violations=e.violations,
                    payload_hash=e.payload_hash,
                    context_metadata=e.context_metadata,
                    latency_ms=e.latency_ms
                ) for e in db_events
            ]

    async def export_ndjson(self, filters: AuditQueryFilters) -> AsyncIterator[str]:
        """Stream NDJSON export."""
        events = await self.query(filters)
        for event in events:
            yield event.model_dump_json() + "\n"

    async def get_summary(self) -> AuditSummary:
        """Get aggregate stats."""
        # Simplified for v0.1: doing it in memory. In prod, use SQL GROUP BY
        from sqlalchemy import select
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(AuditEvent))
            events = result.scalars().all()

            decisions = {}
            agent_counts = {}
            for e in events:
                decisions[e.decision] = decisions.get(e.decision, 0) + 1
                if e.decision == "DENY":
                    agent_counts[e.agent_id] = agent_counts.get(e.agent_id, 0) + 1

            top_violating = [{"agent_id": k, "violations": v} for k, v in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]]

            return AuditSummary(
                total_events=len(events),
                decisions_breakdown=decisions,
                top_violating_agents=top_violating
            )
