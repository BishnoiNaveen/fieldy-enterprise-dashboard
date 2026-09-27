import sys
sys.path.insert(0, 'backend')
from app.services.telematics_engine import analyze_route_journey, calculate_hours, cluster_pings_5km, filter_stationary_jitter

base = {'lat': 30.9010, 'lon': 75.8573, 'name': 'Ludhiana Hub'}
dest = {'lat': 30.3800, 'lon': 76.8405, 'name': 'Barwala Site'}

# Test 1: Clean route with 0 stops
clean_pings = [{'lat': 30.9010 + i*0.001, 'lon': 75.8573 + i*0.001, 'speed_kmh': 60.0, 'timestamp_s': i*60.0, 'timestamp': f'2026-09-22T08:{i:02d}:00Z'} for i in range(40)]
r1 = analyze_route_journey(clean_pings, base, dest)
assert r1['journey_summary']['anomalies_detected'] == 0, f"Expected 0 anomalies, got {r1['journey_summary']['anomalies_detected']}"
assert r1['journey_summary']['unauthorized_stop_duration_minutes'] == 0.0, f"Expected 0.0 unauth min, got {r1['journey_summary']['unauthorized_stop_duration_minutes']}"
assert r1['anomalies'] == [], f"Expected [], got {r1['anomalies']}"
print("Test 1 (Clean route 0 stops): PASS")

# Test 2: Route with short authorized stop (10 min stop in between)
auth_pings = list(clean_pings) + [{'lat': 30.6450, 'lon': 76.3200, 'speed_kmh': 0.0, 'timestamp_s': (40+i)*60.0, 'timestamp': f'2026-09-22T08:{40+i:02d}:00Z'} for i in range(10)]
r2 = analyze_route_journey(auth_pings, base, dest)
assert r2['journey_summary']['anomalies_detected'] == 0, f"Expected 0 anomalies, got {r2['journey_summary']['anomalies_detected']}"
assert r2['journey_summary']['unauthorized_stop_duration_minutes'] == 0.0, f"Expected 0.0 unauth min, got {r2['journey_summary']['unauthorized_stop_duration_minutes']}"
assert r2['anomalies'] == [], f"Expected [], got {r2['anomalies']}"
print("Test 2 (Authorized 10 min stop): PASS")

# Test 3: Route with unauthorized stop (25 min stop at dhaba)
unauth_pings = list(clean_pings) + [{'lat': 30.6450, 'lon': 76.3200, 'speed_kmh': 0.0, 'timestamp_s': (40+i)*60.0, 'timestamp': f'2026-09-22T08:{40+i:02d}:00Z'} for i in range(25)]
r3 = analyze_route_journey(unauth_pings, base, dest)
assert r3['journey_summary']['anomalies_detected'] == 1, f"Expected 1 anomaly, got {r3['journey_summary']['anomalies_detected']}"
unauth_dur = r3['journey_summary']['unauthorized_stop_duration_minutes']
assert unauth_dur > 20.0, f"Expected > 20 min unauth, got {unauth_dur}"
assert len(r3['anomalies']) == 1, f"Expected 1 anomaly in list, got {len(r3['anomalies'])}"
assert r3['anomalies'][0]['type'] == 'unauthorized_stop'
print(f"Test 3 (Unauthorized 25 min stop: detected {unauth_dur} min): PASS")

# Test 4: Pure stationary day at base (e.g. maintenance at hub)
base_pings = [{'lat': 30.9010 + 0.00001*(i%2), 'lon': 75.8573, 'speed_kmh': 0.0, 'timestamp_s': i*60.0, 'timestamp': f'2026-09-22T08:{i:02d}:00Z'} for i in range(60)]
r4 = analyze_route_journey(base_pings, base, dest)
assert r4['journey_summary']['anomalies_detected'] == 0, f"Expected 0 anomalies, got {r4['journey_summary']['anomalies_detected']}"
assert r4['journey_summary']['unauthorized_stop_duration_minutes'] == 0.0
print("Test 4 (Stationary day at base): PASS")

# Test 5: calculate_hours timestamp interval math
h_res = calculate_hours(unauth_pings, base_coords=base, job_site_coords=dest)
assert h_res['conservation_error'] < 1e-5, f"Conservation error too high: {h_res['conservation_error']}"
assert h_res['working_hours'] >= 0.0
assert h_res['travelling_hours'] > 0.0
assert h_res['idle_hours'] > 0.0
print(f"Test 5 (calculate_hours: H_w={h_res['working_hours']}, H_t={h_res['travelling_hours']}, H_i={h_res['idle_hours']}, err={h_res['conservation_error']}): PASS")

# Test 6: Verify API endpoint variation across technicians
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

res_tech1 = client.get('/api/telematics/routes?technician_id=TECH-01').json()
res_tech5 = client.get('/api/telematics/routes?technician_id=TECH-05').json()
res_tech8 = client.get('/api/telematics/routes?technician_id=TECH-08').json()

assert res_tech1['journey_summary']['start_location']['name'] != res_tech5['journey_summary']['start_location']['name'], "TECH-01 and TECH-05 start locations must differ!"
assert res_tech1['route_polyline'] != res_tech5['route_polyline'], "TECH-01 and TECH-05 polyline must differ!"
assert res_tech1['route_polyline'] != res_tech8['route_polyline'], "TECH-01 and TECH-08 polyline must differ!"
print(f"Test 6 (API variation across techs: TECH-01 at {res_tech1['journey_summary']['start_location']['name']}, TECH-05 at {res_tech5['journey_summary']['start_location']['name']}, TECH-08 at {res_tech8['journey_summary']['start_location']['name']}): PASS")

# Test 7: Verify clean technician route (TECH-03, Panipat Grain Silos, no unauthorized stop)
res_tech3 = client.get('/api/telematics/routes?technician_id=TECH-03').json()
assert res_tech3['journey_summary']['anomalies_detected'] == 0, f"TECH-03 should have 0 anomalies, got {res_tech3['journey_summary']['anomalies_detected']}"
assert res_tech3['journey_summary']['unauthorized_stop_duration_minutes'] == 0.0, f"TECH-03 unauth min should be 0.0, got {res_tech3['journey_summary']['unauthorized_stop_duration_minutes']}"
assert res_tech3['anomalies'] == [], f"TECH-03 anomalies should be [], got {res_tech3['anomalies']}"
print(f"Test 7 (API clean route TECH-03 reports 0 anomalies, 0.0 unauth min): PASS")

print("\nALL ADVERSARIAL INTEGRITY TESTS PASSED SUCCESSFULLY!")
