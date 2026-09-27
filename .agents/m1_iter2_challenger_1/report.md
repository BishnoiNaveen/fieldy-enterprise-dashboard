# Adversarial Challenge Report: Geospatial Clean-Route Invariants & Anomaly Detection

- **Target Module**: `backend/app/services/telematics_engine.py`
- **Agent**: `m1_iter2_challenger_1` (Geospatial Clean-Route Adversarial Challenger)
- **Iteration**: Milestone 1 Iteration 2
- **Date**: 2026-09-23
- **Test Harness**: `tests/test_adversarial_clean_routes.py` (106 test cases)
- **Empirical Verdict**: **APPROVE**
- **Overall Risk Assessment**: **LOW** (Clean-Route Invariants Verified 100% Empirically)

---

## Challenge Summary

**Overall risk assessment**: **LOW**

As an empirical challenger, I subjected the updated `telematics_engine.py` to an exhaustive adversarial test battery specifically focused on clean synthesized routes and intentional anomaly insertion:
1. **100 Clean Synthesized Routes**: Verified across 10 designated corridors across India (Punjab, Haryana, UP, Andhra Pradesh, Madhya Pradesh, Maharashtra) with varying GPS breadcrumb volume (from 10 to 500 pings).
2. **Zero False Positives Invariant**: Verified `anomalies_detected == 0`, `unauthorized_stop_duration_minutes == 0.0`, and `anomalies == []` across **100% of trials** (100/100).
3. **Intentional Anomaly Insertion**: Verified that inserted unauthorized halts (>15 minutes outside the 5 km authorized base/job-site zones) are accurately detected with exact duration and geodetic coordinates, while sub-threshold halts (<=15 min) and authorized zone dwells remain correctly unflagged.
4. **Execution Performance**: 100 journey analyses executed in 0.205s total (mean latency: **2.05 ms** per journey analysis, max latency: **8.49 ms**), confirming $O(N)$ linear complexity without quadratic degradation.

---

## 1. Adversarial Challenges & Hypotheses Tested

### Challenge 1 (False Positive Anomaly Generation on Clean Routes) — Passed [Risk: LOW]
- **Assumption Challenged**: On continuous transit routes without unauthorized stops, GPS micro-jitter, ping density variations (10 to 500 pings), or speed-gate transitions could trigger spurious raw stop extraction or false positive `UNAUTHORIZED_STOP` anomalies.
- **Attack Scenario**: Synthesized 100 clean routes across 10 operational corridors spanning distances from 6.8 km (Kovur yard) to 84.6 km (Ludhiana-Barwala). Tested across 10 ping volume steps (10, 20, 35, 50, 75, 100, 180, 250, 375, 500 pings) and 3 operational profiles (`pure_transit`, `operational_full`, `transit_with_minor_pauses`).
- **Blast Radius**: If clean routes produced false anomalies, fleet managers would be overwhelmed with erroneous disciplinary alerts and false billing deductions for technicians.
- **Empirical Result**: 100 out of 100 trials passed with:
  - `journey_summary.anomalies_detected == 0` (100% of trials)
  - `journey_summary.unauthorized_stop_duration_minutes == 0.0` (100% of trials)
  - `anomalies == []` (100% of trials)
- **Mitigation / Engine Defense**: The deadband spatial filter (`JITTER_DEADBAND_METERS = 30.0m`, `STATIONARY_SPEED_KMH = 1.5 km/h`) and raw stop threshold (`MIN_STOP_DURATION_SECONDS = 300.0s`) robustly isolate transient traffic pauses and moving jitter from verified stationary clusters.

### Challenge 2 (Sensitivity and Localization of Inserted Unauthorized Halts) — Passed [Risk: LOW]
- **Assumption Challenged**: If an unauthorized halt occurs outside the 5 km corridor zone, the clustering or classification engine might under-report duration, misclassify it as an authorized transit stop, or merge it into base/destination clusters.
- **Attack Scenarios**:
  1. Inserted 20-minute halt midway along Ludhiana-Barwala corridor (38 km from depot, 55 km from customer site).
  2. Inserted 25-minute roadside dhaba halt outside 5 km zone along Hisar corridor.
  3. Inserted 35-minute prolonged halt along Indore-Pithampur corridor.
  4. Inserted multiple separate unauthorized halts (20 min + 25 min) on a single journey.
- **Blast Radius**: Failure to detect genuine halts allows off-route side trips and unaccounted idle time to escape billing scrutiny.
- **Empirical Result**:
  - 20-min halt: `anomalies_detected == 1`, `unauthorized_stop_duration_minutes == 20.0`, centroid accurately resolved within 20 meters of inserted coordinate.
  - 25-min halt: `anomalies_detected == 1`, `unauthorized_stop_duration_minutes == 25.0`.
  - 35-min halt: `anomalies_detected == 1`, `unauthorized_stop_duration_minutes == 35.0`.
  - Multiple halts: `anomalies_detected == 2`, `unauthorized_stop_duration_minutes == 45.0` (durations: `[20.0, 25.0]`).
- **Mitigation / Engine Defense**: `inspect_journey` strictly applies `UNAUTHORIZED_STOP_THRESHOLD_SECONDS = 900.0s` outside the 5 km base/destination geofences.

### Challenge 3 (Sub-Threshold and Authorized Zone Invariance) — Passed [Risk: LOW]
- **Assumption Challenged**: Dwells inside authorized zones (Depot base or Customer job site) or brief en-route halts (e.g. 10-min tea/toll stop) might inadvertently trigger anomaly alerts if distance or duration thresholds are improperly clamped.
- **Attack Scenarios**:
  1. Inserted 10-minute halt outside 5 km zone (sub-threshold, <= 15 min).
  2. Inserted 30-minute halt 1.1 km from Base Depot (inside 5 km base geofence).
  3. Inserted 30-minute halt 1.0 km from Customer Job Site (inside 5 km destination geofence).
- **Empirical Result**:
  - 10-min halt outside 5 km zone: `anomalies_detected == 0`, `unauthorized_stop_duration_minutes == 0.0`, `anomalies == []` (classified as `AUTHORIZED_TRANSIT_STOP`).
  - 30-min halt inside Base 5 km zone: `anomalies_detected == 0`, `unauthorized_stop_duration_minutes == 0.0`, `anomalies == []` (classified as `STARTING_BASE`).
  - 30-min halt inside Customer 5 km zone: `anomalies_detected == 0`, `unauthorized_stop_duration_minutes == 0.0`, `anomalies == []` (classified as `CUSTOMER_DESTINATION`).

---

## 2. Empirical Stress Test Results Table

| Test Identifier | Category | Test Case / Scenario | Expected Outcome | Actual Outcome | Status |
|---|---|---|---|---|---|
| `test_clean_route_trial[0..9, 0..9]` (100 trials) | Clean Routes | 100 trials across 10 corridors (10 to 500 pings, 3 profiles) | `anomalies_detected == 0`, `unauth_min == 0.0`, `anomalies == []` | `anomalies_detected == 0`, `unauth_min == 0.0`, `anomalies == []` in 100/100 | **PASS** |
| `test_adv_anomaly_01` | Anomaly Insertion | 20-min halt midway outside 5 km zone | `anomalies_detected == 1`, `unauth_min == 20.0` | `anomalies_detected == 1`, `unauth_min == 20.0` | **PASS** |
| `test_adv_anomaly_02` | Anomaly Insertion | 25-min roadside halt outside 5 km zone | `anomalies_detected == 1`, `unauth_min == 25.0` | `anomalies_detected == 1`, `unauth_min == 25.0` | **PASS** |
| `test_adv_anomaly_03` | Anomaly Insertion | 35-min prolonged halt outside 5 km zone | `anomalies_detected == 1`, `unauth_min == 35.0` | `anomalies_detected == 1`, `unauth_min == 35.0` | **PASS** |
| `test_adv_anomaly_04` | Anomaly Insertion | Multiple unauthorized halts (20m + 25m) | `anomalies_detected == 2`, `unauth_min == 45.0` | `anomalies_detected == 2`, `unauth_min == 45.0` | **PASS** |
| `test_adv_anomaly_05` | Boundary Check | Sub-threshold 10-min halt outside 5 km zone | `anomalies_detected == 0`, `unauth_min == 0.0` | `anomalies_detected == 0`, `unauth_min == 0.0` | **PASS** |
| `test_adv_anomaly_06` | Boundary Check | 30-min halt inside base & site 5 km geofences | `anomalies_detected == 0`, `unauth_min == 0.0` | `anomalies_detected == 0`, `unauth_min == 0.0` | **PASS** |

### Benchmark Metrics Across 100 Clean Synthesized Route Trials
- **Total Clean Trials**: 100
- **Pass Rate**: **100.0%** (100 passed, 0 failed)
- **False Positive Anomalies**: **0** across all 100 trials
- **Mean Execution Time per Route**: **2.05 ms**
- **Max Execution Time**: **8.49 ms** (at 500 pings with operational clustering)
- **Min Execution Time**: **0.28 ms** (at 10 pings)
- **Total Test Suite Pass Rate**: **371 / 371 tests passed** (backend + e2e + adversarial) in 6.66s.

---

## 3. Unchallenged Areas

- **Live GPS Hardware Dropout / Multipath**: Hardware-level NMEA parsing errors, satellite dilution of precision (HDOP > 5.0), and device firmware sleep reconnects were not tested with physical hardware; simulated using synthetic Gaussian perturbation and ping intervals.
- **Frontend Map Visual Rendering**: Verification was conducted at the backend engine / API response level; Leaflet DOM rendering is evaluated under Milestone 2.

---

## 4. Final Empirical Verdict

### **VERDICT: APPROVE**

The geospatial clean-route behavior of `telematics_engine.py` meets all acceptance criteria with **100% empirical compliance**:
1. Zero false anomalies detected on clean routes across all 10 corridors and all breadcrumb scales (10 to 500 pings).
2. Exactly 0.0 unauthorized stop duration reported on clean routes.
3. Accurate identification and quantification of inserted unauthorized stop anomalies (>15 min outside 5 km zone).
4. Sub-millisecond to low-millisecond execution performance ($O(N)$ complexity).
