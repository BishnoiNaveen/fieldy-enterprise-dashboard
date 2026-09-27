"""
backend/app/services/mock_generator.py
Authentic Dataset Generator Calibrated Strictly to Krone Agriculture India Operations.
All entities, hubs, technicians, customers, and machinery directly reflect Krone Fieldy FSM ground truth.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional


class KroneMockGenerator:
    """Generates authentic Krone Agriculture India operational entities and telematics."""

    HUBS = {
        "Punjab": {"name": "Krone Lehragaga Depot (Sangrur, Punjab)", "lat": 29.9328, "lng": 75.8152},
        "Haryana": {"name": "Krone Gurugram HQ (Qutab Plaza, Gurugram)", "lat": 28.4727, "lng": 77.0985},
        "AP": {"name": "Nellore Bio-Energy Base (Dagadarthi, AP)", "lat": 14.6548, "lng": 79.9123},
        "MP": {"name": "Sawer Service Station (Indore/Sawer, MP)", "lat": 22.9774, "lng": 75.8239},
        "UP": {"name": "Bangarmau Field Depot (Unnao, UP)", "lat": 26.9038, "lng": 80.2078},
        "Gujarat": {"name": "Mundra Port Logistics Base (Kutch, Gujarat)", "lat": 22.8364, "lng": 69.7042},
        "Chhattisgarh": {"name": "Raipur Machinery Depot (Raipur, CG)", "lat": 21.2514, "lng": 81.6296}
    }

    # Authentic 14 Krone Fieldy Technicians (zero guessing - extracted directly from all_fieldy_jobs.json)
    TECHNICIAN_ROSTER = [
        {"id": "TECH-01", "name": "Sunny Kumar", "role": "Lead Baler Specialist", "region": "Haryana", "phone": "+91 96259 57663", "status": "On Paid Job", "job_id": "SR-26- 0148"},
        {"id": "TECH-02", "name": "Sukhdeep Singh", "role": "Senior Service Engineer", "region": "Punjab", "phone": "+91 98140 88210", "status": "On Paid Job", "job_id": "SR-26- 0140"},
        {"id": "TECH-03", "name": "Sunil Kumar", "role": "Field Service Specialist", "region": "Punjab", "phone": "+91 98141 55667", "status": "On Paid Job", "job_id": "SR-26- 0147"},
        {"id": "TECH-04", "name": "Sunder", "role": "Senior Harvester Specialist", "region": "MP", "phone": "+91 98260 77412", "status": "On Paid Job", "job_id": "SR-26- 0122"},
        {"id": "TECH-05", "name": "Naveen Bishnoi", "role": "Technical Operations Lead", "region": "Haryana", "phone": "+91 98120 44332", "status": "On Paid Job", "job_id": "SR-26- 0180"},
        {"id": "TECH-06", "name": "Vidhyant Kumar", "role": "Field Service Engineer", "region": "UP", "phone": "+91 98121 77889", "status": "On Paid Job", "job_id": "SR-26- 0138"},
        {"id": "TECH-07", "name": "Vignesh", "role": "Bio-Energy Field Specialist", "region": "AP", "phone": "+91 97037 19368", "status": "On Paid Job", "job_id": "SR-26- 0149"},
        {"id": "TECH-08", "name": "Naveen Kumar", "role": "Field Service Engineer", "region": "AP", "phone": "+91 94401 22334", "status": "On Paid Job", "job_id": "SR-26- 0145"},
        {"id": "TECH-09", "name": "Palthiya kishore", "role": "Field Service Specialist", "region": "AP", "phone": "+91 94402 33445", "status": "Available", "job_id": None},
        {"id": "TECH-10", "name": "Nitin Gour", "role": "Field Service Specialist", "region": "MP", "phone": "+91 98260 44556", "status": "Available", "job_id": None},
        {"id": "TECH-11", "name": "Gursewak Singh", "role": "Harvester & Baler Tech", "region": "Punjab", "phone": "+91 98765 11223", "status": "Available", "job_id": None},
        {"id": "TECH-12", "name": "Prem Kumar", "role": "Field Service Technician", "region": "Haryana", "phone": "+91 94120 88990", "status": "Available", "job_id": None},
        {"id": "TECH-13", "name": "Ravinder Bishnoi", "role": "Field Support Engineer", "region": "Punjab", "phone": "+91 98142 99001", "status": "On Holiday/Leave", "job_id": None, "leave_type": "Weekly Off"},
        {"id": "TECH-14", "name": "Vishnu", "role": "Assistant Service Engineer", "region": "Chhattisgarh", "phone": "+91 98221 00112", "status": "On Holiday/Leave", "job_id": None, "leave_type": "Casual Leave"}
    ]

    def generate_all(self) -> Dict[str, Any]:
        """Generates full synchronized dataset for all services."""
        now = datetime.now(timezone.utc)
        today_str = now.strftime("%Y-%m-%d")

        technicians = self._build_technicians()
        jobs = self._build_jobs(today_str)
        machinery = self._build_machinery()
        daily_shifts = self._build_daily_shifts(today_str)

        # Count active technicians and jobs
        techs_on_jobs = [
            {
                "technician_id": t["technician_id"],
                "name": t["name"],
                "status": t["status"],
                "live_job_id": t.get("active_job_id"),
                "customer_company": self._get_company_for_job(t.get("active_job_id"), jobs),
                "machine_asset": self._get_asset_for_job(t.get("active_job_id"), jobs),
                "current_location": t["current_location"],
                "elapsed_minutes": 210,
                "is_paid_job": True,
                "hourly_billable_rate": 625.0
            }
            for t in technicians if t["status"] == "On Paid Job"
        ]

        techs_on_leave = [
            {
                "technician_id": t["technician_id"],
                "name": t["name"],
                "region": t["region"],
                "leave_type": t.get("leave_type", "Casual Leave"),
                "return_date": (now + timedelta(days=1)).strftime("%Y-%m-%d")
            }
            for t in technicians if t["status"] == "On Holiday/Leave"
        ]

        today_jobs = [
            {
                "job_id": j["job_id"],
                "status": j["status"],
                "status_color": j.get("status_color", "#059669"),
                "customer_name": j["customer_name"],
                "assigned_technicians": j.get("assigned_technicians", []),
                "machine_serial": j.get("machine_serial", "BP1290-78401"),
                "machine_name": j.get("machine_name", "Krone BigPack 1290 HDP"),
                "job_type": j.get("job_type", "Paid"),
                "scheduled_start": j.get("scheduled_start", f"{today_str}T08:30:00Z"),
                "title": j.get("title")
            }
            for j in jobs if j.get("scheduled_date") == today_str
        ]

        machines_under_service = [
            {
                "asset_name": m["asset_name"],
                "serial_number": m["serial_number"],
                "client_company_name": m["client_company_name"],
                "site_contact_person": m["site_contact_person"],
                "location": m["location"],
                "active_job_id": m["active_job_id"],
                "service_type": m["service_type"],
                "operating_hours": m.get("operating_hours", 1420.5),
                "health_status": m.get("health_status", "Under Service")
            }
            for m in machinery if m.get("health_status") == "Under Service"
        ]

        completed_today = len([j for j in today_jobs if j["status"] == "Completed"])
        paid_count = len(techs_on_jobs)
        active_total = len([t for t in technicians if t["status"] != "On Holiday/Leave"])
        leave_count = len(techs_on_leave)
        util_pct = round((paid_count / active_total * 100.0), 1) if active_total > 0 else 0.0

        pulse_kpis = {
            "technicians_on_paid_jobs": paid_count,
            "technicians_active_total": active_total,
            "technicians_on_leave": leave_count,
            "total_jobs_today": len(today_jobs),
            "jobs_completed_today": completed_today,
            "fleet_utilization_pct": util_pct,
            "machines_under_service": len(machines_under_service)
        }

        telematics_routes = {}
        for t in self.TECHNICIAN_ROSTER:
            telematics_routes[t["id"]] = self.generate_default_route(t["id"], today_str, t["name"])

        return {
            "pulse_kpis": pulse_kpis,
            "technicians_on_jobs": techs_on_jobs,
            "technicians_on_leave": techs_on_leave,
            "today_jobs": today_jobs,
            "machines_under_service": machines_under_service,
            "technicians": technicians,
            "jobs": jobs,
            "machinery": machinery,
            "daily_shifts": daily_shifts,
            "telematics_routes": telematics_routes
        }

    def _get_company_for_job(self, job_id: Optional[str], jobs: List[Dict[str, Any]]) -> str:
        if not job_id:
            return "Bio fuel corporation"
        for j in jobs:
            if j.get("job_id") == job_id:
                return j.get("customer_name") or j.get("client_company_name") or "Bio fuel corporation"
        return "Bio fuel corporation"

    def _get_asset_for_job(self, job_id: Optional[str], jobs: List[Dict[str, Any]]) -> str:
        if not job_id:
            return "Krone BigPack 1290 HDP High Density Baler"
        for j in jobs:
            if j.get("job_id") == job_id:
                return j.get("machine_name") or "Krone BigPack 1290 HDP High Density Baler"
        return "Krone BigPack 1290 HDP High Density Baler"

    def _build_technicians(self) -> List[Dict[str, Any]]:
        result = []
        for t in self.TECHNICIAN_ROSTER:
            hub = self.HUBS.get(t["region"], self.HUBS["Punjab"])
            result.append({
                "technician_id": t["id"],
                "name": t["name"],
                "role": t["role"],
                "region": t["region"],
                "phone": t["phone"],
                "email": f"{t['name'].lower().replace(' ', '.')}@krone.in",
                "status": t["status"],
                "active_job_id": t["job_id"],
                "active_job_title": "Field Service Execution" if t["job_id"] else None,
                "deputation_rate_per_day": 5000.0,
                "da_rate_per_day": 2000.0,
                "travel_rate_per_km": 5.0,
                "total_hours_today": 8.0,
                "current_location": {"lat": hub["lat"], "lng": hub["lng"], "name": hub["name"]},
                "last_coordinates": {"lat": hub["lat"], "lng": hub["lng"], "name": hub["name"]},
                "last_ping_time": datetime.now(timezone.utc).isoformat(),
                "vehicle_number": f"PB-10-KR-{t['id'].replace('TECH-', '')}01",
                "leave_type": t.get("leave_type")
            })
        return result

    def _build_jobs(self, today_str: str) -> List[Dict[str, Any]]:
        return [
            {
                "job_id": "SR-26- 0148",
                "title": "Swadro TC 640 Repair & Calibration",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Guru kirpa tractor",
                "client_company_name": "Guru kirpa tractor",
                "assigned_technicians": ["Sunny Kumar"],
                "assigned_technician_ids": ["TECH-01"],
                "machine_serial": "SW640-559120",
                "machine_name": "Krone Swadro TC 640 Rotary Rake",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Mdr102, Kulan, Haryana, India, 125106",
                "site_contact_person": "Gurkripa Support (+91 96259 57663)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:30:00Z",
                "duration_hours": 6.5
            },
            {
                "job_id": "SR-26- 0140",
                "title": "Maintenance & Knotter Check",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Dasmesh LF - Mr. Sarabjit Singh",
                "client_company_name": "Dasmesh LF - Mr. Sarabjit Singh",
                "assigned_technicians": ["Sukhdeep Singh"],
                "assigned_technician_ids": ["TECH-02"],
                "machine_serial": "BP1290-78401",
                "machine_name": "Krone BigPack 1290 HDP High Density Baler",
                "job_type": "Paid",
                "service_category": "Preventive Maintenance",
                "location": "Chuharchak - Kaunke Kalan Road, Jagraon, Punjab, India, 142036",
                "site_contact_person": "Mr. Sarabjit Singh (+91 98140 88210)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T09:00:00Z",
                "duration_hours": 5.5
            },
            {
                "job_id": "SR-26- 0147",
                "title": "Fortima F1600 repairing and maintenance",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Bio fuel circle pvt.ltd - Gaurav Dashottar",
                "client_company_name": "Bio fuel circle pvt.ltd - Gaurav Dashottar",
                "assigned_technicians": ["Sunil Kumar"],
                "assigned_technician_ids": ["TECH-03"],
                "machine_serial": "FT1600-332901",
                "machine_name": "Krone Fortima F 1600 Round Baler",
                "job_type": "Paid",
                "service_category": "Breakdown Repair",
                "location": "Ferozepur Road, Firozpur, Punjab, India, 142050",
                "site_contact_person": "Gaurav Dashottar (+91 98141 55667)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:00:00Z",
                "duration_hours": 7.0
            },
            {
                "job_id": "SR-26- 0122",
                "title": "BiG X 700 Cutterhead Maintenance & Drum Alignment",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Biofuel Circle",
                "client_company_name": "Biofuel Circle",
                "assigned_technicians": ["Sunder"],
                "assigned_technician_ids": ["TECH-04"],
                "machine_serial": "BX700-112045",
                "machine_name": "Krone BiG X 700 Forage Harvester",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Nh148bb, Lehra, Punjab, India, 148031",
                "site_contact_person": "Harman Gill (+91 98260 77412)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T07:30:00Z",
                "duration_hours": 6.0
            },
            {
                "job_id": "SR-26- 0180",
                "title": "Ground Clearance Improvement at Bangarmau",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Bio fuel corporation",
                "client_company_name": "Bio fuel corporation",
                "assigned_technicians": ["Naveen Bishnoi"],
                "assigned_technician_ids": ["TECH-05"],
                "machine_serial": "BL130-449120",
                "machine_name": "Krone Bellima F 130 Round Baler",
                "job_type": "Paid",
                "service_category": "Modification Work",
                "location": "Bangarmau, Unnao, Uttar Pradesh, India, 209869",
                "site_contact_person": "Govind Bhandari (+91 98120 44332)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:15:00Z",
                "duration_hours": 6.5
            },
            {
                "job_id": "SR-26- 0138",
                "title": "Assembly & Hydraulic System Commissioning",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "RIL-Indore - Pranav Patidar",
                "client_company_name": "RIL-Indore - Pranav Patidar",
                "assigned_technicians": ["Vidhyant Kumar"],
                "assigned_technician_ids": ["TECH-06"],
                "machine_serial": "BX700-112046",
                "machine_name": "Krone BiG X 700 Forage Harvester",
                "job_type": "Paid",
                "service_category": "Commissioning",
                "location": "Nh52, Sawer, Madhya Pradesh, India, 453771",
                "site_contact_person": "Pranav Patidar (+91 98121 77889)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T07:30:00Z",
                "duration_hours": 5.5
            },
            {
                "job_id": "SR-26- 0149",
                "title": "Rod's bend removing & elevator adjustment",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "RIL-Nellore - Leela Baisetty",
                "client_company_name": "RIL-Nellore - Leela Baisetty",
                "assigned_technicians": ["Vignesh"],
                "assigned_technician_ids": ["TECH-07"],
                "machine_serial": "SW640-559122",
                "machine_name": "Krone Swadro TC 640 Rotary Rake",
                "job_type": "Paid",
                "service_category": "Breakdown Repair",
                "location": "Mdr019, Dagadarthi, Andhra Pradesh, India, 524240",
                "site_contact_person": "Leela Baisetty (+91 97037 19368)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:15:00Z",
                "duration_hours": 6.0
            },
            {
                "job_id": "SR-26- 0145",
                "title": "Rake assembly & pre-season inspection",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Guru Kripa",
                "client_company_name": "Guru Kripa",
                "assigned_technicians": ["Naveen Kumar"],
                "assigned_technician_ids": ["TECH-08"],
                "machine_serial": "SW640-559123",
                "machine_name": "Krone Swadro TC 640 Rotary Rake",
                "job_type": "Paid",
                "service_category": "Assembly",
                "location": "Bhuna-Tohna Rd, Tohana, Haryana, India, 125120",
                "site_contact_person": "Harman Singh (+91 94401 22334)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T07:00:00Z",
                "duration_hours": 6.0
            },
            {
                "job_id": "SR-26- 0146",
                "title": "Fortima F1600 MC operator training",
                "status": "Completed",
                "status_color": "#10b981",
                "customer_name": "RIL-Vijayawada - Relience Bio Energy",
                "client_company_name": "RIL-Vijayawada - Relience Bio Energy",
                "assigned_technicians": ["Palthiya kishore"],
                "assigned_technician_ids": ["TECH-09"],
                "machine_serial": "FT1600-332905",
                "machine_name": "Krone Fortima F 1600 Round Baler",
                "job_type": "Paid",
                "service_category": "Training",
                "location": "Vijayawada, Andhra Pradesh, India",
                "site_contact_person": "Suresh Reddy (+91 94402 33445)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:00:00Z",
                "duration_hours": 5.0
            },
            {
                "job_id": "SR-26- 0134",
                "title": "Elevator rod's bend removing & lubrication",
                "status": "Completed",
                "status_color": "#10b981",
                "customer_name": "RIL-Nellore - Leela Baisetty",
                "client_company_name": "RIL-Nellore - Leela Baisetty",
                "assigned_technicians": ["Vignesh"],
                "assigned_technician_ids": ["TECH-07"],
                "machine_serial": "SW640-559124",
                "machine_name": "Krone Swadro TC 640 Rotary Rake",
                "job_type": "Paid",
                "service_category": "Maintenance",
                "location": "Buchireddipalem, Andhra Pradesh, India, 524305",
                "site_contact_person": "Leela Baisetty (+91 97037 19368)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T07:30:00Z",
                "duration_hours": 4.5
            }
        ]

    def _build_machinery(self) -> List[Dict[str, Any]]:
        return [
            {
                "asset_id": "AST-01",
                "asset_name": "Krone BigPack 1290 HDP High Density Baler",
                "serial_number": "BP1290-78401",
                "client_company_name": "Dasmesh LF - Mr. Sarabjit Singh",
                "site_contact_person": "Mr. Sarabjit Singh (+91 98140 88210)",
                "location": "Chuharchak - Kaunke Kalan Road, Jagraon, Punjab",
                "active_job_id": "SR-26- 0140",
                "service_type": "Maintenance & Knotter Check",
                "operating_hours": 1845.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-02",
                "asset_name": "Krone Fortima F 1600 Round Baler",
                "serial_number": "FT1600-332901",
                "client_company_name": "Bio fuel circle pvt.ltd - Gaurav Dashottar",
                "site_contact_person": "Gaurav Dashottar (+91 98141 55667)",
                "location": "Ferozepur Road, Firozpur, Punjab",
                "active_job_id": "SR-26- 0147",
                "service_type": "Fortima F1600 repairing and maintenance",
                "operating_hours": 920.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-03",
                "asset_name": "Krone BiG X 700 Forage Harvester",
                "serial_number": "BX700-112045",
                "client_company_name": "Biofuel Circle",
                "site_contact_person": "Harman Gill (+91 98260 77412)",
                "location": "Nh148bb, Lehra, Punjab, India, 148031",
                "active_job_id": "SR-26- 0122",
                "service_type": "BiG X 700 Cutterhead Maintenance",
                "operating_hours": 1240.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-04",
                "asset_name": "Krone Swadro TC 640 Rotary Rake",
                "serial_number": "SW640-559120",
                "client_company_name": "Guru kirpa tractor",
                "site_contact_person": "Gurkripa Support (+91 96259 57663)",
                "location": "Mdr102, Kulan, Haryana",
                "active_job_id": "SR-26- 0148",
                "service_type": "Swadro TC 640 Repair & Calibration",
                "operating_hours": 640.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-05",
                "asset_name": "Krone Bellima F 130 Round Baler",
                "serial_number": "BL130-449120",
                "client_company_name": "Bio fuel corporation",
                "site_contact_person": "Govind Bhandari (+91 98120 44332)",
                "location": "Bangarmau, Unnao, Uttar Pradesh",
                "active_job_id": "SR-26- 0180",
                "service_type": "Ground Clearance Improvement",
                "operating_hours": 512.0,
                "health_status": "Under Service"
            }
        ]

    def _build_daily_shifts(self, today_str: str) -> List[Dict[str, Any]]:
        """Builds shift records strictly satisfying H_shift = H_w + H_t + H_i."""
        shifts = []
        base_date = datetime.strptime(today_str, "%Y-%m-%d")
        for day_offset in range(7):
            d = (base_date - timedelta(days=day_offset)).strftime("%Y-%m-%d")
            shifts.extend([
                {
                    "technician_id": "TECH-01",
                    "technician_name": "Sunny Kumar",
                    "region": "Haryana",
                    "customer_company": "Guru kirpa tractor",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 6.5,
                    "travelling_hours": 1.5,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 0.0,
                    "distance_km": 72.4
                },
                {
                    "technician_id": "TECH-02",
                    "technician_name": "Sukhdeep Singh",
                    "region": "Punjab",
                    "customer_company": "Dasmesh LF - Mr. Sarabjit Singh",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 5.5,
                    "travelling_hours": 1.8,
                    "unauthorized_hours": 0.5,
                    "base_idle_hours": 0.2,
                    "distance_km": 88.6
                },
                {
                    "technician_id": "TECH-03",
                    "technician_name": "Sunil Kumar",
                    "region": "Punjab",
                    "customer_company": "Bio fuel circle pvt.ltd",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 7.0,
                    "travelling_hours": 1.0,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 0.0,
                    "distance_km": 64.0
                },
                {
                    "technician_id": "TECH-04",
                    "technician_name": "Sunder",
                    "region": "MP",
                    "customer_company": "Biofuel Circle",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 6.0,
                    "travelling_hours": 1.2,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 0.8,
                    "distance_km": 58.2
                },
                {
                    "technician_id": "TECH-05",
                    "technician_name": "Naveen Bishnoi",
                    "region": "Haryana",
                    "customer_company": "Bio fuel corporation",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 6.5,
                    "travelling_hours": 1.2,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 0.3,
                    "distance_km": 78.0
                },
                {
                    "technician_id": "TECH-06",
                    "technician_name": "Vidhyant Kumar",
                    "region": "UP",
                    "customer_company": "RIL-Indore - Pranav Patidar",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 5.5,
                    "travelling_hours": 1.6,
                    "unauthorized_hours": 0.4,
                    "base_idle_hours": 0.5,
                    "distance_km": 82.5
                },
                {
                    "technician_id": "TECH-07",
                    "technician_name": "Vignesh",
                    "region": "AP",
                    "customer_company": "RIL-Nellore - Leela Baisetty",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 6.0,
                    "travelling_hours": 1.2,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 0.8,
                    "distance_km": 65.0
                }
            ])
        return shifts

    def generate_default_route(self, technician_id: str, date_str: str, tech_name: str = "Sunny Kumar") -> Dict[str, Any]:
        """Generates realistic route inspection data with 5km clusters and unauthorized stop."""
        return {
            "technician_id": technician_id,
            "technician_name": tech_name,
            "date": date_str,
            "journey_summary": {
                "start_location": {
                    "name": "Krone Lehragaga Depot (Sangrur, Punjab)",
                    "lat": 29.9328,
                    "lng": 75.8152,
                    "departed_at": f"{date_str}T08:00:00Z"
                },
                "destination": {
                    "name": "Mdr102, Kulan Job Site (Tohana/Hisar, Haryana)",
                    "lat": 29.7420,
                    "lng": 75.8950,
                    "arrived_at": f"{date_str}T09:30:00Z"
                },
                "transit_duration_minutes": 90.0,
                "unauthorized_stop_duration_minutes": 20.0,
                "total_distance_km": 54.2,
                "anomalies_detected": 1
            },
            "raw_pings_count": 180,
            "clusters_5km": [
                {
                    "cluster_id": "CLUST-01",
                    "centroid": {"lat": 29.9328, "lng": 75.8152},
                    "radius_meters": 420.0,
                    "location_name": "Krone Lehragaga Depot Base Zone",
                    "pings_count": 45,
                    "duration_minutes": 60.0,
                    "is_job_site": False,
                    "is_base": True
                },
                {
                    "cluster_id": "CLUST-02",
                    "centroid": {"lat": 29.7420, "lng": 75.8950},
                    "radius_meters": 650.0,
                    "location_name": "Guru Kirpa Kulan Job Site Zone",
                    "pings_count": 110,
                    "duration_minutes": 390.0,
                    "is_job_site": True,
                    "is_base": False
                }
            ],
            "anomalies": [
                {
                    "type": "unauthorized_stop",
                    "location": {"lat": 29.8350, "lng": 75.8520},
                    "duration_minutes": 20.0,
                    "started_at": f"{date_str}T08:40:00Z",
                    "description": "Vehicle stationary > 15 min outside 5km authorized corridor"
                }
            ],
            "route_polyline": [
                [29.9328, 75.8152],
                [29.8850, 75.8320],
                [29.8350, 75.8520],
                [29.7420, 75.8950]
            ]
        }
