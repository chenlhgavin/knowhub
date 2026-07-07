---
name: design-guide
description: Extract design systems from websites and generate pixel-perfect replicas. Use this skill when users want to analyze a website's design, extract design tokens, create design documentation, or replicate a website's visual appearance.
---

# Design Guide Extraction Skill

This skill analyzes websites to extract their complete design language, generates comprehensive design documentation, and creates pixel-perfect HTML replicas.

## Prerequisites

- **Node.js**: Version 18+ required
- **Playwright**: Install with `npm install playwright` or `npx playwright install chromium`

## Capabilities

1. **Design Extraction**: Captures colors, typography, spacing, shadows, animations, and UI patterns
2. **Screenshot Capture**: Takes viewport (1600x1200) and full-page screenshots
3. **Design Guide Generation**: Creates comprehensive markdown documentation
4. **Pixel-Perfect Replication**: Rebuilds the page and iterates until visually identical
5. **Output Delivery**: Saves all artifacts to organized output directory

## Workflow

When the user provides a URL to analyze:

### Step 1: Extract Design Data

Run the extraction script to capture all design information:

```bash
node /home/ubuntu/workspace/codeai/.claude/skills/design-guide/scripts/extract_design.js "<URL>"
```

This script will:
- Launch a headless browser
- Navigate to the URL and wait for full load
- Extract all computed styles from DOM elements
- Capture CSS custom properties (design tokens)
- Record animations and transitions
- Take viewport and full-page screenshots
- Output a JSON file with all design data

Output files are saved to `/tmp/design-extract/`:
- `design-data.json` - Complete extracted design information
- `screenshot-viewport.png` - 1600x1200 viewport screenshot
- `screenshot-full.png` - Full page screenshot
- `styles.css` - Extracted/computed stylesheets

### Step 2: Analyze Design Data

Read the extracted JSON and identify:

**Color Palette**:
- Primary, secondary, accent colors
- Background colors (light/dark modes)
- Text colors (headings, body, muted)
- Border colors
- Semantic colors (success, warning, error, info)

**Typography**:
- Font families (headings, body, mono)
- Font sizes scale
- Font weights
- Line heights
- Letter spacing

**Spacing**:
- Padding scale
- Margin scale
- Gap values
- Section spacing

**Effects**:
- Box shadows (cards, elevated, pressed)
- Border radius values
- Transitions (duration, easing)
- Hover/focus states
- Animations (keyframes, transforms)

**Layout**:
- Container widths
- Grid systems
- Breakpoints
- Flexbox patterns

### Step 3: Generate Design Guide

Create a comprehensive `design-guide.md` file containing:

```markdown
# Design Guide: [Site Name]

## Overview
Brief description of the design language and aesthetic.

## Design Tokens

### Colors
[Document all colors with hex values and usage]

### Typography
[Document font stack, sizes, weights]

### Spacing
[Document spacing scale]

### Effects
[Document shadows, borders, transitions]

## Component Patterns
[Document reusable UI patterns observed]

## Animation & Interactions
[Document hover states, transitions, animations]

## Implementation Notes
[Specific CSS techniques and patterns used]
```

### Step 4: Build Replica HTML

Create `/tmp/test.html` that replicates the original design:

1. Use extracted design tokens as CSS custom properties
2. Recreate the HTML structure
3. Apply styles matching the original
4. Include all animations and interactions

### Step 5: Compare and Iterate

Use the comparison script to validate:

```bash
node /home/ubuntu/workspace/codeai/.claude/skills/design-guide/scripts/compare_screenshots.js \
  "/tmp/design-extract/screenshot-viewport.png" \
  "/tmp/test.html"
```

This outputs:
- Difference score (0 = identical)
- Visual diff image highlighting mismatches
- Specific areas needing adjustment

**Iterate until difference score < 5%**:
1. Analyze diff image
2. Identify mismatched areas
3. Adjust HTML/CSS
4. Re-compare
5. Repeat until pixel-perfect

### Step 6: Finalize and Deliver

Once pixel-perfect:

1. Review the generated HTML for any improvements to design-guide.md
2. Create output directory: `.claude/skills/design-guide/output/<sitename>/`
3. Copy final files:
   - `design-guide.md` - Complete design documentation
   - `index.html` - Pixel-perfect replica
   - `screenshots/` - Original and comparison screenshots
   - `design-tokens.css` - Extracted CSS custom properties

## Script Reference

### extract_design.js

```bash
node extract_design.js <URL> [options]
```

Options:
- `--output <dir>` - Output directory (default: /tmp/design-extract)
- `--viewport <WxH>` - Viewport size (default: 1600x1200)
- `--wait <ms>` - Wait time after load (default: 2000)
- `--interact` - Enable interaction mode to explore hover/click states

### compare_screenshots.js

```bash
node compare_screenshots.js <original-image> <html-file> [options]
```

Options:
- `--threshold <n>` - Acceptable difference % (default: 5)
- `--output <file>` - Diff image output path

## Design Token Categories

### Colors to Extract
- `--color-primary-*` (50-950 scale if available)
- `--color-secondary-*`
- `--color-accent-*`
- `--color-neutral-*`
- `--color-background`
- `--color-foreground`
- `--color-muted`
- `--color-border`
- `--color-success/warning/error/info`

### Typography to Extract
- `--font-sans/serif/mono`
- `--font-size-xs/sm/base/lg/xl/2xl/3xl/4xl`
- `--font-weight-light/normal/medium/semibold/bold`
- `--line-height-tight/normal/relaxed`
- `--letter-spacing-tight/normal/wide`

### Spacing to Extract
- `--spacing-1` through `--spacing-16` (or px values)
- `--container-sm/md/lg/xl/2xl`

### Effects to Extract
- `--shadow-sm/md/lg/xl`
- `--radius-sm/md/lg/full`
- `--transition-fast/normal/slow`
- `--ease-in/out/in-out`

## Example Usage

User: "Create a design guide for https://stripe.com"

1. Run extraction: `node extract_design.js "https://stripe.com"`
2. Read `/tmp/design-extract/design-data.json`
3. Analyze color palette, typography, spacing, effects
4. Generate `design-guide.md` with Stripe's design system
5. Build `/tmp/test.html` replicating Stripe's homepage
6. Compare screenshots, iterate until < 5% difference
7. Finalize to `.claude/skills/design-guide/output/stripe/`

## Notes

- Some sites may block automated access; may need to adjust user agent
- Dynamic content (carousels, videos) captured in initial state
- Login-required pages need authentication handling
- Very long pages may need segmented screenshots
- Complex animations may require manual documentation
