"""
backend/app/services/analytics_engine.py
Enterprise Productivity & Hours Analytics Engine for Krone Agriculture India FSM.
Strictly enforces the Conservation Law of Hours: H_shift = H_w + H_t + H_i.
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
import math


class AnalyticsEngine:
    """
    Computes technician productivity metrics, hours rollups (Daily, Weekly, Monthly),
    and multi-dimensional filtering across Krone field service operations.
    """

    CONSERVATION_TOLERANCE = 1e-6
    STANDARD_SHIFT_HOURS = 8.0
    DEPONENT_RATE_PER_MANDAY = 5000.0  # Clause 4.7
    HOURLY_BILLABLE_RATE = 625.0       # 5000.0 / 8.0

    @staticmethod
    def enforce_hours_conservation(
        raw_shift_hours: float,
        working_hours: float,
        travelling_hours: float,
        unauthorized_hours: float = 0.0,
        base_idle_hours: float = 0.0
    ) -> Dict[str, float]:
        """
        Enforces strict conservation: H_shift = H_w + H_t + H_i.
        Guarantees non-negative idle hours and clamps shift duration if overtime occurred.
        """
        def _safe_float(val: Any) -> float:
            try:
                f = float(val)
                return f if math.isfinite(f) else 0.0
            except (ValueError, TypeError):
                return 0.0

        w = max(0.0, _safe_float(working_hours))
        t = max(0.0, _safe_float(travelling_hours))
        known_idle = max(0.0, _safe_float(unauthorized_hours) + _safe_float(base_idle_hours))
        raw_shift = max(0.0, _safe_float(raw_shift_hours))

        # Effective shift hours must be at least the sum of productive + transit time
        effective_shift = max(raw_shift, w + t + known_idle)

        # Idle hours account for the remainder
        idle = max(0.0, effective_shift - (w + t))

        # Precision rounding to 4 decimal places while guaranteeing strict balance
        w_round = round(w, 4)
        t_round = round(t, 4)
        shift_round = round(effective_shift, 4)
        idle_round = round(shift_round - (w_round + t_round), 4)

        # Handle floating rounding glitch
        if idle_round < 0.0:
            idle_round = 0.0
            shift_round = round(w_round + t_round, 4)

        diff = abs(shift_round - (w_round + t_round + idle_round))
        assert diff < 1e-3, f"Conservation violation: {shift_round} != {w_round} + {t_round} + {idle_round}"

        utilization_pct = round(((w_round + t_round) / shift_round * 100.0), 2) if shift_round > 0 else 0.0
        efficiency_pct = round((w_round / shift_round * 100.0), 2) if shift_round > 0 else 0.0

        return {
            "shift_hours": shift_round,
            "working_hours": w_round,
            "travelling_hours": t_round,
            "idle_hours": idle_round,
            "utilization_pct": utilization_pct,
            "efficiency_pct": efficiency_pct,
            "conservation_error": round(diff, 8)
        }

    def filter_records(
        self,
        records: List[Dict[str, Any]],
        technician_id: Optional[str] = None,
        customer_company: Optional[str] = None,
        job_status: Optional[str] = None,
        job_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Filters work order or attendance records across multiple dimensions."""
        filtered = records

        if technician_id and technician_id.upper() != "ALL":
            filtered = [
                r for r in filtered
                if r.get("technician_id") == technician_id
                or technician_id in r.get("assigned_technician_ids", [])
            ]

        if customer_company and customer_company.upper() != "ALL":
            cust_lower = customer_company.lower()
            filtered = [
                r for r in filtered
                if cust_lower in str(r.get("customer_company", "")).lower()
                or cust_lower in str(r.get("customer_name", "")).lower()
                or cust_lower in str(r.get("client_company_name", "")).lower()
            ]

        if job_status and job_status.upper() != "ALL":
            status_lower = job_status.lower()
            filtered = [
                r for r in filtered
                if str(r.get("status", "")).lower() == status_lower
                or str(r.get("job_status", "")).lower() == status_lower
            ]

        if job_type and job_type.upper() != "ALL":
            type_lower = job_type.lower()
            filtered = [
                r for r in filtered
                if str(r.get("job_type", "")).lower() == type_lower
                or str(r.get("service_category", "")).lower() == type_lower
            ]

        if start_date:
            filtered = [r for r in filtered if r.get("date", r.get("job_date", r.get("scheduled_date", ""))) >= start_date]

        if end_date:
            filtered = [r for r in filtered if r.get("date", r.get("job_date", r.get("scheduled_date", ""))) <= end_date]

        return filtered

    def aggregate_productivity(
        self,
        daily_shift_records: List[Dict[str, Any]],
        jobs_records: List[Dict[str, Any]],
        timeframe: str = "daily",
        technician_id: Optional[str] = None,
        customer_company: Optional[str] = None,
        job_status: Optional[str] = None,
        job_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete productivity aggregation across Daily, Weekly, or Monthly frames.
        """
        # Step 1: Apply multi-dimensional filters to jobs and shift records
        filtered_shifts = self.filter_records(
            daily_shift_records,
            technician_id=technician_id,
            customer_company=customer_company,
            start_date=start_date,
            end_date=end_date
        )
        filtered_jobs = self.filter_records(
            jobs_records,
            technician_id=technician_id,
            customer_company=customer_company,
            job_status=job_status,
            job_type=job_type,
            start_date=start_date,
            end_date=end_date
        )

        # Step 2: Compute fleet summary totals
        tot_work = 0.0
        tot_travel = 0.0
        tot_idle = 0.0
        tot_shift = 0.0
        tot_distance = 0.0

        for s in filtered_shifts:
            metrics = self.enforce_hours_conservation(
                raw_shift_hours=s.get("shift_hours", self.STANDARD_SHIFT_HOURS),
                working_hours=s.get("working_hours", 0.0),
                travelling_hours=s.get("travelling_hours", 0.0),
                unauthorized_hours=s.get("unauthorized_hours", 0.0),
                base_idle_hours=s.get("base_idle_hours", 0.0)
            )
            tot_work += metrics["working_hours"]
            tot_travel += metrics["travelling_hours"]
            tot_idle += metrics["idle_hours"]
            tot_shift += metrics["shift_hours"]
            tot_distance += s.get("distance_km", 0.0)

        tot_work = round(tot_work, 2)
        tot_travel = round(tot_travel, 2)
        tot_idle = round(tot_idle, 2)
        tot_shift = round(tot_shift, 2)
        avg_utilization = round(((tot_work + tot_travel) / tot_shift * 100.0), 2) if tot_shift > 0 else 0.0

        summary = {
            "total_working_hours": tot_work,
            "total_travelling_hours": tot_travel,
            "total_idle_hours": tot_idle,
            "total_shift_hours": tot_shift,
            "average_utilization_pct": avg_utilization,
            "total_distance_km": round(tot_distance, 1),
            "jobs_count": len(filtered_jobs)
        }

        # Step 3: Per-technician aggregation records
        tech_map: Dict[str, Dict[str, Any]] = {}
        for s in filtered_shifts:
            t_id = s["technician_id"]
            if t_id not in tech_map:
                tech_map[t_id] = {
                    "technician_id": t_id,
                    "technician_name": s.get("technician_name", t_id),
                    "region": s.get("region", "North"),
                    "working_hours": 0.0,
                    "travelling_hours": 0.0,
                    "idle_hours": 0.0,
                    "shift_hours": 0.0,
                    "distance_km": 0.0,
                    "jobs_count": 0,
                    "days_active": 0
                }
            m = self.enforce_hours_conservation(
                raw_shift_hours=s.get("shift_hours", self.STANDARD_SHIFT_HOURS),
                working_hours=s.get("working_hours", 0.0),
                travelling_hours=s.get("travelling_hours", 0.0),
                unauthorized_hours=s.get("unauthorized_hours", 0.0),
                base_idle_hours=s.get("base_idle_hours", 0.0)
            )
            tech_map[t_id]["working_hours"] += m["working_hours"]
            tech_map[t_id]["travelling_hours"] += m["travelling_hours"]
            tech_map[t_id]["idle_hours"] += m["idle_hours"]
            tech_map[t_id]["shift_hours"] += m["shift_hours"]
            tech_map[t_id]["distance_km"] += s.get("distance_km", 0.0)
            tech_map[t_id]["days_active"] += 1

        # Link jobs count to technician
        for j in filtered_jobs:
            assigned = j.get("assigned_technician_ids", [])
            if not assigned and "technician_id" in j:
                assigned = [j["technician_id"]]
            for t_id in assigned:
                if t_id and t_id in tech_map:
                    tech_map[t_id]["jobs_count"] += 1

        technician_records = []
        for t_id, d in sorted(tech_map.items()):
            w = round(d["working_hours"], 2)
            t = round(d["travelling_hours"], 2)
            sh = round(d["shift_hours"], 2)
            i = round(max(0.0, sh - (w + t)), 2)
            util = round(((w + t) / sh * 100.0), 2) if sh > 0 else 0.0
            status_rating = "EXEMPLARY" if util >= 75.0 else ("NORMAL" if util >= 60.0 else "NEEDS_IMPROVEMENT")
            technician_records.append({
                "technician_id": t_id,
                "technician_name": d["technician_name"],
                "region": d["region"],
                "working_hours": w,
                "travelling_hours": t,
                "idle_hours": i,
                "shift_hours": sh,
                "utilization_pct": util,
                "distance_km": round(d["distance_km"], 1),
                "travel_distance_km": round(d["distance_km"], 1),
                "jobs_count": d["jobs_count"],
                "billable_revenue_inr": round(w * self.HOURLY_BILLABLE_RATE, 2),
                "deputation_revenue_inr": round(w * self.HOURLY_BILLABLE_RATE, 2),
                "man_days": round(w / self.STANDARD_SHIFT_HOURS, 3),
                "performance_badge": status_rating,
                "status_rating": status_rating
            })

        # Step 4: Trend series generation
        date_buckets: Dict[str, Dict[str, float]] = {}
        for s in filtered_shifts:
            d_str = s.get("date", "2026-09-22")
            if d_str not in date_buckets:
                date_buckets[d_str] = {"working": 0.0, "travelling": 0.0, "idle": 0.0, "distance": 0.0}
            m = self.enforce_hours_conservation(
                raw_shift_hours=s.get("shift_hours", self.STANDARD_SHIFT_HOURS),
                working_hours=s.get("working_hours", 0.0),
                travelling_hours=s.get("travelling_hours", 0.0)
            )
            date_buckets[d_str]["working"] += m["working_hours"]
            date_buckets[d_str]["travelling"] += m["travelling_hours"]
            date_buckets[d_str]["idle"] += m["idle_hours"]
            date_buckets[d_str]["distance"] += s.get("distance_km", 0.0)

        trend_data = []
        for d_str in sorted(date_buckets.keys()):
            b = date_buckets[d_str]
            trend_data.append({
                "period": d_str,
                "working": round(b["working"], 2),
                "travelling": round(b["travelling"], 2),
                "idle": round(b["idle"], 2),
                "distance_km": round(b["distance"], 1)
            })

        # Step 5: Customer distribution breakdown
        cust_buckets: Dict[str, Dict[str, Any]] = {}
        for j in filtered_jobs:
            c_name = j.get("customer_name") or j.get("client_company_name") or "Direct Service"
            if c_name not in cust_buckets:
                cust_buckets[c_name] = {"total_hours": 0.0, "jobs_count": 0}
            cust_buckets[c_name]["total_hours"] += float(j.get("duration_hours", 4.0))
            cust_buckets[c_name]["jobs_count"] += 1

        customer_distribution = []
        total_cust_hours = sum(c["total_hours"] for c in cust_buckets.values()) or 1.0
        for c_name, c_data in sorted(cust_buckets.items(), key=lambda x: x[1]["total_hours"], reverse=True):
            customer_distribution.append({
                "customer_name": c_name,
                "client_company_name": c_name,
                "total_hours": round(c_data["total_hours"], 2),
                "percentage": round(c_data["total_hours"] / total_cust_hours * 100.0, 1),
                "jobs_count": c_data["jobs_count"]
            })

        return {
            "timeframe": timeframe.lower(),
            "summary": summary,
            "technician_records": technician_records,
            "trend_data": trend_data,
            "customer_distribution": customer_distribution
        }
