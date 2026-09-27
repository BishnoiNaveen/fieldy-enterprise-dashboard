# Task Dispatch — M2 Explorer 2 (Pulse Board, Tables & Productivity Analytics)

## Mission
Analyze and provide the concrete implementation blueprint for the Live Operational Pulse Board, Machinery Table, Filter Controls, and Recharts Productivity Analytics with Daily/Weekly/Monthly switchers.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md
- Survey Explorer 3 Report: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\survey_explorer_3\report.md

## Scope & Deliverables
1. Design `LivePulseBoard.tsx`:
   - Technicians on paid jobs with live job IDs and assigned Krone machinery.
   - Today's jobs table with `SR-26-XXXX`, status badges, client company, assigned technician.
2. Design `MachineryTable.tsx`:
   - Krone machines under service today (Asset Name, 7-digit Serial, Customer Company, Site Contact Person).
3. Design `FilterBar.tsx`:
   - Multi-dimensional filters: technician dropdown, customer company dropdown, status filter, date range, and timeframe switcher (Daily / Weekly / Monthly) without page reload.
4. Design `ProductivityCharts.tsx`:
   - Stacked Bar & Line charts using Recharts for Working, Travelling, and Idle hours.
   - Drill-down technician scorecards and utilization metrics.
5. Output blueprint to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_explorer_2\report.md` and `handoff.md`.
6. Send completion message to parent orchestrator.
