# Design Guide: example.com

> Extracted from: https://example.com/
> Generated: 2026-01-26T12:00:59.796Z

## Overview

This design guide documents the visual language and design tokens extracted from example.com. Use these tokens to create consistent, pixel-perfect replicas of the original design.

## Color Palette

### Primary / Brand Colors

| Color | Hex | RGB |
|-------|-----|-----|
| ![#334488](https://via.placeholder.com/20/334488/334488) | `#334488` | `rgb(51, 68, 136)` |

### Background Colors

| Color | Hex | Usage |
|-------|-----|-------|
| ![#EEEEEE](https://via.placeholder.com/20/EEEEEE/EEEEEE) | `#EEEEEE` | Primary background |

### Text Colors

| Color | Hex | Usage |
|-------|-----|-------|
| ![#000000](https://via.placeholder.com/20/000000/000000) | `#000000` | Primary text |
| ![#334488](https://via.placeholder.com/20/334488/334488) | `#334488` | Secondary text |

## Typography

### Font Families

| Token | Font Family |
|-------|-------------|
| `--font-primary` | Times New Roman |
| `--font-secondary` | system-ui |

### Font Sizes

| Token | Size |
|-------|------|
| `--text-xs` | 16px |
| `--text-sm` | 24px |

### Font Weights

| Token | Weight |
|-------|--------|
| `--font-weight-normal` | 400 |
| `--font-weight-bold` | 700 |

## Spacing

### Spacing Scale

| Token | Value |
|-------|-------|
| `--spacing-1` | 16px |
| `--spacing-2` | 16px |
| `--spacing-3` | 180px |
| `--spacing-4` | 320px |

## Effects

### Transitions

```css
/* all */
```

## Component Patterns

### Headings

| Tag | Font Size | Font Weight | Line Height | Color |
|-----|-----------|-------------|-------------|-------|
| h1 | 24px | 700 | normal | #000000 |

## Layout

## Implementation Guide

### 1. Setup CSS Custom Properties

Copy the design tokens from `design-tokens.css` to your stylesheet's `:root` selector.

### 2. Import Fonts

Ensure the following fonts are available:

- Times New Roman
- system-ui

### 3. Apply Base Styles

```css
body {
  font-family: var(--font-primary);
  background-color: var(--color-background);
  color: var(--color-text);
  line-height: 1.5;
}
```

### 4. Reference Screenshots

Use the extracted screenshots for visual reference:
- `screenshot-viewport.png` - Main viewport view
- `screenshot-full.png` - Full page view

---

*This design guide was automatically generated. Review and adjust tokens as needed for your implementation.*
