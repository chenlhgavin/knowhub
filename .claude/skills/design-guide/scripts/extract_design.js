#!/usr/bin/env node

/**
 * Design Extraction Script
 * Extracts comprehensive design data from a website using Playwright
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const url = args[0];

if (!url) {
  console.error('Usage: node extract_design.js <URL> [--output <dir>] [--viewport <WxH>] [--wait <ms>] [--interact]');
  process.exit(1);
}

// Parse arguments
let outputDir = '/tmp/design-extract';
let viewportWidth = 1600;
let viewportHeight = 1200;
let waitTime = 2000;
let interactMode = false;

for (let i = 1; i < args.length; i++) {
  if (args[i] === '--output' && args[i + 1]) {
    outputDir = args[++i];
  } else if (args[i] === '--viewport' && args[i + 1]) {
    const [w, h] = args[++i].split('x').map(Number);
    viewportWidth = w || 1600;
    viewportHeight = h || 1200;
  } else if (args[i] === '--wait' && args[i + 1]) {
    waitTime = parseInt(args[++i]) || 2000;
  } else if (args[i] === '--interact') {
    interactMode = true;
  }
}

// Ensure output directory exists
fs.mkdirSync(outputDir, { recursive: true });

async function extractDesign() {
  console.log(`\n🎨 Design Extraction Started`);
  console.log(`   URL: ${url}`);
  console.log(`   Output: ${outputDir}`);
  console.log(`   Viewport: ${viewportWidth}x${viewportHeight}\n`);

  const browser = await chromium.launch({
    headless: true,
    args: ['--disable-web-security', '--allow-running-insecure-content']
  });

  const context = await browser.newContext({
    viewport: { width: viewportWidth, height: viewportHeight },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    deviceScaleFactor: 2
  });

  const page = await context.newPage();

  try {
    // Navigate to URL
    console.log('📡 Navigating to URL...');
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    // Wait for additional content to load
    await page.waitForTimeout(5000);

    // Take screenshots
    console.log('📸 Capturing screenshots...');
    await page.screenshot({
      path: path.join(outputDir, 'screenshot-viewport.png'),
      type: 'png'
    });

    await page.screenshot({
      path: path.join(outputDir, 'screenshot-full.png'),
      fullPage: true,
      type: 'png'
    });

    // Extract design data
    console.log('🔍 Extracting design data...');
    const designData = await page.evaluate(() => {
      const data = {
        url: window.location.href,
        title: document.title,
        timestamp: new Date().toISOString(),
        colors: {
          background: new Set(),
          text: new Set(),
          border: new Set(),
          accent: new Set(),
          all: new Set()
        },
        typography: {
          fontFamilies: new Set(),
          fontSizes: new Set(),
          fontWeights: new Set(),
          lineHeights: new Set(),
          letterSpacings: new Set()
        },
        spacing: {
          paddings: new Set(),
          margins: new Set(),
          gaps: new Set()
        },
        effects: {
          boxShadows: new Set(),
          borderRadii: new Set(),
          transitions: new Set(),
          transforms: new Set(),
          filters: new Set()
        },
        layout: {
          maxWidths: new Set(),
          gridTemplates: new Set(),
          flexPatterns: []
        },
        cssVariables: {},
        elements: [],
        animations: [],
        hoverStates: []
      };

      // Helper to parse and normalize colors
      function normalizeColor(color) {
        if (!color || color === 'transparent' || color === 'rgba(0, 0, 0, 0)') return null;
        return color;
      }

      // Helper to parse spacing values
      function parseSpacing(value) {
        if (!value || value === '0px' || value === 'auto' || value === 'normal') return null;
        return value;
      }

      // Extract CSS custom properties (design tokens)
      const rootStyles = getComputedStyle(document.documentElement);
      const allStyleSheets = [...document.styleSheets];

      allStyleSheets.forEach(sheet => {
        try {
          const rules = sheet.cssRules || sheet.rules;
          if (rules) {
            [...rules].forEach(rule => {
              if (rule.type === CSSRule.STYLE_RULE && rule.selectorText === ':root') {
                const style = rule.style;
                for (let i = 0; i < style.length; i++) {
                  const prop = style[i];
                  if (prop.startsWith('--')) {
                    data.cssVariables[prop] = style.getPropertyValue(prop).trim();
                  }
                }
              }
              // Capture keyframe animations
              if (rule.type === CSSRule.KEYFRAMES_RULE) {
                const keyframes = [];
                [...rule.cssRules].forEach(kf => {
                  keyframes.push({
                    offset: kf.keyText,
                    style: kf.style.cssText
                  });
                });
                data.animations.push({
                  name: rule.name,
                  keyframes
                });
              }
            });
          }
        } catch (e) {
          // CORS restrictions on external stylesheets
        }
      });

      // Get all elements and extract their computed styles
      const allElements = document.querySelectorAll('*');
      const elementSamples = new Map();

      allElements.forEach((el, index) => {
        if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.tagName === 'NOSCRIPT') return;

        const style = getComputedStyle(el);
        const rect = el.getBoundingClientRect();

        // Skip invisible elements
        if (rect.width === 0 || rect.height === 0) return;

        // Colors
        const bgColor = normalizeColor(style.backgroundColor);
        const textColor = normalizeColor(style.color);
        const borderColor = normalizeColor(style.borderColor);

        if (bgColor) data.colors.background.add(bgColor);
        if (textColor) data.colors.text.add(textColor);
        if (borderColor && style.borderWidth !== '0px') data.colors.border.add(borderColor);
        [bgColor, textColor, borderColor].filter(Boolean).forEach(c => data.colors.all.add(c));

        // Typography
        data.typography.fontFamilies.add(style.fontFamily);
        data.typography.fontSizes.add(style.fontSize);
        data.typography.fontWeights.add(style.fontWeight);
        if (style.lineHeight !== 'normal') data.typography.lineHeights.add(style.lineHeight);
        if (style.letterSpacing !== 'normal') data.typography.letterSpacings.add(style.letterSpacing);

        // Spacing
        ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft'].forEach(prop => {
          const val = parseSpacing(style[prop]);
          if (val) data.spacing.paddings.add(val);
        });
        ['marginTop', 'marginRight', 'marginBottom', 'marginLeft'].forEach(prop => {
          const val = parseSpacing(style[prop]);
          if (val) data.spacing.margins.add(val);
        });
        const gap = parseSpacing(style.gap);
        if (gap) data.spacing.gaps.add(gap);

        // Effects
        if (style.boxShadow && style.boxShadow !== 'none') {
          data.effects.boxShadows.add(style.boxShadow);
        }
        if (style.borderRadius && style.borderRadius !== '0px') {
          data.effects.borderRadii.add(style.borderRadius);
        }
        if (style.transition && style.transition !== 'all 0s ease 0s' && style.transition !== 'none') {
          data.effects.transitions.add(style.transition);
        }
        if (style.transform && style.transform !== 'none') {
          data.effects.transforms.add(style.transform);
        }
        if (style.filter && style.filter !== 'none') {
          data.effects.filters.add(style.filter);
        }

        // Layout
        if (style.maxWidth && style.maxWidth !== 'none') {
          data.layout.maxWidths.add(style.maxWidth);
        }
        if (style.display === 'grid' && style.gridTemplateColumns !== 'none') {
          data.layout.gridTemplates.add(style.gridTemplateColumns);
        }

        // Sample key elements for pattern detection
        const tagName = el.tagName.toLowerCase();
        const classes = el.className?.toString() || '';

        if (['button', 'a', 'input', 'nav', 'header', 'footer', 'main', 'section', 'article', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'li'].includes(tagName)) {
          const key = `${tagName}${classes ? '.' + classes.split(' ')[0] : ''}`;
          if (!elementSamples.has(key) && elementSamples.size < 100) {
            elementSamples.set(key, {
              tag: tagName,
              classes: classes.split(' ').filter(Boolean).slice(0, 5),
              styles: {
                display: style.display,
                position: style.position,
                width: style.width,
                height: style.height,
                padding: style.padding,
                margin: style.margin,
                backgroundColor: style.backgroundColor,
                color: style.color,
                fontSize: style.fontSize,
                fontWeight: style.fontWeight,
                fontFamily: style.fontFamily,
                borderRadius: style.borderRadius,
                boxShadow: style.boxShadow,
                border: style.border,
                textDecoration: style.textDecoration,
                transition: style.transition
              },
              rect: {
                width: Math.round(rect.width),
                height: Math.round(rect.height),
                x: Math.round(rect.x),
                y: Math.round(rect.y)
              }
            });
          }
        }
      });

      data.elements = [...elementSamples.values()];

      // Convert Sets to Arrays
      Object.keys(data.colors).forEach(key => {
        data.colors[key] = [...data.colors[key]];
      });
      Object.keys(data.typography).forEach(key => {
        data.typography[key] = [...data.typography[key]];
      });
      Object.keys(data.spacing).forEach(key => {
        data.spacing[key] = [...data.spacing[key]];
      });
      Object.keys(data.effects).forEach(key => {
        data.effects[key] = [...data.effects[key]];
      });
      Object.keys(data.layout).forEach(key => {
        if (data.layout[key] instanceof Set) {
          data.layout[key] = [...data.layout[key]];
        }
      });

      // Get page HTML structure (simplified)
      function getStructure(el, depth = 0) {
        if (depth > 4 || !el || el.nodeType !== 1) return null;
        if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'SVG'].includes(el.tagName)) return null;

        const children = [...el.children]
          .map(child => getStructure(child, depth + 1))
          .filter(Boolean)
          .slice(0, 10);

        return {
          tag: el.tagName.toLowerCase(),
          classes: (el.className?.toString() || '').split(' ').filter(Boolean).slice(0, 3),
          id: el.id || undefined,
          children: children.length > 0 ? children : undefined
        };
      }

      data.structure = getStructure(document.body);

      return data;
    });

    // If interact mode, explore hover states
    if (interactMode) {
      console.log('🖱️  Exploring hover states...');
      const interactiveElements = await page.$$('a, button, [role="button"], input, select, [onclick]');

      for (const element of interactiveElements.slice(0, 20)) {
        try {
          const beforeStyle = await element.evaluate(el => {
            const style = getComputedStyle(el);
            return {
              backgroundColor: style.backgroundColor,
              color: style.color,
              boxShadow: style.boxShadow,
              transform: style.transform,
              borderColor: style.borderColor
            };
          });

          await element.hover();
          await page.waitForTimeout(300);

          const afterStyle = await element.evaluate(el => {
            const style = getComputedStyle(el);
            return {
              backgroundColor: style.backgroundColor,
              color: style.color,
              boxShadow: style.boxShadow,
              transform: style.transform,
              borderColor: style.borderColor,
              tag: el.tagName.toLowerCase(),
              classes: el.className?.toString() || ''
            };
          });

          const changes = {};
          let hasChanges = false;
          for (const prop of Object.keys(beforeStyle)) {
            if (beforeStyle[prop] !== afterStyle[prop]) {
              changes[prop] = { from: beforeStyle[prop], to: afterStyle[prop] };
              hasChanges = true;
            }
          }

          if (hasChanges) {
            designData.hoverStates.push({
              element: `${afterStyle.tag}${afterStyle.classes ? '.' + afterStyle.classes.split(' ')[0] : ''}`,
              changes
            });
          }
        } catch (e) {
          // Element may have been removed or is not hoverable
        }
      }
    }

    // Save design data
    console.log('💾 Saving design data...');
    fs.writeFileSync(
      path.join(outputDir, 'design-data.json'),
      JSON.stringify(designData, null, 2)
    );

    // Generate a CSS file with extracted tokens
    console.log('🎨 Generating design tokens CSS...');
    let cssContent = `/* Design Tokens extracted from ${url} */\n/* Generated: ${new Date().toISOString()} */\n\n:root {\n`;

    // Add CSS variables
    Object.entries(designData.cssVariables).forEach(([key, value]) => {
      cssContent += `  ${key}: ${value};\n`;
    });

    // Add extracted colors as tokens
    cssContent += '\n  /* Extracted Colors */\n';
    designData.colors.background.slice(0, 20).forEach((color, i) => {
      cssContent += `  --extracted-bg-${i + 1}: ${color};\n`;
    });
    designData.colors.text.slice(0, 10).forEach((color, i) => {
      cssContent += `  --extracted-text-${i + 1}: ${color};\n`;
    });

    // Add typography tokens
    cssContent += '\n  /* Extracted Typography */\n';
    const uniqueFonts = [...new Set(designData.typography.fontFamilies)].slice(0, 5);
    uniqueFonts.forEach((font, i) => {
      const name = i === 0 ? 'primary' : i === 1 ? 'secondary' : `font-${i + 1}`;
      cssContent += `  --font-${name}: ${font};\n`;
    });

    // Add spacing tokens
    cssContent += '\n  /* Extracted Spacing */\n';
    const spacingValues = [...new Set([...designData.spacing.paddings, ...designData.spacing.margins])]
      .map(v => parseInt(v))
      .filter(v => !isNaN(v) && v > 0)
      .sort((a, b) => a - b)
      .slice(0, 12);
    spacingValues.forEach((val, i) => {
      cssContent += `  --spacing-${i + 1}: ${val}px;\n`;
    });

    // Add effect tokens
    cssContent += '\n  /* Extracted Effects */\n';
    designData.effects.boxShadows.slice(0, 5).forEach((shadow, i) => {
      const name = ['sm', 'md', 'lg', 'xl', '2xl'][i] || `shadow-${i + 1}`;
      cssContent += `  --shadow-${name}: ${shadow};\n`;
    });
    designData.effects.borderRadii.slice(0, 5).forEach((radius, i) => {
      const name = ['sm', 'md', 'lg', 'xl', 'full'][i] || `radius-${i + 1}`;
      cssContent += `  --radius-${name}: ${radius};\n`;
    });

    cssContent += '}\n';

    fs.writeFileSync(path.join(outputDir, 'design-tokens.css'), cssContent);

    console.log('\n✅ Extraction Complete!\n');
    console.log('Output files:');
    console.log(`   📄 ${path.join(outputDir, 'design-data.json')}`);
    console.log(`   🎨 ${path.join(outputDir, 'design-tokens.css')}`);
    console.log(`   📸 ${path.join(outputDir, 'screenshot-viewport.png')}`);
    console.log(`   📸 ${path.join(outputDir, 'screenshot-full.png')}`);
    console.log('\n📊 Summary:');
    console.log(`   Colors: ${designData.colors.all.length} unique`);
    console.log(`   Font Families: ${designData.typography.fontFamilies.length}`);
    console.log(`   Font Sizes: ${designData.typography.fontSizes.length}`);
    console.log(`   Shadows: ${designData.effects.boxShadows.length}`);
    console.log(`   Border Radii: ${designData.effects.borderRadii.length}`);
    console.log(`   CSS Variables: ${Object.keys(designData.cssVariables).length}`);
    console.log(`   Animations: ${designData.animations.length}`);
    if (interactMode) {
      console.log(`   Hover States: ${designData.hoverStates.length}`);
    }

  } catch (error) {
    console.error('❌ Error during extraction:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

extractDesign();
