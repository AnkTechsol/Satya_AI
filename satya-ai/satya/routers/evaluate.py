from fastapi import APIRouter, Depends, HTTPException, Request
from ..schemas.evaluate import EvaluateRequest, EvaluateResult
from ..core.policy_engine import PolicyEngine
from ..core.audit_logger import AuditLogger
from ..core.agent_registry import AgentRegistry
from ..schemas.audit import AuditEventSchema
from ..utils.hashing import hash_payload
from ..core.interceptor import verify_satya_key
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["Evaluate"], dependencies=[Depends(verify_satya_key)])
registry = AgentRegistry()
engine = PolicyEngine(registry)

@router.post("/evaluate", response_model=EvaluateResult)
async def evaluate(request: Request, eval_req: EvaluateRequest):
    # We retrieve the audit_logger instance from app state so it persists
    audit_logger: AuditLogger = request.app.state.audit_logger

    try:
        result = await engine.evaluate(
            agent_id=eval_req.agent_id,
            payload=eval_req.payload,
            context=eval_req.context
        )

        # Construct audit event
        from datetime import datetime, timezone
        audit_event = AuditEventSchema(
            event_id=result.event_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            agent_id=eval_req.agent_id,
            decision=result.decision,
            matched_policies=result.matched_policies,
            violations=result.violations or [],
            payload_hash=hash_payload(json.dumps(eval_req.payload)),
            context_metadata=eval_req.context or {},
            latency_ms=result.latency_ms
        )

        # Log asynchronously
        await audit_logger.log(audit_event)

        # If DENY, return 403 Forbidden with details, per acceptance criteria
        if result.decision == "DENY":
            # FastAPI HTTPException can take custom detail objects or we can use JSONResponse directly
            # For exact matching of schema but 403 status:
            from fastapi.responses import JSONResponse
            from fastapi.encoders import jsonable_encoder
            return JSONResponse(status_code=403, content=jsonable_encoder(result))

        return result

    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
