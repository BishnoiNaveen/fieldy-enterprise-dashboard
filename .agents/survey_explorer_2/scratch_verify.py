import math
from datetime import datetime, timedelta

def haversine(lat1, lon1, lat2, lon2, r=6371.0):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2)**2
    a = min(1.0, max(0.0, a))
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def initial_bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dlam = math.radians(lon2 - lon1)
    y = math.sin(dlam) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlam)
    return math.atan2(y, x)

def cross_track_distance(lat_p, lon_p, lat_a, lon_a, lat_b, lon_b, r=6371.0):
    phi_a, phi_p = math.radians(lat_a), math.radians(lat_p)
    dphi = phi_p - phi_a
    dlam = math.radians(lon_p - lon_a)
    a = math.sin(dphi / 2)**2 + math.cos(phi_a) * math.cos(phi_p) * math.sin(dlam / 2)**2
    delta_13 = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    theta_13 = initial_bearing(lat_a, lon_a, lat_p, lon_p)
    theta_12 = initial_bearing(lat_a, lon_a, lat_b, lon_b)
    
    d_xt_angular = math.asin(min(1.0, max(-1.0, math.sin(delta_13) * math.sin(theta_13 - theta_12))))
    return abs(d_xt_angular * r)

def weighted_cartesian_centroid(stops):
    X, Y, Z, total_w = 0.0, 0.0, 0.0, 0.0
    for s in stops:
        w = max(1.0, float(s.get('duration_s', 1.0)))
        phi = math.radians(s['lat'])
        lam = math.radians(s['lon'])
        X += w * math.cos(phi) * math.cos(lam)
        Y += w * math.cos(phi) * math.sin(lam)
        Z += w * math.sin(phi)
        total_w += w
    if total_w == 0:
        return stops[0]['lat'], stops[0]['lon']
    X /= total_w
    Y /= total_w
    Z /= total_w
    hyp = math.sqrt(X*X + Y*Y)
    return math.degrees(math.atan2(Z, hyp)), math.degrees(math.atan2(Y, X))

def cluster_stops_5km(raw_stops, max_radius_km=5.0):
    clusters = []
    for stop in raw_stops:
        best_cluster = None
        best_dist = float('inf')
        for c in clusters:
            dist_to_centroid = haversine(stop['lat'], stop['lon'], c['centroid_lat'], c['centroid_lon'])
            if dist_to_centroid <= max_radius_km and dist_to_centroid < best_dist:
                cand_stops = c['stops'] + [stop]
                new_lat, new_lon = weighted_cartesian_centroid(cand_stops)
                if all(haversine(s['lat'], s['lon'], new_lat, new_lon) <= max_radius_km for s in cand_stops):
                    best_cluster = c
                    best_dist = dist_to_centroid
        
        if best_cluster is not None:
            best_cluster['stops'].append(stop)
            c_lat, c_lon = weighted_cartesian_centroid(best_cluster['stops'])
            best_cluster['centroid_lat'] = c_lat
            best_cluster['centroid_lon'] = c_lon
            best_cluster['total_duration_s'] += stop['duration_s']
            best_cluster['end_time'] = max(best_cluster['end_time'], stop['end_time'])
        else:
            clusters.append({
                'cluster_id': f"ZONE-{len(clusters)+1}",
                'centroid_lat': stop['lat'],
                'centroid_lon': stop['lon'],
                'total_duration_s': stop['duration_s'],
                'start_time': stop['start_time'],
                'end_time': stop['end_time'],
                'stops': [stop]
            })
    return clusters

def run_telematics_simulation():
    # Base location: Krone Kakinada Depot
    base_loc = {'lat': 16.9600, 'lon': 82.2300, 'name': 'Krone Kakinada Depot'}
    # Customer site: RIL Bio-Energy Facility
    customer_loc = {'lat': 16.5000, 'lon': 81.8000, 'name': 'Reliance Bio-Energy Site'}
    
    t0 = datetime(2026, 9, 22, 8, 0, 0) # 08:00 Clock-In
    
    # 1. Base Stop: 08:00 to 08:20 (20 min prep)
    stop_base = {
        'id': 'STOP-1',
        'name': 'Kakinada Depot Prep',
        'start_time': t0,
        'end_time': t0 + timedelta(minutes=20),
        'duration_s': 1200,
        'lat': 16.9600,
        'lon': 82.2300
    }
    
    # 2. Transit Leg 1: 08:20 to 09:30 (70 min driving, ~60 km)
    t_travel_1 = 70 * 60 # 4200s
    
    # 3. Unauthorized Dhaba Stop: 09:30 to 09:58 (28 min stop, >15m threshold!)
    t_dhaba_start = t0 + timedelta(minutes=20 + 70)
    stop_unauth = {
        'id': 'STOP-2',
        'name': 'Highway Dhaba Stop (Unauthorized)',
        'start_time': t_dhaba_start,
        'end_time': t_dhaba_start + timedelta(minutes=28),
        'duration_s': 28 * 60, # 1680s
        'lat': 16.7350,
        'lon': 82.0150
    }
    
    # 4. Transit Leg 2: 09:58 to 10:48 (50 min driving, ~40 km)
    t_travel_2 = 50 * 60 # 3000s
    
    # 5. Customer Arrival: Stop at Main Plant: 10:48 to 13:18 (2.5 hrs = 9000s)
    t_cust_start = t_dhaba_start + timedelta(minutes=28 + 50)
    stop_cust_1 = {
        'id': 'STOP-3',
        'name': 'RIL Plant Gate & Baler Main Workshop',
        'start_time': t_cust_start,
        'end_time': t_cust_start + timedelta(hours=2.5),
        'duration_s': 2.5 * 3600,
        'lat': 16.5000,
        'lon': 81.8000
    }
    
    # 6. Micro-move inside customer farm: 13:18 to 13:24 (6 mins transit, 1.4 km)
    t_micro_move = 6 * 60 # 360s
    
    # 7. Customer Field Plot 4B (testing baler knots): 13:24 to 15:34 (2.167 hrs = 7800s)
    t_field_start = t_cust_start + timedelta(hours=2.5, minutes=6)
    stop_cust_2 = {
        'id': 'STOP-4',
        'name': 'RIL Field Plot 4B',
        'start_time': t_field_start,
        'end_time': t_field_start + timedelta(minutes=130),
        'duration_s': 130 * 60, # 7800s
        'lat': 16.5120,
        'lon': 81.8090 # 1.63 km from Main Workshop
    }
    
    # 8. Shift wrap-up & Clock-Out: 15:34 to 16:00 (26 min wrapup at site office)
    stop_cust_3 = {
        'id': 'STOP-5',
        'name': 'RIL Site Office (Customer Sign-off & Invoicing)',
        'start_time': t_field_start + timedelta(minutes=130),
        'end_time': t0 + timedelta(hours=8), # Exactly 16:00
        'duration_s': 26 * 60, # 1560s
        'lat': 16.5010,
        'lon': 81.8005
    }
    
    raw_stops = [stop_base, stop_unauth, stop_cust_1, stop_cust_2, stop_cust_3]
    
    # Run 5km clustering
    clusters = cluster_stops_5km(raw_stops, max_radius_km=5.0)
    
    # Route Inspection
    classified_zones = []
    working_time_s = 0.0
    unauth_time_s = 0.0
    base_time_s = 0.0
    
    for c in clusters:
        dist_base = haversine(c['centroid_lat'], c['centroid_lon'], base_loc['lat'], base_loc['lon'])
        dist_cust = haversine(c['centroid_lat'], c['centroid_lon'], customer_loc['lat'], customer_loc['lon'])
        
        if dist_base <= 5.0:
            c['zone_type'] = 'STARTING_BASE'
            base_time_s += c['total_duration_s']
        elif dist_cust <= 5.0:
            c['zone_type'] = 'CUSTOMER_DESTINATION'
            working_time_s += c['total_duration_s']
        else:
            if c['total_duration_s'] > 900:
                c['zone_type'] = 'UNAUTHORIZED_STOP'
                c['anomaly'] = True
                unauth_time_s += c['total_duration_s']
            else:
                c['zone_type'] = 'AUTHORIZED_TRANSIT_STOP'
                c['anomaly'] = False
        classified_zones.append(c)
        
    # Telematics transit time: Leg 1 + Leg 2 + on-site micro transit
    authorized_transit_s = t_travel_1 + t_travel_2 + t_micro_move
    
    # Shift duration: 08:00 to 16:00 = 8.00 hours = 28800 seconds
    shift_total_s = (t0 + timedelta(hours=8) - t0).total_seconds()
    
    # Productivity math:
    # Working hours: Customer site productive time (all merged stops in customer 5km zone)
    H_work = working_time_s / 3600.0
    # Travelling hours: Active moving transit time on authorized route
    H_travel = authorized_transit_s / 3600.0
    # Idle hours: Unauthorized stop duration + base idle time
    H_idle = (unauth_time_s + base_time_s) / 3600.0
    
    H_shift = shift_total_s / 3600.0
    
    print("=== TELEMATICS & HOURS VERIFICATION SUMMARY ===")
    print(f"Shift Total: {H_shift:.4f} hrs (Exact 8.00 hrs)")
    print(f"Working Hours (on-site productive): {H_work:.4f} hrs")
    print(f"Travelling Hours (active transit):  {H_travel:.4f} hrs")
    print(f"Idle Hours (unauth + base idle):    {H_idle:.4f} hrs")
    print(f"Sum (Work + Travel + Idle):         {H_work + H_travel + H_idle:.4f} hrs")
    print(f"Conservation Error:                 {abs(H_shift - (H_work + H_travel + H_idle)):.8f} hrs")
    print("\n--- CLUSTERS GENERATED ---")
    for c in classified_zones:
        s_names = [s['name'] for s in c['stops']]
        print(f"Zone ID: {c['cluster_id']} | Type: {c['zone_type']:20} | Duration: {c['total_duration_s']/3600:.2f} hrs | Stops merged: {len(c['stops'])}")
        print(f"  Centroid: ({c['centroid_lat']:.4f}, {c['centroid_lon']:.4f})")
        print(f"  Stops: {s_names}")

if __name__ == '__main__':
    run_telematics_simulation()
