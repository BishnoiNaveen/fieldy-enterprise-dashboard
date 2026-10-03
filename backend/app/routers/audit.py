"""
backend/app/routers/audit.py
API endpoints for 12-Pillar Forensic Bill & KM Claim Auditing.
"""
from fastapi import APIRouter, Depends, Request
from typing import Dict, Any, List
from app.models.schemas import BillAuditRequest, BillAuditResponse
from app.services.audit_engine import ForensicAuditEngine

router = APIRouter()


def get_audit_engine(request: Request) -> ForensicAuditEngine:
    if not hasattr(request.app.state, "audit_engine"):
        request.app.state.audit_engine = ForensicAuditEngine()
    return request.app.state.audit_engine


@router.post("/check-bill", response_model=BillAuditResponse)
async def check_technician_bill(
    req: BillAuditRequest,
    engine: ForensicAuditEngine = Depends(get_audit_engine)
) -> BillAuditResponse:
    """Executes statutory 12-pillar forensic audit on technician travel/conveyance claim."""
    return engine.perform_audit(req)


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_audit_history(
    engine: ForensicAuditEngine = Depends(get_audit_engine)
) -> List[Dict[str, Any]]:
    """Returns recent forensic audit outcomes with financial disallowances and recoveries."""
    return engine.get_history()
