"""
backend/tests/test_amcs_audit_automations.py
Unit & integration tests for AMCs, 12-Pillar Forensic Bill Audits, WhatsApp/Email Automations, and Security Hardening.
"""
import pytest
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_amcs_success():
    """Verify GET /api/amcs returns authentic AMCs."""
    resp = client.get("/api/amcs")
    assert resp.status_code == 200
    amcs = resp.json()
    assert len(amcs) >= 10
    first = amcs[0]
    assert "amc_id" in first
    assert "title" in first
    assert "customer" in first
    assert "total_value" in first
    assert first["total_value"] > 0


def test_amc_filtering_by_customer():
    """Verify AMC search and customer filtering."""
    resp = client.get("/api/amcs?customer=RIL")
    assert resp.status_code == 200
    amcs = resp.json()
    assert len(amcs) > 0
    assert all("RIL" in a["customer"] for a in amcs)


def test_forensic_audit_valid_local_claim():
    """Verify 12-pillar audit approves compliant local conveyance (<50 KM, >=8h duty)."""
    payload = {
        "technician_id": "TECH-01",
        "technician_name": "Sunny Kumar",
        "date": "2026-10-02",
        "claimed_km": 35.0,
        "vehicle_type": "bike",
        "claimed_da": 150.0,
        "claimed_hotel": 0.0,
        "stay_provided_by_client": False,
        "duty_hours": 8.5,
        "job_id": "SR-26- 0148",
        "trip_purpose": "Bellima Baler Knotter Inspection"
    }
    resp = client.post("/api/audit/check-bill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "APPROVED"
    assert data["classification"] == "LOCAL_CONVEYANCE"
    assert data["admissible_km"] == 35.0
    assert data["disallowed_km"] == 0.0
    assert data["total_disallowed_recovery"] == 0.0
    assert data["total_admissible_amount"] == (35.0 * 5.0) + 150.0


def test_forensic_audit_catches_local_outstation_da_fraud():
    """Verify audit disallows excess DA when outstation rate is claimed on local trip."""
    payload = {
        "technician_id": "TECH-02",
        "technician_name": "Sukhdeep Singh",
        "date": "2026-10-02",
        "claimed_km": 40.0,
        "vehicle_type": "bike",
        "claimed_da": 300.0,  # Claimed outstation DA on local trip
        "claimed_hotel": 0.0,
        "stay_provided_by_client": False,
        "duty_hours": 8.0,
        "job_id": "SR-26- 0140"
    }
    resp = client.post("/api/audit/check-bill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "FLAGGED_PARTIAL_APPROVAL"
    assert data["disallowed_da"] == 150.0  # Excess ₹150 disallowed
    assert data["admissible_da"] == 150.0
    assert data["total_disallowed_recovery"] >= 150.0


def test_forensic_audit_catches_guest_house_double_claim():
    """Verify audit disallows hotel claim when client provided guest house."""
    payload = {
        "technician_id": "TECH-09",
        "technician_name": "Vishnu",
        "date": "2026-10-01",
        "claimed_km": 120.0,
        "vehicle_type": "bike",
        "claimed_da": 300.0,
        "claimed_hotel": 1500.0,  # Claimed hotel while RIL guest house was provided
        "stay_provided_by_client": True,
        "duty_hours": 9.0,
        "job_id": "SR-26- 0149"
    }
    resp = client.post("/api/audit/check-bill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["verdict"] == "FLAGGED_PARTIAL_APPROVAL"
    assert data["disallowed_hotel"] == 1500.0  # Fully disallowed!
    assert data["admissible_hotel"] == 0.0
    assert data["total_disallowed_recovery"] >= 1500.0


def test_forensic_audit_catches_inflated_km():
    """Verify audit disallows inflated KM claims exceeding GPS corridor ceiling."""
    payload = {
        "technician_id": "TECH-04",
        "technician_name": "Sunder",
        "date": "2026-10-02",
        "claimed_km": 95.0,  # Benchmark for SR-26- 0122 is 26km (x2=52km max ~60km)
        "vehicle_type": "bike",
        "claimed_da": 150.0,
        "claimed_hotel": 0.0,
        "stay_provided_by_client": False,
        "duty_hours": 8.5,
        "job_id": "SR-26- 0122"
    }
    resp = client.post("/api/audit/check-bill", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["disallowed_km"] > 0.0
    assert data["total_disallowed_recovery"] > 0.0


def test_whatsapp_dispatch_automation():
    """Verify WhatsApp work order dispatch formatting."""
    payload = {
        "job_id": "SR-26- 0148",
        "recipient_phone": "+91 9625957663",
        "recipient_name": "Sunny Kumar",
        "recipient_role": "technician"
    }
    resp = client.post("/api/automations/whatsapp/dispatch", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "DELIVERED"
    assert "KRONE AGRICULTURE INDIA" in data["formatted_body"]
    assert "SR-26- 0148" in data["formatted_body"]


def test_email_report_automation():
    """Verify email report dispatch."""
    payload = {
        "recipient_email": "kin.it@krone-india.com",
        "report_type": "service_job_card",
        "subject": "Krone Work Order Service Report — SR-26- 0148",
        "job_id": "SR-26- 0148"
    }
    resp = client.post("/api/automations/email/send-report", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SENT"


def test_security_audit_endpoint():
    """Verify system security audit reports AAA rating and active hardening."""
    resp = client.get("/api/security/audit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SECURE"
    assert data["overall_rating"] == "ENTERPRISE_GRADE_AAA"
    assert "cors_hardening" in data["checks"]
    assert "rate_limiting" in data["checks"]
    assert "bill_fraud_detector" in data["checks"]
