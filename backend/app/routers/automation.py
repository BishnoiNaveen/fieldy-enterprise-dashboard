"""
backend/app/routers/automation.py
API endpoints for WhatsApp Business API dispatch, email notifications, and webhook status.
"""
from fastapi import APIRouter, Depends, Request
from typing import Dict, Any
from app.models.schemas import (
    WhatsAppDispatchRequest,
    WhatsAppDispatchResponse,
    EmailReportRequest,
    EmailReportResponse
)
from app.services.automation_service import AutomationService
from app.services.sync_service import SyncService

router = APIRouter()


def get_automation_service(request: Request) -> AutomationService:
    if not hasattr(request.app.state, "automation_service"):
        request.app.state.automation_service = AutomationService()
    return request.app.state.automation_service


def get_sync_service(request: Request) -> SyncService:
    return request.app.state.sync_service


@router.post("/whatsapp/dispatch", response_model=WhatsAppDispatchResponse)
async def dispatch_whatsapp(
    req: WhatsAppDispatchRequest,
    service: AutomationService = Depends(get_automation_service),
    sync: SyncService = Depends(get_sync_service)
) -> WhatsAppDispatchResponse:
    """Dispatches formatted WhatsApp Business message to technician or customer."""
    jobs = sync.get_all_jobs()
    job_meta = next((j for j in jobs if j.get("job_id") == req.job_id), None)
    return service.dispatch_whatsapp_message(req, job_meta)


@router.post("/email/send-report", response_model=EmailReportResponse)
async def send_email_report(
    req: EmailReportRequest,
    service: AutomationService = Depends(get_automation_service)
) -> EmailReportResponse:
    """Sends service reports or forensic audit recovery reports via email."""
    return service.dispatch_email_report(req)


@router.get("/status")
async def get_automation_status(
    service: AutomationService = Depends(get_automation_service)
) -> Dict[str, Any]:
    """Returns status and metrics for all automation messaging channels."""
    return service.get_automation_status()
