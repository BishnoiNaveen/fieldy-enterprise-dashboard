/**
 * tests/test_offline_api.cjs
 * Empirical verification harness for frontend/src/services/api.ts offline fallback.
 */

const path = require('path');
const createJiti = require('../frontend/node_modules/jiti');

const jiti = createJiti(__filename, {
  esmResolve: true,
  interopDefault: true,
});

async function run() {
  console.log('Testing api.ts offline fallback...');
  try {
    const apiModule = jiti('../frontend/src/services/api.ts');
    console.log('Successfully loaded api.ts');
    console.log('Exported keys:', Object.keys(apiModule));

    const { api, getBackendLiveStatus } = apiModule;

    // Test 1: getPulse with backend down
    console.log('\n--- 1. Testing getPulse() fallback ---');
    const pulse = await api.getPulse();
    console.log('Pulse received:', {
      timestamp: pulse.timestamp,
      kpis: pulse.kpis,
      techCount: pulse.technicians_on_jobs?.length,
      jobsCount: pulse.today_jobs?.length,
      machinesCount: pulse.machines_under_service?.length,
    });
    if (!pulse || !pulse.kpis || pulse.kpis.technicians_on_paid_jobs !== 8) {
      throw new Error('Invalid pulse fallback data');
    }
    console.log('Assertion PASSED: pulse data matches calibrated Krone synthetic dataset.');

    // Test 2: triggerSync with backend down
    console.log('\n--- 2. Testing triggerSync() fallback ---');
    const syncRes = await api.triggerSync(true);
    console.log('Sync response received:', syncRes);
    if (!syncRes || syncRes.status !== 'success' || syncRes.source !== 'fieldy_cache') {
      throw new Error('Invalid sync fallback data');
    }
    console.log('Assertion PASSED: triggerSync fallback returned valid sync response.');

    // Test 3: getProductivity with backend down
    console.log('\n--- 3. Testing getProductivity() fallback ---');
    const prod = await api.getProductivity({ timeframe: 'daily' });
    console.log('Productivity summary received:', prod.summary);
    if (!prod || !prod.summary || prod.summary.total_shift_hours !== 96.0) {
      throw new Error('Invalid productivity fallback data');
    }
    // Verify hours conservation
    const { total_working_hours, total_travelling_hours, total_idle_hours, total_shift_hours } = prod.summary;
    const sumHours = total_working_hours + total_travelling_hours + total_idle_hours;
    console.log(`Hours conservation check: ${total_working_hours} + ${total_travelling_hours} + ${total_idle_hours} = ${sumHours} (shift = ${total_shift_hours})`);
    if (Math.abs(sumHours - total_shift_hours) > 0.001) {
      throw new Error('Productivity hours conservation violated!');
    }
    console.log('Assertion PASSED: hours conservation strictly preserved in fallback data.');

    // Test 4: getRoute with backend down
    console.log('\n--- 4. Testing getRoute() fallback ---');
    const route = await api.getRoute('TECH-01', '2026-09-22');
    console.log('Route summary:', route.journey_summary);
    console.log('Clusters count:', route.clusters_5km?.length);
    console.log('Anomalies count:', route.anomalies?.length);
    console.log('Polyline length:', route.route_polyline?.length);
    if (!route || !route.journey_summary || route.journey_summary.transit_duration_minutes !== 105) {
      throw new Error('Invalid route fallback data');
    }
    console.log('Assertion PASSED: route fallback data matches Krone telematics corridor.');

    // Test 5: getTechnicians with backend down
    console.log('\n--- 5. Testing getTechnicians() fallback ---');
    const techs = await api.getTechnicians();
    console.log('Technicians count:', techs?.length);
    if (!techs || techs.length < 2) {
      throw new Error('Invalid technicians fallback data');
    }
    console.log('Assertion PASSED: technicians fallback returned valid list.');

    // Test 6: getJobs with backend down
    console.log('\n--- 6. Testing getJobs() fallback ---');
    const jobs = await api.getJobs();
    console.log('Jobs count:', jobs?.length);
    if (!jobs || jobs.length < 1) {
      throw new Error('Invalid jobs fallback data');
    }
    console.log('Assertion PASSED: jobs fallback returned valid list.');

    // Test 7: Backend live status check
    const status = getBackendLiveStatus();
    console.log('\nBackend live status after failed calls:', status);
    if (status !== false) {
      throw new Error('Expected isBackendLive to be false after offline fallbacks!');
    }
    console.log('Assertion PASSED: isBackendLive correctly transitioned to false.');

    console.log('\n=== ALL 7 OFFLINE FALLBACK TESTS PASSED EMPIRICALLY ===');
    process.exit(0);
  } catch (err) {
    console.error('FAILED with error:', err);
    process.exit(1);
  }
}

run();
