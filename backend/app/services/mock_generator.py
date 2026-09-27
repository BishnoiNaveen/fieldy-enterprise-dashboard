"""
backend/app/services/mock_generator.py
Synthetic Dataset Generator Calibrated to Krone Agriculture India Operations.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional


class KroneMockGenerator:
    """Generates authentic Krone Agriculture India operational entities and telematics."""

    HUBS = {
        "Punjab": {"name": "Krone Regional Ag Depot Ludhiana", "lat": 30.9010, "lng": 75.8573},
        "Haryana": {"name": "Krone Service Station Hisar", "lat": 29.1492, "lng": 75.7217},
        "UP": {"name": "Muzaffarnagar Field Support Center", "lat": 29.4727, "lng": 77.7085},
        "Maharashtra": {"name": "Baramati Agro Hub", "lat": 18.1517, "lng": 74.5772},
        "MP": {"name": "Indore Bio-Power Depot", "lat": 22.7196, "lng": 75.8577},
        "Gujarat": {"name": "Jamnagar Clean Energy Base", "lat": 22.4707, "lng": 70.0577},
        "AP": {"name": "Nellore Bio-Gas Service Depot", "lat": 14.4426, "lng": 79.9865}
    }

    TECHNICIAN_ROSTER = [
        {"id": "TECH-01", "name": "Gurpreet Singh", "role": "Lead Baler Specialist", "region": "Punjab", "phone": "+91 98140 88210", "status": "On Paid Job", "job_id": "SR-26-0101"},
        {"id": "TECH-02", "name": "Vikram Sharma", "role": "Senior Service Engineer", "region": "Haryana", "phone": "+91 98120 77412", "status": "On Paid Job", "job_id": "SR-26-0102"},
        {"id": "TECH-03", "name": "Sunny Kumar", "role": "Lead Service Specialist", "region": "Haryana", "phone": "+91 96259 57663", "status": "On Paid Job", "job_id": "SR-26-0103"},
        {"id": "TECH-04", "name": "Jaswinder Singh", "role": "Senior Field Specialist", "region": "Punjab", "phone": "+91 98765 11223", "status": "On Paid Job", "job_id": "SR-26-0104"},
        {"id": "TECH-05", "name": "B. Vignesh", "role": "Bio-Energy Field Specialist", "region": "AP", "phone": "+91 97037 19368", "status": "On Paid Job", "job_id": "SR-26-0105"},
        {"id": "TECH-06", "name": "M. Naveen Kumar", "role": "Field Service Engineer", "region": "AP", "phone": "+91 94401 22334", "status": "On Paid Job", "job_id": "SR-26-0106"},
        {"id": "TECH-07", "name": "Palthiya Kishore", "role": "Field Service Engineer", "region": "AP", "phone": "+91 94402 33445", "status": "On Paid Job", "job_id": "SR-26-0107"},
        {"id": "TECH-08", "name": "Nitin Gour", "role": "Field Technician", "region": "MP", "phone": "+91 98260 44556", "status": "On Paid Job", "job_id": "SR-26-0108"},
        {"id": "TECH-09", "name": "Sunil Kumar", "role": "Field Technician", "region": "Punjab", "phone": "+91 98141 55667", "status": "Available", "job_id": None},
        {"id": "TECH-10", "name": "Sachin Jadhav", "role": "Hydraulics Specialist", "region": "Maharashtra", "phone": "+91 98220 66778", "status": "Available", "job_id": None},
        {"id": "TECH-11", "name": "Vidhyant Kumar", "role": "Field Technician", "region": "Haryana", "phone": "+91 98121 77889", "status": "Available", "job_id": None},
        {"id": "TECH-12", "name": "Prem Kumar", "role": "Field Technician", "region": "UP", "phone": "+91 94120 88990", "status": "Available", "job_id": None},
        {"id": "TECH-13", "name": "Kuldeep Gill", "role": "Field Technician", "region": "Punjab", "phone": "+91 98142 99001", "status": "On Holiday/Leave", "job_id": None, "leave_type": "Casual Leave"},
        {"id": "TECH-14", "name": "Rohit Deshmukh", "role": "Apprentice Technician", "region": "Maharashtra", "phone": "+91 98221 00112", "status": "On Holiday/Leave", "job_id": None, "leave_type": "Weekly Off"}
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
            return "Reliance Industries Limited"
        for j in jobs:
            if j.get("job_id") == job_id:
                return j.get("customer_name") or j.get("client_company_name") or "Reliance Industries Limited"
        return "Reliance Industries Limited"

    def _get_asset_for_job(self, job_id: Optional[str], jobs: List[Dict[str, Any]]) -> str:
        if not job_id:
            return "Krone BigPack 1290 HDP"
        for j in jobs:
            if j.get("job_id") == job_id:
                return j.get("machine_name") or "Krone BigPack 1290 HDP"
        return "Krone BigPack 1290 HDP"

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
                "job_id": "SR-26-0101",
                "title": "Knotter Timing Calibration & Twine Guide Replacement",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Reliance Industries Limited (Bio-Energy Division)",
                "client_company_name": "Reliance Industries Limited (Bio-Energy Division)",
                "assigned_technicians": ["Gurpreet Singh"],
                "assigned_technician_ids": ["TECH-01"],
                "machine_serial": "BP1290-78401",
                "machine_name": "Krone BigPack 1290 HDP High Density Baler",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Ludhiana Bio-Mass Hub, Punjab",
                "site_contact_person": "Rajinder Verma (+91 98765 43210)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:30:00Z",
                "duration_hours": 6.5
            },
            {
                "job_id": "SR-26-0102",
                "title": "Bale Chamber Roller Bearing Service & Tension Calibration",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Punjab State Farm Cooperative Hoshiarpur",
                "client_company_name": "Punjab State Farm Cooperative Hoshiarpur",
                "assigned_technicians": ["Vikram Sharma"],
                "assigned_technician_ids": ["TECH-02"],
                "machine_serial": "FV1500-33901",
                "machine_name": "Krone Fortima V 1500 Round Baler",
                "job_type": "Paid",
                "service_category": "Emergency Repair",
                "location": "Barwala Plant, Hisar, Haryana",
                "site_contact_person": "Sunil Kumar (Plant Head, +91 98123 99881)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T09:00:00Z",
                "duration_hours": 5.5
            },
            {
                "job_id": "SR-26-0103",
                "title": "500-Hour Scheduled Preventive Maintenance & Knife Sharpening",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "VERBIO Bio-Gas India Pvt Ltd (Western UP Plant)",
                "client_company_name": "VERBIO Bio-Gas India Pvt Ltd (Western UP Plant)",
                "assigned_technicians": ["Sunny Kumar"],
                "assigned_technician_ids": ["TECH-03"],
                "machine_serial": "BX6800-45912",
                "machine_name": "Krone BiG X 680 Forage Harvester",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Panipat Grain Silos, Haryana",
                "site_contact_person": "Harish Patel (+91 98221 44556)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:00:00Z",
                "duration_hours": 7.0
            },
            {
                "job_id": "SR-26-0104",
                "title": "Bed Oil Leakage & Cutterbar Disc Inspection",
                "status": "Completed",
                "status_color": "#10b981",
                "customer_name": "SAEL Punjab Biomass Energy Project",
                "client_company_name": "SAEL Punjab Biomass Energy Project",
                "assigned_technicians": ["Jaswinder Singh"],
                "assigned_technician_ids": ["TECH-04"],
                "machine_serial": "EC8700-12845",
                "machine_name": "Krone EasyCut B 870 Mower Conditioner",
                "job_type": "Paid",
                "service_category": "Breakdown Repair",
                "location": "Barnala Bio-Mass Site, Punjab",
                "site_contact_person": "Gurcharan Singh (+91 98765 43213)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T07:30:00Z",
                "duration_hours": 5.0
            },
            {
                "job_id": "SR-26-0105",
                "title": "Bellima Twine Arm Alignment & Hydraulic Cylinder Seal Kit",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Hoshiarpur Bio-Fuels Farm Cluster",
                "client_company_name": "Hoshiarpur Bio-Fuels Farm Cluster",
                "assigned_technicians": ["B. Vignesh"],
                "assigned_technician_ids": ["TECH-05"],
                "machine_serial": "SW8800-98321",
                "machine_name": "Krone Swadro TC 880 Rotary Rake",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Dagadarthi Bio-Mass Plant, Nellore, AP",
                "site_contact_person": "Leela Baisetty (+91 97037 19368)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:15:00Z",
                "duration_hours": 6.0
            },
            {
                "job_id": "SR-26-0106",
                "title": "Knotter Drive Chain Replacement & Auto-Lube Priming",
                "status": "Completed",
                "status_color": "#10b981",
                "customer_name": "RIL Barwala Bio-Mass Facility",
                "client_company_name": "RIL Barwala Bio-Mass Facility",
                "assigned_technicians": ["M. Naveen Kumar"],
                "assigned_technician_ids": ["TECH-06"],
                "machine_serial": "BP1290-78402",
                "machine_name": "Krone BigPack 1290 HDP High Density Baler",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Barwala Agricultural Block, Haryana",
                "site_contact_person": "Naveen Bishnoi (+91 98120 44332)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T07:30:00Z",
                "duration_hours": 5.5
            },
            {
                "job_id": "SR-26-0107",
                "title": "Bale Ejector Sensor Calibration & Firmware Update",
                "status": "In Progress",
                "status_color": "#059669",
                "customer_name": "Kakinada Agro Energy Terminal",
                "client_company_name": "Kakinada Agro Energy Terminal",
                "assigned_technicians": ["Palthiya Kishore"],
                "assigned_technician_ids": ["TECH-07"],
                "machine_serial": "BP1290-78403",
                "machine_name": "Krone BigPack 1290 HDP High Density Baler",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Kakinada Port Agro Yard, AP",
                "site_contact_person": "Kuldeep Yadav (+91 94401 88776)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:15:00Z",
                "duration_hours": 6.0
            },
            {
                "job_id": "SR-26-0108",
                "title": "Rotor Tine Straightening & Cam Track Greasing",
                "status": "Completed",
                "status_color": "#10b981",
                "customer_name": "Bathinda Bio-Power Co.",
                "client_company_name": "Bathinda Bio-Power Co.",
                "assigned_technicians": ["Nitin Gour"],
                "assigned_technician_ids": ["TECH-08"],
                "machine_serial": "FV1500-33902",
                "machine_name": "Krone Fortima V 1500 Round Baler",
                "job_type": "Paid",
                "service_category": "AMC Service",
                "location": "Talwandi Sabo Bio-Mass Facility, Punjab",
                "site_contact_person": "Davinder Singh (+91 98140 11998)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T07:00:00Z",
                "duration_hours": 6.0
            },
            {
                "job_id": "SR-26-0109",
                "title": "Season Pre-Check & Electrical Loom Harness Test",
                "status": "Hold",
                "status_color": "#f59e0b",
                "customer_name": "Sangrur Green Agro",
                "client_company_name": "Sangrur Green Agro",
                "assigned_technicians": [],
                "assigned_technician_ids": [],
                "machine_serial": "BX6800-45915",
                "machine_name": "Krone BiG X 680 Forage Harvester",
                "job_type": "AMC",
                "service_category": "General Service",
                "location": "Sangrur Bio-Energy Site, Punjab",
                "site_contact_person": "Hardeep Gill (+91 98141 33221)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T13:00:00Z",
                "duration_hours": 4.0
            },
            {
                "job_id": "SR-26-0110",
                "title": "Commissioning & Operator Training for High Density Baling",
                "status": "Completed",
                "status_color": "#10b981",
                "customer_name": "Ludhiana Bio-Energy Hub",
                "client_company_name": "Ludhiana Bio-Energy Hub",
                "assigned_technicians": [],
                "assigned_technician_ids": [],
                "machine_serial": "EC8700-12849",
                "machine_name": "Krone EasyCut B 870 Mower Conditioner",
                "job_type": "Warranty",
                "service_category": "Training",
                "location": "Ludhiana Depo, Punjab",
                "site_contact_person": "Balwinder Sandhu (+91 98140 77665)",
                "scheduled_date": today_str,
                "scheduled_start": f"{today_str}T08:00:00Z",
                "duration_hours": 4.0
            }
        ]

    def _build_machinery(self) -> List[Dict[str, Any]]:
        return [
            {
                "asset_id": "AST-01",
                "asset_name": "Krone BigPack 1290 HDP High Density Baler",
                "serial_number": "BP1290-78401",
                "client_company_name": "Reliance Industries Limited (Bio-Energy Division)",
                "site_contact_person": "Rajinder Verma (+91 98765 43210)",
                "location": "Ludhiana Bio-Mass Hub, Punjab",
                "active_job_id": "SR-26-0101",
                "service_type": "Emergency Knotter Timing Calibration",
                "operating_hours": 1845.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-02",
                "asset_name": "Krone Fortima V 1500 Round Baler",
                "serial_number": "FV1500-33901",
                "client_company_name": "Punjab State Farm Cooperative Hoshiarpur",
                "site_contact_person": "Harbhajan Mann (+91 98765 43211)",
                "location": "Hoshiarpur Agro Complex, Punjab",
                "active_job_id": "SR-26-0102",
                "service_type": "Commissioning & First Season Run",
                "operating_hours": 920.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-03",
                "asset_name": "Krone BiG X 680 Forage Harvester",
                "serial_number": "BX6800-45912",
                "client_company_name": "VERBIO Bio-Gas India Pvt Ltd (Western UP Plant)",
                "site_contact_person": "Sunil Tyagi (+91 98765 43212)",
                "location": "Meerut Sugar Belt, Uttar Pradesh",
                "active_job_id": "SR-26-0103",
                "service_type": "Drum Cutterhead Knife Sharpening",
                "operating_hours": 512.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-04",
                "asset_name": "Krone EasyCut B 870 Mower Conditioner",
                "serial_number": "EC8700-12845",
                "client_company_name": "SAEL Punjab Biomass Energy Project",
                "site_contact_person": "Gurcharan Singh (+91 98765 43213)",
                "location": "Barnala Bio-Mass Site, Punjab",
                "active_job_id": "SR-26-0104",
                "service_type": "Bed Oil Leakage & Cutterbar Disc Inspection",
                "operating_hours": 1240.0,
                "health_status": "Under Service"
            },
            {
                "asset_id": "AST-05",
                "asset_name": "Krone Swadro TC 880 Rotary Rake",
                "serial_number": "SW8800-98321",
                "client_company_name": "Hoshiarpur Bio-Fuels Farm Cluster",
                "site_contact_person": "Malkit Singh (+91 98765 43214)",
                "location": "Hoshiarpur Fields, Punjab",
                "active_job_id": "SR-26-0105",
                "service_type": "Rotor Height Calibration",
                "operating_hours": 640.0,
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
                    "technician_name": "Gurpreet Singh",
                    "region": "Punjab",
                    "customer_company": "Reliance Industries Limited",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 6.5,
                    "travelling_hours": 1.5,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 0.0,
                    "distance_km": 84.6
                },
                {
                    "technician_id": "TECH-02",
                    "technician_name": "Vikram Sharma",
                    "region": "Haryana",
                    "customer_company": "Reliance Industries Limited",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 5.5,
                    "travelling_hours": 1.8,
                    "unauthorized_hours": 0.5,
                    "base_idle_hours": 0.2,
                    "distance_km": 92.4
                },
                {
                    "technician_id": "TECH-03",
                    "technician_name": "Sunny Kumar",
                    "region": "Haryana",
                    "customer_company": "Adani Agri Logistics Ltd",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 7.0,
                    "travelling_hours": 1.0,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 0.0,
                    "distance_km": 48.0
                },
                {
                    "technician_id": "TECH-04",
                    "technician_name": "Jaswinder Singh",
                    "region": "Punjab",
                    "customer_company": "SAEL Punjab Biomass Energy Project",
                    "date": d,
                    "shift_hours": 8.0,
                    "working_hours": 5.0,
                    "travelling_hours": 2.0,
                    "unauthorized_hours": 0.0,
                    "base_idle_hours": 1.0,
                    "distance_km": 76.5
                },
                {
                    "technician_id": "TECH-05",
                    "technician_name": "B. Vignesh",
                    "region": "AP",
                    "customer_company": "Reliance Industries Limited (RIL-Nellore)",
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

    def generate_default_route(self, technician_id: str, date_str: str, tech_name: str = "Gurpreet Singh") -> Dict[str, Any]:
        """Generates realistic route inspection data with 5km clusters and unauthorized stop."""
        return {
            "technician_id": technician_id,
            "technician_name": tech_name,
            "date": date_str,
            "journey_summary": {
                "start_location": {
                    "name": "Krone Regional Hub Ludhiana",
                    "lat": 30.9010,
                    "lng": 75.8573,
                    "departed_at": f"{date_str}T08:00:00Z"
                },
                "destination": {
                    "name": "RIL Bio-Energy Facility Barwala",
                    "lat": 30.3801,
                    "lng": 76.8402,
                    "arrived_at": f"{date_str}T09:45:00Z"
                },
                "transit_duration_minutes": 105.0,
                "unauthorized_stop_duration_minutes": 25.0,
                "total_distance_km": 84.6,
                "anomalies_detected": 1
            },
            "raw_pings_count": 180,
            "clusters_5km": [
                {
                    "cluster_id": "CLUST-01",
                    "centroid": {"lat": 30.9015, "lng": 75.8570},
                    "radius_meters": 450.0,
                    "location_name": "Ludhiana Depot Operational Zone",
                    "pings_count": 45,
                    "duration_minutes": 60.0,
                    "is_job_site": False,
                    "is_base": True
                },
                {
                    "cluster_id": "CLUST-02",
                    "centroid": {"lat": 30.3800, "lng": 76.8405},
                    "radius_meters": 820.0,
                    "location_name": "RIL Barwala Bio-Mass Job Site",
                    "pings_count": 110,
                    "duration_minutes": 390.0,
                    "is_job_site": True,
                    "is_base": False
                }
            ],
            "anomalies": [
                {
                    "type": "unauthorized_stop",
                    "location": {"lat": 30.6450, "lng": 76.3200},
                    "duration_minutes": 25.0,
                    "started_at": f"{date_str}T08:45:00Z",
                    "description": "Vehicle stationary > 15 min outside 5km authorized corridor"
                }
            ],
            "route_polyline": [
                [30.9010, 75.8573],
                [30.8500, 76.0100],
                [30.6450, 76.3200],
                [30.3800, 76.8405]
            ]
        }
