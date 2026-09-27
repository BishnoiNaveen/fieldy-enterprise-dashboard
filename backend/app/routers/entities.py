"""
backend/app/routers/entities.py
Endpoints for querying Technicians and Jobs catalogs.
"""
from fastapi import APIRouter, Depends, Query, Request
from typing import Dict, Any, List, Optional
from app.models.schemas import TechnicianDetail, JobDetail
from app.services.sync_service import SyncService

router = APIRouter()


def get_sync_service(request: Request) -> SyncService:
    return request.app.state.sync_service


@router.get("/technicians", response_model=List[TechnicianDetail])
async def list_technicians(
    status: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sync_service: SyncService = Depends(get_sync_service)
) -> List[Dict[str, Any]]:
    """Returns technicians with operational status and live coordinates."""
    techs = sync_service.get_all_technicians()
    if status and status.upper() != "ALL":
        techs = [t for t in techs if t.get("status", "").lower() == status.lower()]
    if region and region.upper() != "ALL":
        techs = [t for t in techs if t.get("region", "").lower() == region.lower()]
    if search:
        s_lower = search.lower()
        techs = [
            t for t in techs
            if s_lower in t.get("name", "").lower()
            or s_lower in t.get("technician_id", "").lower()
            or s_lower in t.get("region", "").lower()
        ]
    return techs


@router.get("/jobs", response_model=List[JobDetail])
async def list_jobs(
    status: Optional[str] = Query(None),
    customer: Optional[str] = Query(None),
    technician_id: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    sync_service: SyncService = Depends(get_sync_service)
) -> List[Dict[str, Any]]:
    """Returns Fieldy work orders (SR-26-XXXX) with filtering."""
    jobs = sync_service.get_all_jobs()
    if status and status.upper() != "ALL":
        jobs = [j for j in jobs if j.get("status", "").lower() == status.lower()]
    if customer:
        c_lower = customer.lower()
        jobs = [
            j for j in jobs
            if c_lower in j.get("customer_name", "").lower()
            or c_lower in j.get("client_company_name", "").lower()
        ]
    if technician_id:
        jobs = [
            j for j in jobs
            if technician_id in j.get("assigned_technician_ids", [])
            or technician_id in j.get("assigned_technicians", [])
        ]
    if job_type and job_type.upper() != "ALL":
        jobs = [j for j in jobs if j.get("job_type", "").lower() == job_type.lower()]
    return jobs
