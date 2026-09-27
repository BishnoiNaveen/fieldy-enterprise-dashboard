"""
backend/app/routers/analytics.py
Productivity & Hours Analytics Router for Daily, Weekly, and Monthly rollups.
"""
from fastapi import APIRouter, Depends, Query, Request
from typing import Dict, Any, Optional
from app.models.schemas import ProductivityResponse
from app.services.analytics_engine import AnalyticsEngine
from app.services.sync_service import SyncService

router = APIRouter()


def get_analytics_engine() -> AnalyticsEngine:
    return AnalyticsEngine()


def get_sync_service(request: Request) -> SyncService:
    return request.app.state.sync_service


@router.get("/productivity", response_model=ProductivityResponse)
async def get_productivity_analytics(
    timeframe: str = Query("daily", pattern="^(daily|weekly|monthly)$"),
    technician_id: Optional[str] = Query(None),
    customer_company: Optional[str] = Query(None),
    job_status: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    engine: AnalyticsEngine = Depends(get_analytics_engine),
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """
    Aggregates technician working, travelling, and idle hours strictly preserving H_shift = H_w + H_t + H_i.
    """
    shifts = sync_service.get_daily_shifts()
    jobs = sync_service.get_all_jobs()

    return engine.aggregate_productivity(
        daily_shift_records=shifts,
        jobs_records=jobs,
        timeframe=timeframe,
        technician_id=technician_id,
        customer_company=customer_company,
        job_status=job_status,
        job_type=job_type,
        start_date=start_date,
        end_date=end_date
    )
