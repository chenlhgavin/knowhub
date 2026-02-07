#!/usr/bin/env node

/**
 * Design Guide Workflow - Complete Pipeline
 * Orchestrates: Extract -> Generate Guide -> Build Replica -> Compare -> Iterate
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const url = args[0];

if (!url) {
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║           Design Guide Extraction & Replication Tool             ║
╠══════════════════════════════════════════════════════════════════╣
║  Usage: node workflow.js <URL> [options]                         ║
║                                                                  ║
║  Options:                                                        ║
║    --output <dir>     Output directory (default: auto-generated)║
║    --skip-extract     Skip extraction if data exists             ║
║    --skip-replica     Skip replica generation                    ║
║    --interact         Enable interaction mode for hover states   ║
║                                                                  ║
║  Examples:                                                       ║
║    node workflow.js https://stripe.com                           ║
║    node workflow.js https://example.com --interact               ║
╚══════════════════════════════════════════════════════════════════╝
  `);
  process.exit(1);
}

// Parse URL to get site name
const siteName = new URL(url).hostname.replace('www.', '').replace(/\./g, '-');
const skillDir = path.dirname(__dirname);
const scriptsDir = __dirname;
const defaultOutput = path.join(skillDir, 'output', siteName);
const tempDir = '/tmp/design-extract';

// Parse options
let outputDir = defaultOutput;
let skipExtract = false;
let skipReplica = false;
let interact = false;

for (let i = 1; i < args.length; i++) {
  if (args[i] === '--output' && args[i + 1]) outputDir = args[++i];
  if (args[i] === '--skip-extract') skipExtract = true;
  if (args[i] === '--skip-replica') skipReplica = true;
  if (args[i] === '--interact') interact = true;
}

console.log(`
╔══════════════════════════════════════════════════════════════════╗
║                   Design Guide Workflow                          ║
╠══════════════════════════════════════════════════════════════════╣
║  URL: ${url.padEnd(55)}║
║  Site: ${siteName.padEnd(54)}║
║  Output: ${outputDir.substring(0, 52).padEnd(52)}║
╚══════════════════════════════════════════════════════════════════╝
`);

// Ensure directories exist
fs.mkdirSync(tempDir, { recursive: true });
fs.mkdirSync(outputDir, { recursive: true });
fs.mkdirSync(path.join(outputDir, 'screenshots'), { recursive: true });

async function runStep(stepNum, title, fn) {
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`Step ${stepNum}: ${title}`);
  console.log('─'.repeat(60));
  try {
    await fn();
    console.log(`✅ Step ${stepNum} completed`);
    return true;
  } catch (error) {
    console.error(`❌ Step ${stepNum} failed: ${error.message}`);
    return false;
  }
}

async function main() {
  const startTime = Date.now();

  // Step 1: Extract Design
  if (!skipExtract) {
    const extractResult = await runStep(1, 'Extracting Design Data', async () => {
      const cmd = `node "${path.join(scriptsDir, 'extract_design.js')}" "${url}" --output "${tempDir}" ${interact ? '--interact' : ''}`;
      execSync(cmd, { stdio: 'inherit' });
    });
    if (!extractResult) process.exit(1);
  } else {
    console.log('\n⏭️  Skipping extraction (--skip-extract)');
  }

  // Step 2: Generate Design Guide
  const guideResult = await runStep(2, 'Generating Design Guide', async () => {
    const cmd = `node "${path.join(scriptsDir, 'generate_guide.js')}" "${path.join(tempDir, 'design-data.json')}" "${path.join(outputDir, 'design-guide.md')}"`;
    execSync(cmd, { stdio: 'inherit' });
  });
  if (!guideResult) process.exit(1);

  // Copy screenshots
  console.log('\n📸 Copying screenshots...');
  ['screenshot-viewport.png', 'screenshot-full.png'].forEach(file => {
    const src = path.join(tempDir, file);
    const dest = path.join(outputDir, 'screenshots', file);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
      console.log(`   Copied: ${file}`);
    }
  });

  // Copy design tokens
  const tokensSource = path.join(tempDir, 'design-tokens.css');
  if (fs.existsSync(tokensSource)) {
    fs.copyFileSync(tokensSource, path.join(outputDir, 'design-tokens.css'));
    console.log('   Copied: design-tokens.css');
  }

  // Copy raw data
  const dataSource = path.join(tempDir, 'design-data.json');
  if (fs.existsSync(dataSource)) {
    fs.copyFileSync(dataSource, path.join(outputDir, 'design-data.json'));
    console.log('   Copied: design-data.json');
  }

  // Summary
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log(`
╔══════════════════════════════════════════════════════════════════╗
║                      Workflow Complete                           ║
╠══════════════════════════════════════════════════════════════════╣
║  Total time: ${elapsed.padEnd(10)}seconds                                  ║
║                                                                  ║
║  Output Files:                                                   ║
║    📄 design-guide.md      - Complete design documentation       ║
║    🎨 design-tokens.css    - CSS custom properties               ║
║    📊 design-data.json     - Raw extracted data                  ║
║    📸 screenshots/         - Reference screenshots               ║
║                                                                  ║
║  Next Steps:                                                     ║
║    1. Review design-guide.md for design tokens                   ║
║    2. Create index.html replica using the guide                  ║
║    3. Run comparison to validate pixel-perfection                ║
║                                                                  ║
║  Compare Command:                                                ║
║    node compare_screenshots.js \\                                 ║
║      "${path.join(outputDir, 'screenshots/screenshot-viewport.png')}" \\
║      "/tmp/test.html"                                            ║
╚══════════════════════════════════════════════════════════════════╝
`);

  console.log(`\n📁 All files saved to: ${outputDir}\n`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
