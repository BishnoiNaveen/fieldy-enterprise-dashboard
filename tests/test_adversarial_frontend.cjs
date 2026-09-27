/**
 * tests/test_adversarial_frontend.cjs
 * Adversarial stress testing for API resilience, timeouts, server errors, and schema contract validation.
 */

const http = require('http');
const path = require('path');
const createJiti = require('../frontend/node_modules/jiti');

const jiti = createJiti(__filename, {
  esmResolve: true,
  interopDefault: true,
});

async function runAdversarialSuite() {
  console.log('=== STARTING ADVERSARIAL FRONTEND STRESS TEST SUITE ===\n');
  let testCount = 0;
  let passCount = 0;
  let failCount = 0;

  function assert(condition, testName) {
    testCount++;
    if (condition) {
      passCount++;
      console.log(`  [PASS] Test ${testCount}: ${testName}`);
    } else {
      failCount++;
      console.error(`  [FAIL] Test ${testCount}: ${testName}`);
    }
  }

  const { api, getBackendLiveStatus } = jiti('../frontend/src/services/api.ts');

  // -------------------------------------------------------------
  // Scenario 1: HTTP 500 Internal Server Error Adversarial Mock
  // -------------------------------------------------------------
  console.log('Scenario 1: Backend returns HTTP 500 Internal Server Error');
  const server500 = http.createServer((req, res) => {
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ detail: 'Fatal DB Connection Failure in Fieldy Synchronizer' }));
  });

  await new Promise(resolve => server500.listen(8000, resolve));
  console.log('  Adversarial server listening on port 8000 (HTTP 500 generator)');

  try {
    const pulse500 = await api.getPulse();
    assert(pulse500 && pulse500.kpis && pulse500.kpis.technicians_on_paid_jobs === 8, 'getPulse() gracefully recovers from HTTP 500 error');
    assert(getBackendLiveStatus() === false, 'isBackendLive is false after HTTP 500');

    const sync500 = await api.triggerSync(true);
    assert(sync500 && sync500.status === 'success' && sync500.source === 'fieldy_cache', 'triggerSync() gracefully recovers from HTTP 500 error');

    const prod500 = await api.getProductivity({ timeframe: 'daily' });
    assert(prod500 && prod500.summary && prod500.summary.total_working_hours === 64.5, 'getProductivity() gracefully recovers from HTTP 500 error');

    const route500 = await api.getRoute('TECH-01');
    assert(route500 && route500.journey_summary && route500.journey_summary.transit_duration_minutes === 105, 'getRoute() gracefully recovers from HTTP 500 error');

    const techs500 = await api.getTechnicians();
    assert(Array.isArray(techs500) && techs500.length > 0, 'getTechnicians() gracefully recovers from HTTP 500 error');

    const jobs500 = await api.getJobs();
    assert(Array.isArray(jobs500) && jobs500.length > 0, 'getJobs() gracefully recovers from HTTP 500 error');
  } finally {
    await new Promise(resolve => server500.close(resolve));
    console.log('  HTTP 500 server closed\n');
  }

  // -------------------------------------------------------------
  // Scenario 2: HTTP 502 Bad Gateway with Malformed HTML body
  // -------------------------------------------------------------
  console.log('Scenario 2: Backend returns HTTP 502 with HTML Error Page (Proxy crash)');
  const server502 = http.createServer((req, res) => {
    res.writeHead(502, { 'Content-Type': 'text/html' });
    res.end('<html><head><title>502 Bad Gateway</title></head><body><center><h1>502 Bad Gateway</h1></center></body></html>');
  });

  await new Promise(resolve => server502.listen(8000, resolve));
  console.log('  Adversarial server listening on port 8000 (HTML 502 generator)');

  try {
    const pulse502 = await api.getPulse();
    assert(pulse502 && pulse502.kpis && pulse502.kpis.technicians_active_total === 12, 'getPulse() gracefully recovers from HTML 502 Bad Gateway');

    const prod502 = await api.getProductivity({ timeframe: 'weekly' });
    assert(prod502 && prod502.summary && prod502.summary.average_utilization_pct === 67.2, 'getProductivity() gracefully recovers from HTML 502 Bad Gateway');
  } finally {
    await new Promise(resolve => server502.close(resolve));
    console.log('  HTTP 502 server closed\n');
  }

  // -------------------------------------------------------------
  // Scenario 3: High-Concurrency Burst Stress Test (50 simultaneous calls)
  // -------------------------------------------------------------
  console.log('Scenario 3: 50-Request Concurrent Burst under offline conditions');
  const burstPromises = [];
  for (let i = 0; i < 20; i++) {
    burstPromises.push(api.getPulse());
    burstPromises.push(api.getProductivity({ timeframe: 'daily' }));
  }
  for (let i = 0; i < 10; i++) {
    burstPromises.push(api.getRoute('TECH-01'));
  }

  const results = await Promise.allSettled(burstPromises);
  const rejectedCount = results.filter(r => r.status === 'rejected').length;
  const fulfilledCount = results.filter(r => r.status === 'fulfilled').length;

  assert(rejectedCount === 0, 'Zero promises rejected during 50-call concurrent burst');
  assert(fulfilledCount === 50, 'All 50 concurrent calls successfully fulfilled with fallback data');
  console.log(`  Burst completed: ${fulfilledCount} fulfilled, ${rejectedCount} rejected\n`);

  // -------------------------------------------------------------
  // Scenario 4: Deep Contract & Type Validation of Fallback Data
  // -------------------------------------------------------------
  console.log('Scenario 4: Fallback Data Schema & Invariant Verification');
  const pulse = await api.getPulse();
  const prod = await api.getProductivity();
  const route = await api.getRoute('TECH-01');

  // Invariant 1: Pulse KPI numbers are non-negative
  const kpis = pulse.kpis;
  assert(
    kpis.technicians_on_paid_jobs >= 0 &&
    kpis.technicians_active_total >= 0 &&
    kpis.technicians_on_leave >= 0 &&
    kpis.total_jobs_today >= 0 &&
    kpis.jobs_completed_today >= 0,
    'All Pulse KPIs are non-negative integers'
  );

  // Invariant 2: Active technicians >= technicians on paid jobs
  assert(
    kpis.technicians_active_total >= kpis.technicians_on_paid_jobs,
    'Fleet invariant: Total active techs >= techs currently on paid jobs'
  );

  // Invariant 3: Machinery contact person and serial number formatting
  assert(
    pulse.machines_under_service.every(m => m.serial_number && m.serial_number.length >= 7),
    'All machines under service have valid serial numbers (>= 7 chars)'
  );
  assert(
    pulse.machines_under_service.every(m => m.site_contact_person && m.site_contact_person.includes('+91')),
    'All machines under service have valid contact phone formatted with +91'
  );

  // Invariant 4: Hours conservation across technician productivity records
  const techRecords = prod.technician_records;
  const hoursConserved = techRecords.every(t => {
    const sum = t.working_hours + t.travelling_hours + t.idle_hours;
    return Math.abs(sum - t.shift_hours) < 0.01;
  });
  assert(hoursConserved, 'Every individual technician record satisfies H_shift = H_w + H_t + H_i');

  // Invariant 5: Route polyline and 5 km clusters coordinate validity
  assert(
    route.route_polyline.every(pt => Array.isArray(pt) && pt.length === 2 && pt[0] > 0 && pt[1] > 0),
    'Every point in route_polyline has valid positive [lat, lng] coordinates'
  );

  assert(
    route.clusters_5km.every(c => c.radius_meters > 0 && c.centroid.lat > 0 && c.centroid.lng > 0),
    'Every 5 km cluster has valid positive centroid and radius'
  );

  assert(
    route.anomalies.every(a => a.duration_minutes > 15),
    'All detected anomalies represent unscheduled stops exceeding the 15-minute threshold'
  );

  // -------------------------------------------------------------
  // Summary
  // -------------------------------------------------------------
  console.log('\n=== ADVERSARIAL STRESS TEST SUMMARY ===');
  console.log(`Total Scenarios Tested: ${testCount}`);
  console.log(`Passed: ${passCount}`);
  console.log(`Failed: ${failCount}`);

  if (failCount > 0) {
    console.error('CRITICAL: Adversarial stress testing uncovered vulnerabilities!');
    process.exit(1);
  } else {
    console.log('SUCCESS: All adversarial stress tests passed. Frontend API resilience verified.');
    process.exit(0);
  }
}

runAdversarialSuite().catch(err => {
  console.error('FATAL UNCAUGHT ERROR:', err);
  process.exit(1);
});
