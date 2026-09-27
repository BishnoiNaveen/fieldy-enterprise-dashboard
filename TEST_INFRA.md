# E2E Test Infra: Krone Agriculture India — Field Service & Telematics Dashboard

## Test Philosophy
- Opaque-box, requirement-driven derived directly from `ORIGINAL_REQUEST.md` and `PROJECT.md § Feature Inventory`.
- Independent of implementation internals; tests verify public REST endpoints, algorithmic guarantees, and business logic.
- Methodology: Category-Partition + Boundary Value Analysis (BVA) + Pairwise Combinations + Real-World Workload Testing.

## Feature Inventory Mapping
| # | Feature | Source | Tier 1 (Features) | Tier 2 (Boundaries) | Tier 3 (Interactions) |
|---|---------|--------|:-----------------:|:-------------------:|:---------------------:|
| 1 | Real-Time Operational Pulse KPIs | ORIGINAL_REQUEST §R1 | ≥5 tests | ≥5 tests | ✓ |
| 2 | Today's Jobs List (`SR-26-XXXX`) | ORIGINAL_REQUEST §R1 | ≥5 tests | ≥5 tests | ✓ |
| 3 | Machinery Under Service Table | ORIGINAL_REQUEST §R1 | ≥5 tests | ≥5 tests | ✓ |
| 4 | Fieldy FSM Session Synchronizer | ORIGINAL_REQUEST §R1 | ≥5 tests | ≥5 tests | ✓ |
| 5 | Calibrated Krone Synthetic Fallback | ORIGINAL_REQUEST §R4 | ≥5 tests | ≥5 tests | ✓ |
| 6 | 5 km Radius Haversine Clustering | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ |
| 7 | Speed-Gated Jitter Dampening | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ |
| 8 | Autonomous Route Inspector | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ |
| 9 | Transit vs Unauthorized Stop Detection | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ |
| 10 | Route Anomaly Detection & Alerts | ORIGINAL_REQUEST §R3 | ≥5 tests | ≥5 tests | ✓ |
| 11 | Multi-Tier Hours Analytics ($H_w, H_t, H_i$) | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ |
| 12 | Timeframe Toggling (Daily/Weekly/Monthly) | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ |
| 13 | Multi-Dimensional Search & Filtering | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ |
| 14 | Comparative Charts & Scorecards | ORIGINAL_REQUEST §R2 | ≥5 tests | ≥5 tests | ✓ |
| 15 | Executive Bento Grid UI Data Feed | ORIGINAL_REQUEST §R4 | ≥5 tests | ≥5 tests | ✓ |
| 16 | Interactive Leaflet Route Map Feed | ORIGINAL_REQUEST §R3, R4 | ≥5 tests | ≥5 tests | ✓ |

## Test Architecture
- **Test Runner**: Pytest executing in Python virtual environment / CLI.
- **Directory Layout**:
  - `tests/test_tier1_features.py`: Happy-path tests for each feature in isolation.
  - `tests/test_tier2_boundaries.py`: Extreme coordinates, exact 4.99 km vs 5.01 km boundary, zero duration, max shift, missing GPS.
  - `tests/test_tier3_combinations.py`: Pairwise interactions between sync, filters, clustering, and hours aggregation.
  - `tests/test_tier4_scenarios.py`: End-to-end multi-technician full-day field service workflows.
- **Execution Command**: `pytest tests/ -v`

## Real-World Application Scenarios (Tier 4)
| # | Scenario | Features Exercised | Complexity |
|---|----------|--------------------|------------|
| 1 | RIL Barwala Knotter Emergency Repair | F1, F2, F3, F6, F8, F9, F11 | High |
| 2 | Hoshiarpur Multi-Field Baler Commissioning | F2, F6, F7, F8, F11, F13 | High |
| 3 | Western UP High-Density Harvester Fleet Inspection | F1, F3, F4, F10, F11, F14 | High |
| 4 | Offline Hub Sync & Telematics Replay | F4, F5, F6, F12, F16 | High |
| 5 | Unauthorized Dhaba Halt & Detour Investigation | F6, F8, F9, F10, F11, F13 | High |

## Coverage Thresholds
- Tier 1: ≥ 5 per feature (≥ 80 tests)
- Tier 2: ≥ 5 per feature (≥ 80 tests)
- Tier 3: Pairwise coverage across core modules (≥ 20 tests)
- Tier 4: ≥ 5 comprehensive real-world scenarios
- Total: ≥ 185 test cases
