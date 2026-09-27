"""
backend/app/routers/dashboard.py
Endpoints for Live Operational Pulse, Synchronizer, and Fieldy Cloud API Integration.
"""
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.models.schemas import PulseResponse, SyncRequest, SyncResponse
from app.services.sync_service import SyncService

router = APIRouter()


def get_sync_service(request: Request) -> SyncService:
    return request.app.state.sync_service


class ApiConfigRequest(BaseModel):
    token: Optional[str] = None
    workspace_id: Optional[str] = None
    location_id: Optional[str] = None


@router.get("/pulse", response_model=PulseResponse)
async def get_dashboard_pulse(
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """
    Returns real-time KPIs, active technicians on jobs, machinery under service, and sync metadata.
    """
    return sync_service.get_pulse_data()


@router.post("/sync", response_model=SyncResponse)
async def trigger_sync(
    payload: Optional[SyncRequest] = None,
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """
    Triggers an immediate fresh synchronization with Fieldy FSM cloud or fallback cache.
    """
    force = payload.force_refresh if payload else True
    modules = payload.modules if payload else None
    return await sync_service.trigger_fresh_sync(force_refresh=force, modules=modules)


@router.get("/api-config")
async def get_api_config(
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """
    Returns current Fieldy API connection configuration and live database metrics.
    """
    return sync_service.get_api_config()


@router.post("/api-config")
async def update_api_config(
    payload: ApiConfigRequest,
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """
    Updates Fieldy API Bearer Token and optional workspace/location IDs,
    tests live connection, and executes a fresh synchronization.
    """
    if payload.token:
        # Test connection first
        test_result = await sync_service.test_api_connection(
            token=payload.token,
            workspace_id=payload.workspace_id,
            location_id=payload.location_id
        )
        if test_result.get("connected"):
            sync_service.set_api_credentials(payload.token, payload.workspace_id, payload.location_id)
            sync_res = await sync_service.trigger_fresh_sync(force_refresh=True)
            return {
                "status": "success",
                "message": "Fieldy API connected and live data synchronized successfully!",
                "connection": test_result,
                "sync": sync_res
            }
        else:
            # Even if remote auth failed, store credentials if desired but report error
            sync_service.set_api_credentials(payload.token, payload.workspace_id, payload.location_id)
            return {
                "status": "warning",
                "message": f"Credentials saved, but live connection test failed: {test_result.get('message')}. Dashboard remains active on verified Fieldy database.",
                "connection": test_result
            }

    return {"status": "noop", "message": "No token provided."}


@router.post("/test-connection")
async def test_connection(
    payload: ApiConfigRequest,
    sync_service: SyncService = Depends(get_sync_service)
) -> Dict[str, Any]:
    """
    Tests live connection against api.getfieldy.com without modifying stored state.
    """
    if not payload.token:
        return {"status": "error", "connected": False, "message": "Bearer Token is required for testing."}
    return await sync_service.test_api_connection(
        token=payload.token,
        workspace_id=payload.workspace_id,
        location_id=payload.location_id
    )
