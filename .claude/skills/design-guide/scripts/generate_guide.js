#!/usr/bin/env node

/**
 * Design Guide Generator
 * Generates a comprehensive markdown design guide from extracted data
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const dataFile = args[0] || '/tmp/design-extract/design-data.json';
const outputFile = args[1] || '/tmp/design-extract/design-guide.md';

if (!fs.existsSync(dataFile)) {
  console.error(`❌ Data file not found: ${dataFile}`);
  console.error('Run extract_design.js first to generate the design data.');
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(dataFile, 'utf-8'));

// Helper functions
function rgbToHex(rgb) {
  if (!rgb || rgb === 'transparent') return null;
  const match = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    const r = parseInt(match[1]).toString(16).padStart(2, '0');
    const g = parseInt(match[2]).toString(16).padStart(2, '0');
    const b = parseInt(match[3]).toString(16).padStart(2, '0');
    return `#${r}${g}${b}`.toUpperCase();
  }
  return rgb;
}

function categorizeColors(colors) {
  const categorized = {
    whites: [],
    grays: [],
    blacks: [],
    blues: [],
    greens: [],
    reds: [],
    yellows: [],
    purples: [],
    others: []
  };

  colors.forEach(color => {
    const hex = rgbToHex(color);
    if (!hex) return;

    const match = color.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
    if (!match) {
      categorized.others.push({ original: color, hex });
      return;
    }

    const r = parseInt(match[1]);
    const g = parseInt(match[2]);
    const b = parseInt(match[3]);

    // Categorize by dominant channel
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const diff = max - min;

    if (diff < 20) {
      // Grayscale
      if (max > 240) categorized.whites.push({ original: color, hex, r, g, b });
      else if (max < 30) categorized.blacks.push({ original: color, hex, r, g, b });
      else categorized.grays.push({ original: color, hex, r, g, b });
    } else if (r > g && r > b) {
      if (g > b + 30) categorized.yellows.push({ original: color, hex, r, g, b });
      else categorized.reds.push({ original: color, hex, r, g, b });
    } else if (g > r && g > b) {
      categorized.greens.push({ original: color, hex, r, g, b });
    } else if (b > r && b > g) {
      if (r > g + 30) categorized.purples.push({ original: color, hex, r, g, b });
      else categorized.blues.push({ original: color, hex, r, g, b });
    } else {
      categorized.others.push({ original: color, hex, r, g, b });
    }
  });

  return categorized;
}

function extractFontFamily(fontString) {
  const fonts = fontString.split(',').map(f => f.trim().replace(/["']/g, ''));
  return fonts[0] || fontString;
}

function sortByNumericValue(arr) {
  return [...arr].sort((a, b) => {
    const numA = parseFloat(a);
    const numB = parseFloat(b);
    return numA - numB;
  });
}

// Generate the markdown
let md = '';

// Header
const siteName = new URL(data.url).hostname.replace('www.', '');
md += `# Design Guide: ${siteName}\n\n`;
md += `> Extracted from: ${data.url}\n`;
md += `> Generated: ${data.timestamp}\n\n`;

// Overview
md += `## Overview\n\n`;
md += `This design guide documents the visual language and design tokens extracted from ${siteName}. `;
md += `Use these tokens to create consistent, pixel-perfect replicas of the original design.\n\n`;

// Color Palette
md += `## Color Palette\n\n`;

const categorizedColors = categorizeColors(data.colors.all);

if (categorizedColors.blues.length > 0) {
  md += `### Primary / Brand Colors\n\n`;
  md += `| Color | Hex | RGB |\n`;
  md += `|-------|-----|-----|\n`;
  [...categorizedColors.blues, ...categorizedColors.purples].slice(0, 8).forEach(c => {
    md += `| ![${c.hex}](https://via.placeholder.com/20/${c.hex.slice(1)}/${c.hex.slice(1)}) | \`${c.hex}\` | \`${c.original}\` |\n`;
  });
  md += '\n';
}

md += `### Background Colors\n\n`;
md += `| Color | Hex | Usage |\n`;
md += `|-------|-----|-------|\n`;
[...categorizedColors.whites, ...categorizedColors.grays.slice(0, 3)].slice(0, 6).forEach((c, i) => {
  const usage = i === 0 ? 'Primary background' : i === 1 ? 'Secondary background' : 'Surface/Card';
  md += `| ![${c.hex}](https://via.placeholder.com/20/${c.hex.slice(1)}/${c.hex.slice(1)}) | \`${c.hex}\` | ${usage} |\n`;
});
md += '\n';

md += `### Text Colors\n\n`;
md += `| Color | Hex | Usage |\n`;
md += `|-------|-----|-------|\n`;
const textColors = data.colors.text.slice(0, 6).map(c => ({ original: c, hex: rgbToHex(c) }));
textColors.forEach((c, i) => {
  const usage = i === 0 ? 'Primary text' : i === 1 ? 'Secondary text' : 'Muted text';
  if (c.hex) {
    md += `| ![${c.hex}](https://via.placeholder.com/20/${c.hex.slice(1)}/${c.hex.slice(1)}) | \`${c.hex}\` | ${usage} |\n`;
  }
});
md += '\n';

if (categorizedColors.greens.length > 0 || categorizedColors.reds.length > 0 || categorizedColors.yellows.length > 0) {
  md += `### Semantic Colors\n\n`;
  md += `| Color | Hex | Meaning |\n`;
  md += `|-------|-----|--------|\n`;
  if (categorizedColors.greens[0]) {
    md += `| ![${categorizedColors.greens[0].hex}](https://via.placeholder.com/20/${categorizedColors.greens[0].hex.slice(1)}/${categorizedColors.greens[0].hex.slice(1)}) | \`${categorizedColors.greens[0].hex}\` | Success |\n`;
  }
  if (categorizedColors.reds[0]) {
    md += `| ![${categorizedColors.reds[0].hex}](https://via.placeholder.com/20/${categorizedColors.reds[0].hex.slice(1)}/${categorizedColors.reds[0].hex.slice(1)}) | \`${categorizedColors.reds[0].hex}\` | Error/Danger |\n`;
  }
  if (categorizedColors.yellows[0]) {
    md += `| ![${categorizedColors.yellows[0].hex}](https://via.placeholder.com/20/${categorizedColors.yellows[0].hex.slice(1)}/${categorizedColors.yellows[0].hex.slice(1)}) | \`${categorizedColors.yellows[0].hex}\` | Warning |\n`;
  }
  md += '\n';
}

// Typography
md += `## Typography\n\n`;

md += `### Font Families\n\n`;
const uniqueFonts = [...new Set(data.typography.fontFamilies.map(f => extractFontFamily(f)))].slice(0, 5);
md += `| Token | Font Family |\n`;
md += `|-------|-------------|\n`;
uniqueFonts.forEach((font, i) => {
  const token = i === 0 ? '--font-primary' : i === 1 ? '--font-secondary' : `--font-${i + 1}`;
  md += `| \`${token}\` | ${font} |\n`;
});
md += '\n';

md += `### Font Sizes\n\n`;
const sortedSizes = sortByNumericValue(data.typography.fontSizes).slice(0, 12);
md += `| Token | Size |\n`;
md += `|-------|------|\n`;
sortedSizes.forEach((size, i) => {
  const tokens = ['--text-xs', '--text-sm', '--text-base', '--text-lg', '--text-xl', '--text-2xl', '--text-3xl', '--text-4xl', '--text-5xl', '--text-6xl'];
  const token = tokens[i] || `--text-${i + 1}`;
  md += `| \`${token}\` | ${size} |\n`;
});
md += '\n';

md += `### Font Weights\n\n`;
const weights = [...new Set(data.typography.fontWeights)].sort((a, b) => parseInt(a) - parseInt(b));
md += `| Token | Weight |\n`;
md += `|-------|--------|\n`;
weights.forEach(weight => {
  const name = {
    '100': 'thin', '200': 'extralight', '300': 'light', '400': 'normal',
    '500': 'medium', '600': 'semibold', '700': 'bold', '800': 'extrabold', '900': 'black'
  }[weight] || weight;
  md += `| \`--font-weight-${name}\` | ${weight} |\n`;
});
md += '\n';

// Spacing
md += `## Spacing\n\n`;

const allSpacing = [...new Set([
  ...data.spacing.paddings,
  ...data.spacing.margins
])].map(v => parseInt(v)).filter(v => !isNaN(v) && v > 0).sort((a, b) => a - b);

md += `### Spacing Scale\n\n`;
md += `| Token | Value |\n`;
md += `|-------|-------|\n`;
allSpacing.slice(0, 16).forEach((val, i) => {
  md += `| \`--spacing-${i + 1}\` | ${val}px |\n`;
});
md += '\n';

if (data.spacing.gaps.length > 0) {
  md += `### Gap Values\n\n`;
  md += `| Token | Value |\n`;
  md += `|-------|-------|\n`;
  data.spacing.gaps.slice(0, 8).forEach((gap, i) => {
    md += `| \`--gap-${i + 1}\` | ${gap} |\n`;
  });
  md += '\n';
}

// Effects
md += `## Effects\n\n`;

if (data.effects.boxShadows.length > 0) {
  md += `### Box Shadows\n\n`;
  md += `| Token | Value |\n`;
  md += `|-------|-------|\n`;
  const shadowNames = ['sm', 'md', 'lg', 'xl', '2xl'];
  data.effects.boxShadows.slice(0, 5).forEach((shadow, i) => {
    md += `| \`--shadow-${shadowNames[i] || i + 1}\` | \`${shadow.length > 60 ? shadow.substring(0, 60) + '...' : shadow}\` |\n`;
  });
  md += '\n';
}

if (data.effects.borderRadii.length > 0) {
  md += `### Border Radius\n\n`;
  md += `| Token | Value |\n`;
  md += `|-------|-------|\n`;
  const sortedRadii = sortByNumericValue(data.effects.borderRadii).slice(0, 6);
  const radiusNames = ['sm', 'md', 'lg', 'xl', '2xl', 'full'];
  sortedRadii.forEach((radius, i) => {
    md += `| \`--radius-${radiusNames[i] || i + 1}\` | ${radius} |\n`;
  });
  md += '\n';
}

if (data.effects.transitions.length > 0) {
  md += `### Transitions\n\n`;
  md += `\`\`\`css\n`;
  data.effects.transitions.slice(0, 5).forEach(t => {
    md += `/* ${t} */\n`;
  });
  md += `\`\`\`\n\n`;
}

// CSS Custom Properties
if (Object.keys(data.cssVariables).length > 0) {
  md += `## CSS Custom Properties (Design Tokens)\n\n`;
  md += `The following CSS custom properties were extracted from the site:\n\n`;
  md += `\`\`\`css\n:root {\n`;
  Object.entries(data.cssVariables).slice(0, 50).forEach(([key, value]) => {
    md += `  ${key}: ${value};\n`;
  });
  if (Object.keys(data.cssVariables).length > 50) {
    md += `  /* ... and ${Object.keys(data.cssVariables).length - 50} more */\n`;
  }
  md += `}\n\`\`\`\n\n`;
}

// Animations
if (data.animations && data.animations.length > 0) {
  md += `## Animations\n\n`;
  data.animations.slice(0, 5).forEach(anim => {
    md += `### @keyframes ${anim.name}\n\n`;
    md += `\`\`\`css\n@keyframes ${anim.name} {\n`;
    anim.keyframes.forEach(kf => {
      md += `  ${kf.offset} { ${kf.style} }\n`;
    });
    md += `}\n\`\`\`\n\n`;
  });
}

// Hover States
if (data.hoverStates && data.hoverStates.length > 0) {
  md += `## Hover & Interactive States\n\n`;
  md += `| Element | Property | Normal | Hover |\n`;
  md += `|---------|----------|--------|-------|\n`;
  data.hoverStates.slice(0, 10).forEach(state => {
    Object.entries(state.changes).forEach(([prop, change]) => {
      md += `| \`${state.element}\` | ${prop} | \`${change.from}\` | \`${change.to}\` |\n`;
    });
  });
  md += '\n';
}

// Component Patterns
if (data.elements && data.elements.length > 0) {
  md += `## Component Patterns\n\n`;

  const buttons = data.elements.filter(el => el.tag === 'button' || (el.tag === 'a' && el.classes.some(c => c.includes('btn') || c.includes('button'))));
  if (buttons.length > 0) {
    md += `### Buttons\n\n`;
    md += `\`\`\`css\n`;
    buttons.slice(0, 3).forEach((btn, i) => {
      md += `/* Button ${i + 1}: .${btn.classes.join('.')} */\n`;
      md += `{\n`;
      Object.entries(btn.styles).forEach(([prop, val]) => {
        if (val && val !== 'none' && val !== 'auto' && val !== 'normal' && val !== '0px') {
          const cssProp = prop.replace(/([A-Z])/g, '-$1').toLowerCase();
          md += `  ${cssProp}: ${val};\n`;
        }
      });
      md += `}\n\n`;
    });
    md += `\`\`\`\n\n`;
  }

  const headings = data.elements.filter(el => ['h1', 'h2', 'h3', 'h4'].includes(el.tag));
  if (headings.length > 0) {
    md += `### Headings\n\n`;
    md += `| Tag | Font Size | Font Weight | Line Height | Color |\n`;
    md += `|-----|-----------|-------------|-------------|-------|\n`;
    headings.forEach(h => {
      md += `| ${h.tag} | ${h.styles.fontSize} | ${h.styles.fontWeight} | ${h.styles.lineHeight || 'normal'} | ${rgbToHex(h.styles.color) || 'inherit'} |\n`;
    });
    md += '\n';
  }
}

// Layout
if (data.layout) {
  md += `## Layout\n\n`;

  if (data.layout.maxWidths && data.layout.maxWidths.length > 0) {
    md += `### Container Widths\n\n`;
    md += `| Token | Value |\n`;
    md += `|-------|-------|\n`;
    const widthNames = ['sm', 'md', 'lg', 'xl', '2xl'];
    sortByNumericValue(data.layout.maxWidths).slice(0, 5).forEach((w, i) => {
      md += `| \`--container-${widthNames[i] || i + 1}\` | ${w} |\n`;
    });
    md += '\n';
  }

  if (data.layout.gridTemplates && data.layout.gridTemplates.length > 0) {
    md += `### Grid Templates\n\n`;
    md += `\`\`\`css\n`;
    data.layout.gridTemplates.slice(0, 5).forEach((grid, i) => {
      md += `/* Grid ${i + 1} */\ngrid-template-columns: ${grid};\n\n`;
    });
    md += `\`\`\`\n\n`;
  }
}

// Implementation Guide
md += `## Implementation Guide\n\n`;

md += `### 1. Setup CSS Custom Properties\n\n`;
md += `Copy the design tokens from \`design-tokens.css\` to your stylesheet's \`:root\` selector.\n\n`;

md += `### 2. Import Fonts\n\n`;
if (uniqueFonts.length > 0) {
  md += `Ensure the following fonts are available:\n\n`;
  uniqueFonts.forEach(font => {
    md += `- ${font}\n`;
  });
  md += '\n';
}

md += `### 3. Apply Base Styles\n\n`;
md += `\`\`\`css\nbody {\n`;
md += `  font-family: var(--font-primary);\n`;
md += `  background-color: var(--color-background);\n`;
md += `  color: var(--color-text);\n`;
md += `  line-height: 1.5;\n`;
md += `}\n\`\`\`\n\n`;

md += `### 4. Reference Screenshots\n\n`;
md += `Use the extracted screenshots for visual reference:\n`;
md += `- \`screenshot-viewport.png\` - Main viewport view\n`;
md += `- \`screenshot-full.png\` - Full page view\n\n`;

// Footer
md += `---\n\n`;
md += `*This design guide was automatically generated. Review and adjust tokens as needed for your implementation.*\n`;

// Write the file
fs.writeFileSync(outputFile, md);
console.log(`✅ Design guide generated: ${outputFile}`);
console.log(`   Total size: ${(md.length / 1024).toFixed(2)} KB`);
