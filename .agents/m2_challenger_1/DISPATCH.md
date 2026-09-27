# Task Dispatch — M2 Challenger 1 (Frontend Build & Bundle Integrity Challenger)

## Mission
Adversarially challenge the frontend build, bundle size, asset dependencies, and console error profile.

## Authoritative Inputs
- ORIGINAL_REQUEST.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md
- PROJECT.md: C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md

## Scope & Deliverables
1. Run `npm run build` in `frontend/`. Assert that the build succeeds with exit code 0.
2. Inspect the generated `frontend/dist/` bundle:
   - Check that `index.html`, JS chunks, and CSS assets exist and are valid.
   - Verify that there are NO broken asset paths (e.g. missing Leaflet PNG marker images — Leaflet must use custom SVG divIcons).
3. Test offline fallback: run a Node script importing and executing `frontend/src/services/api.ts` with backend down; verify that it returns valid Krone mock data without throwing unhandled exceptions.
4. Deliver empirical verdict: `APPROVE` or `REJECT`.
5. Report to `C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_challenger_1\report.md` and `handoff.md`.
6. Send completion message to parent orchestrator.

## 2026-09-23T09:32:15Z
Received dispatch from parent orchestrator:
You are m2_challenger_1, frontend build & bundle integrity challenger.
Your working directory is C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_challenger_1.
You MUST read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\ORIGINAL_REQUEST.md before starting work.
Also read C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\PROJECT.md and C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_challenger_1\DISPATCH.md.

Challenger tasks:
1. Run `npm run build` in `frontend/`. Assert that it exits with code 0.
2. Inspect the generated `frontend/dist/` bundle: check for valid HTML, JS chunks, CSS assets, and zero broken asset paths (custom SVG divIcons used for Leaflet).
3. Test offline fallback: verify that `frontend/src/services/api.ts` handles network errors gracefully without crashing the UI.
4. Deliver empirical verdict: APPROVE or REJECT.
Write report to C:\Users\Naveen\.gemini\antigravity\scratch\fieldy-enterprise-dashboard\.agents\m2_challenger_1\report.md and handoff.md.
Send completion message to parent orchestrator.
