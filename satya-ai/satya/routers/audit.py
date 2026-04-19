from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from ..core.audit_logger import AuditLogger
from ..schemas.audit import AuditEventSchema, AuditQueryFilters, AuditSummary
from ..core.interceptor import verify_satya_key

router = APIRouter(prefix="/v1/audit", tags=["Audit"], dependencies=[Depends(verify_satya_key)])
audit_logger = AuditLogger()

@router.get("/events", response_model=List[AuditEventSchema])
async def get_events(
    agent_id: Optional[str] = None,
    decision: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    cursor: Optional[int] = None
):
    filters = AuditQueryFilters(
        agent_id=agent_id,
        decision=decision,
        severity=severity,
        limit=limit,
        cursor=cursor
    )
    return await audit_logger.query(filters)

@router.get("/export")
async def export_events(
    agent_id: Optional[str] = None,
    decision: Optional[str] = None
):
    filters = AuditQueryFilters(agent_id=agent_id, decision=decision, limit=10000)
    return StreamingResponse(
        audit_logger.export_ndjson(filters),
        media_type="application/x-ndjson"
    )

@router.get("/summary", response_model=AuditSummary)
async def get_summary():
    return await audit_logger.get_summary()
