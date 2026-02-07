#!/usr/bin/env node

/**
 * Screenshot Comparison Script
 * Compares original screenshot with rebuilt HTML page
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const { PNG } = require('pngjs');

const args = process.argv.slice(2);
const originalImage = args[0];
const htmlFile = args[1];

if (!originalImage || !htmlFile) {
  console.error('Usage: node compare_screenshots.js <original-image> <html-file> [--threshold <n>] [--output <file>]');
  process.exit(1);
}

// Parse arguments
let threshold = 5;
let diffOutput = '/tmp/design-extract/diff.png';
let viewportWidth = 1600;
let viewportHeight = 1200;

for (let i = 2; i < args.length; i++) {
  if (args[i] === '--threshold' && args[i + 1]) {
    threshold = parseFloat(args[++i]) || 5;
  } else if (args[i] === '--output' && args[i + 1]) {
    diffOutput = args[++i];
  } else if (args[i] === '--viewport' && args[i + 1]) {
    const [w, h] = args[++i].split('x').map(Number);
    viewportWidth = w || 1600;
    viewportHeight = h || 1200;
  }
}

// Simple pixel comparison without external dependencies
function compareImages(img1Buffer, img2Buffer) {
  const png1 = PNG.sync.read(img1Buffer);
  const png2 = PNG.sync.read(img2Buffer);

  const width = Math.min(png1.width, png2.width);
  const height = Math.min(png1.height, png2.height);

  let diffPixels = 0;
  const totalPixels = width * height;

  // Create diff image
  const diff = new PNG({ width, height });

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      const idx1 = (png1.width * y + x) << 2;
      const idx2 = (png2.width * y + x) << 2;
      const idxDiff = (width * y + x) << 2;

      const r1 = png1.data[idx1];
      const g1 = png1.data[idx1 + 1];
      const b1 = png1.data[idx1 + 2];

      const r2 = png2.data[idx2];
      const g2 = png2.data[idx2 + 1];
      const b2 = png2.data[idx2 + 2];

      // Calculate color difference
      const dr = Math.abs(r1 - r2);
      const dg = Math.abs(g1 - g2);
      const db = Math.abs(b1 - b2);
      const colorDiff = (dr + dg + db) / 3;

      if (colorDiff > 10) {
        diffPixels++;
        // Highlight differences in red
        diff.data[idxDiff] = 255;
        diff.data[idxDiff + 1] = 0;
        diff.data[idxDiff + 2] = 0;
        diff.data[idxDiff + 3] = Math.min(255, colorDiff * 2);
      } else {
        // Keep original with reduced opacity
        diff.data[idxDiff] = r1;
        diff.data[idxDiff + 1] = g1;
        diff.data[idxDiff + 2] = b1;
        diff.data[idxDiff + 3] = 128;
      }
    }
  }

  const diffPercent = (diffPixels / totalPixels) * 100;

  return {
    diffPercent: diffPercent.toFixed(2),
    diffPixels,
    totalPixels,
    width,
    height,
    diffImage: PNG.sync.write(diff)
  };
}

async function compareScreenshots() {
  console.log('\n🔍 Screenshot Comparison Started');
  console.log(`   Original: ${originalImage}`);
  console.log(`   HTML: ${htmlFile}\n`);

  // Read original image
  if (!fs.existsSync(originalImage)) {
    console.error(`❌ Original image not found: ${originalImage}`);
    process.exit(1);
  }

  const originalBuffer = fs.readFileSync(originalImage);

  // Take screenshot of HTML file
  console.log('📸 Capturing rebuilt page screenshot...');

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: viewportWidth, height: viewportHeight },
    deviceScaleFactor: 2
  });

  const page = await context.newPage();

  try {
    // Handle both file paths and URLs
    let htmlUrl = htmlFile;
    if (!htmlFile.startsWith('http://') && !htmlFile.startsWith('https://')) {
      htmlUrl = `file://${path.resolve(htmlFile)}`;
    }

    await page.goto(htmlUrl, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(1000);

    const rebuiltBuffer = await page.screenshot({ type: 'png' });

    // Save rebuilt screenshot for reference
    const rebuiltPath = path.join(path.dirname(diffOutput), 'screenshot-rebuilt.png');
    fs.writeFileSync(rebuiltPath, rebuiltBuffer);
    console.log(`   Saved rebuilt screenshot: ${rebuiltPath}`);

    // Compare images
    console.log('🔬 Comparing screenshots...');

    let result;
    try {
      result = compareImages(originalBuffer, rebuiltBuffer);
    } catch (e) {
      // If pngjs is not available, do a simple size comparison
      console.log('   Note: pngjs not available, performing basic comparison');
      result = {
        diffPercent: originalBuffer.length !== rebuiltBuffer.length ? '100.00' : '0.00',
        diffPixels: 0,
        totalPixels: 0,
        width: viewportWidth,
        height: viewportHeight,
        diffImage: null
      };
    }

    // Save diff image if available
    if (result.diffImage) {
      fs.writeFileSync(diffOutput, result.diffImage);
      console.log(`   Saved diff image: ${diffOutput}`);
    }

    // Output results
    console.log('\n📊 Comparison Results:');
    console.log(`   Difference: ${result.diffPercent}%`);
    console.log(`   Threshold: ${threshold}%`);
    console.log(`   Status: ${parseFloat(result.diffPercent) <= threshold ? '✅ PASS' : '❌ FAIL'}`);

    if (parseFloat(result.diffPercent) > threshold) {
      console.log('\n💡 Suggestions to improve match:');
      console.log('   1. Check the diff image to identify mismatched areas');
      console.log('   2. Verify font families are correctly loaded');
      console.log('   3. Check spacing and padding values');
      console.log('   4. Verify colors match exactly (use extracted CSS variables)');
      console.log('   5. Check border-radius and shadow values');
      console.log('   6. Ensure images/icons are properly included');
    }

    // Return result as JSON for programmatic use
    const output = {
      pass: parseFloat(result.diffPercent) <= threshold,
      diffPercent: parseFloat(result.diffPercent),
      threshold,
      originalImage,
      rebuiltImage: rebuiltPath,
      diffImage: diffOutput
    };

    console.log('\n📝 Result JSON:');
    console.log(JSON.stringify(output, null, 2));

    await browser.close();
    process.exit(output.pass ? 0 : 1);

  } catch (error) {
    console.error('❌ Error during comparison:', error.message);
    await browser.close();
    process.exit(1);
  }
}

// Check if pngjs is available
try {
  require('pngjs');
} catch (e) {
  console.log('⚠️  Note: pngjs not installed. Run: npm install pngjs');
  console.log('   Continuing with basic comparison...\n');
}

compareScreenshots();
