"""
backend/app/routers/amcs.py
API endpoints for Krone Annual Maintenance Contracts (AMCs).
"""
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from typing import Dict, Any, List, Optional
from app.models.schemas import AMCDetail, AMCsListResponse
from app.services.sync_service import SyncService

router = APIRouter()


def get_sync_service(request: Request) -> SyncService:
    return request.app.state.sync_service


@router.get("", response_model=List[AMCDetail])
async def list_amcs(
    status: Optional[str] = Query(None),
    customer: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sync_service: SyncService = Depends(get_sync_service)
) -> List[Dict[str, Any]]:
    """Returns all 11 authentic Krone AMCs parsed from Fieldy records."""
    amcs = sync_service.get_all_amcs()
    if status and status.upper() != "ALL":
        amcs = [a for a in amcs if a.get("status", "").lower() == status.lower()]
    if customer:
        c_lower = customer.lower()
        amcs = [a for a in amcs if c_lower in a.get("customer", "").lower()]
    if search:
        s_lower = search.lower()
        amcs = [
            a for a in amcs
            if s_lower in a.get("title", "").lower()
            or s_lower in a.get("amc_id", "").lower()
            or s_lower in a.get("customer", "").lower()
        ]
    return amcs


@router.get("/{amc_id}", response_model=AMCDetail)
async def get_amc(
    amc_id: str,
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """Returns detailed terms and asset quotas for a specific AMC."""
    amc = sync_service.get_amc_by_id(amc_id)
    if not amc:
        raise HTTPException(status_code=404, detail=f"AMC '{amc_id}' not found in Fieldy contract database.")
    return amc
