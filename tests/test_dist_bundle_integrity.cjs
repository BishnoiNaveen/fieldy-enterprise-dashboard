/**
 * tests/test_dist_bundle_integrity.cjs
 * Empirical verification harness for frontend/dist bundle integrity and asset references.
 */

const fs = require('fs');
const path = require('path');

const distDir = path.resolve(__dirname, '../frontend/dist');
const assetsDir = path.join(distDir, 'assets');

console.log('=== DIST BUNDLE INTEGRITY AUDIT ===');
console.log('Target dist directory:', distDir);

let failures = [];

// 1. Verify index.html
const indexPath = path.join(distDir, 'index.html');
if (!fs.existsSync(indexPath)) {
  failures.push('Missing dist/index.html');
} else {
  const html = fs.readFileSync(indexPath, 'utf8');
  console.log('✓ dist/index.html exists (size:', html.length, 'bytes)');
  
  if (!html.includes('<!doctype html>')) failures.push('index.html missing <!doctype html>');
  if (!html.includes('<div id="root"></div>')) failures.push('index.html missing <div id="root">');
  if (!html.includes('Krone Agriculture India')) failures.push('index.html missing Krone branding title');

  // Check script tags
  const scriptMatch = html.match(/src="([^"]+\.js)"/);
  if (!scriptMatch) {
    failures.push('index.html missing JS script bundle reference');
  } else {
    const jsRelPath = scriptMatch[1].replace(/^\//, '');
    const jsFullPath = path.join(distDir, jsRelPath);
    if (!fs.existsSync(jsFullPath)) {
      failures.push(`Referenced JS file does not exist: ${jsRelPath}`);
    } else {
      console.log(`✓ Referenced JS bundle exists: ${jsRelPath} (${fs.statSync(jsFullPath).size} bytes)`);
    }
  }

  // Check CSS links
  const cssMatches = html.match(/href="([^"]+\.css)"/g) || [];
  cssMatches.forEach((m) => {
    const href = m.match(/href="([^"]+)"/)[1];
    if (href.startsWith('http')) {
      console.log(`✓ External CSS link: ${href}`);
    } else {
      const cssRel = href.replace(/^\//, '');
      const cssFullPath = path.join(distDir, cssRel);
      if (!fs.existsSync(cssFullPath)) {
        failures.push(`Referenced CSS file does not exist: ${cssRel}`);
      } else {
        console.log(`✓ Referenced CSS asset exists: ${cssRel} (${fs.statSync(cssFullPath).size} bytes)`);
      }
    }
  });

  // Check Favicon
  const faviconMatch = html.match(/href="([^"]+\.svg)"/);
  if (faviconMatch) {
    const favRel = faviconMatch[1].replace(/^\//, '');
    const favFullPath = path.join(distDir, favRel);
    if (!fs.existsSync(favFullPath)) {
      failures.push(`Referenced favicon does not exist: ${favRel}`);
    } else {
      console.log(`✓ Referenced favicon exists: ${favRel} (${fs.statSync(favFullPath).size} bytes)`);
    }
  }
}

// 2. Scan JS bundle
const jsFiles = fs.readdirSync(assetsDir).filter(f => f.endsWith('.js'));
if (jsFiles.length === 0) {
  failures.push('No JS bundle found in dist/assets');
} else {
  const mainJs = path.join(assetsDir, jsFiles[0]);
  const jsContent = fs.readFileSync(mainJs, 'utf8');
  console.log(`\nInspecting JS bundle: ${jsFiles[0]} (${jsContent.length} bytes)`);

  // Check for custom Leaflet divIcons
  const divIconHits = (jsContent.match(/custom-leaflet-icon/g) || []).length;
  console.log(`✓ Found ${divIconHits} occurrences of 'custom-leaflet-icon' in JS bundle`);
  if (divIconHits === 0) {
    failures.push('Expected custom-leaflet-icon references in JS bundle');
  }

  // Check for Krone branding strings
  const kroneStrings = ['Krone BigPack', 'Reliance Industries', 'Autonomous Route Inspector', '5 km Geofence'];
  kroneStrings.forEach(s => {
    if (jsContent.includes(s)) {
      console.log(`✓ Found expected domain text in JS: "${s}"`);
    } else {
      failures.push(`Missing expected domain text in JS: "${s}"`);
    }
  });
}

// 3. Scan CSS bundle
const cssFiles = fs.readdirSync(assetsDir).filter(f => f.endsWith('.css'));
if (cssFiles.length === 0) {
  failures.push('No CSS bundle found in dist/assets');
} else {
  const mainCss = path.join(assetsDir, cssFiles[0]);
  const cssContent = fs.readFileSync(mainCss, 'utf8');
  console.log(`\nInspecting CSS bundle: ${cssFiles[0]} (${cssContent.length} bytes)`);

  // Check Leaflet styles
  const requiredSelectors = ['.leaflet-container', '.custom-leaflet-icon', '.custom-leaflet-popup'];
  requiredSelectors.forEach(sel => {
    if (cssContent.includes(sel)) {
      console.log(`✓ CSS contains required selector: "${sel}"`);
    } else {
      failures.push(`CSS missing selector: "${sel}"`);
    }
  });

  // Check url() asset links in CSS
  const urls = cssContent.match(/url\(([^)]+)\)/g) || [];
  console.log(`Found ${urls.length} url() references in CSS:`, urls);
  urls.forEach(u => {
    const rawUrl = u.replace(/^url\(["']?/, '').replace(/["']?\)$/, '');
    if (rawUrl.startsWith('data:') || rawUrl.startsWith('http') || rawUrl.startsWith('#')) {
      console.log(`✓ Safe fragment/external/data URI: ${rawUrl.substring(0, 40)}...`);
    } else {
      const resolved = path.resolve(assetsDir, rawUrl);
      if (!fs.existsSync(resolved)) {
        failures.push(`Broken CSS asset URL: ${rawUrl} (resolved: ${resolved})`);
      } else {
        console.log(`✓ Valid local CSS asset URL: ${rawUrl}`);
      }
    }
  });
}

// 4. Check for broken Leaflet Marker default icon usage across source components
console.log('\n--- Checking Marker Icon definitions in Source Components ---');
const srcDir = path.resolve(__dirname, '../frontend/src');
function findFiles(dir, filter) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const full = path.join(dir, file);
    const stat = fs.statSync(full);
    if (stat && stat.isDirectory()) {
      results = results.concat(findFiles(full, filter));
    } else if (filter(full)) {
      results.push(full);
    }
  });
  return results;
}

const tsxFiles = findFiles(srcDir, f => f.endsWith('.tsx'));
let markerCount = 0;
let markersWithCustomIcon = 0;

tsxFiles.forEach(file => {
  const content = fs.readFileSync(file, 'utf8');
  const lines = content.split('\n');
  lines.forEach((line, idx) => {
    if (line.includes('<Marker')) {
      markerCount++;
      // Check surrounding lines (up to 5 lines ahead) for icon= prop
      const chunk = lines.slice(idx, idx + 6).join(' ');
      if (chunk.includes('icon={')) {
        markersWithCustomIcon++;
      } else {
        failures.push(`Marker at ${path.relative(srcDir, file)}:${idx + 1} does not have explicit icon={...} prop! This triggers broken default Leaflet PNGs!`);
      }
    }
  });
});

console.log(`Total <Marker> instances across frontend: ${markerCount}`);
console.log(`Markers with explicit custom SVG divIcon: ${markersWithCustomIcon}`);

if (markerCount > 0 && markerCount === markersWithCustomIcon) {
  console.log('✓ 100% of Leaflet <Marker> components explicitly use custom divIcons! Zero default PNG fallbacks.');
}

console.log('\n=== AUDIT RESULTS SUMMARY ===');
if (failures.length > 0) {
  console.error(`FAILURES DETECTED (${failures.length}):`);
  failures.forEach(f => console.error(`  ❌ ${f}`));
  process.exit(1);
} else {
  console.log('ALL BUNDLE AND ASSET INTEGRITY CHECKS PASSED EMPIRICALLY (0 failures).');
  process.exit(0);
}
