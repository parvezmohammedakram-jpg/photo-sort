# PhotoSort -- UI Design System Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Design Philosophy

PhotoSort is a tool, not a showcase. The interface should disappear and let the photographs be the focus. Every design decision optimizes for:

1. **Information density** -- Show more photos, less chrome.
2. **Scannability** -- The eye should land on scores, categories, and issues immediately.
3. **Quietness** -- Neutral surfaces that do not compete with photograph thumbnails.
4. **Precision** -- Monospace numbers, consistent alignment, clear labels.

This system draws from the principles of utilitarian minimalism: warm monochrome palette, flat surfaces, thin borders, no decoration without function.

---

## 2. CSS Custom Properties

```css
:root {
  /* Surfaces */
  --surface-page: #FAFAF9;
  --surface-card: #FFFFFF;
  --surface-raised: #F5F5F4;
  --surface-inset: #F0EFED;
  --surface-overlay: rgba(0, 0, 0, 0.4);

  /* Borders */
  --border-default: #E5E4E2;
  --border-strong: #D4D3D1;
  --border-focus: #111111;

  /* Text */
  --text-primary: #111111;
  --text-body: #2F3437;
  --text-muted: #787774;
  --text-faint: #A3A09C;
  --text-inverse: #FFFFFF;

  /* Status -- Good */
  --status-good-bg: #EDF3EC;
  --status-good-text: #346538;
  --status-good-border: #C4D9C3;

  /* Status -- Review */
  --status-review-bg: #FBF3DB;
  --status-review-text: #956400;
  --status-review-border: #E8D8A8;

  /* Status -- Poor */
  --status-poor-bg: #FDEBEC;
  --status-poor-text: #9F2F2D;
  --status-poor-border: #E8B4B3;

  /* Status -- Duplicate */
  --status-dup-bg: #E1F3FE;
  --status-dup-text: #1F6C9F;
  --status-dup-border: #B0D8F0;

  /* Interactive */
  --interactive-primary: #111111;
  --interactive-primary-hover: #2F3437;
  --interactive-primary-active: #000000;
  --interactive-primary-text: #FFFFFF;
  --interactive-secondary-border: #D4D3D1;

  /* Typography */
  --font-sans: 'Geist Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI',
    Helvetica, Arial, sans-serif;
  --font-mono: 'Geist Mono', 'JetBrains Mono', 'SF Mono', 'Consolas',
    monospace;

  /* Type Scale */
  --text-xs: 0.6875rem;    /* 11px */
  --text-sm: 0.75rem;      /* 12px */
  --text-base: 0.875rem;   /* 14px */
  --text-md: 1rem;         /* 16px */
  --text-lg: 1.25rem;      /* 20px */
  --text-xl: 1.5rem;       /* 24px */
  --text-2xl: 2rem;        /* 32px */
  --text-3xl: 2.5rem;      /* 40px */

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;

  /* Shadows -- minimal */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);

  /* Transitions */
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --duration-fast: 150ms;
  --duration-normal: 200ms;

  /* Layout */
  --sidebar-width: 240px;
  --header-height: 56px;
  --content-max-width: 1400px;
}
```

---

## 3. Base Styles

```css
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.6;
  color: var(--text-body);
  background-color: var(--surface-page);
}

h1, h2, h3, h4 {
  color: var(--text-primary);
  line-height: 1.2;
  letter-spacing: -0.02em;
}

h1 { font-size: var(--text-2xl); font-weight: 600; }
h2 { font-size: var(--text-xl); font-weight: 500; }
h3 { font-size: var(--text-lg); font-weight: 500; }
h4 { font-size: var(--text-md); font-weight: 500; }

code, .mono {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}
```

---

## 4. Component Patterns

### Card

```css
.card {
  background: var(--surface-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
}
```

No shadow by default. No hover elevation. Border only.

### Button -- Primary

```css
.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: 10px 20px;
  background: var(--interactive-primary);
  color: var(--interactive-primary-text);
  border: none;
  border-radius: var(--radius-md);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: 500;
  cursor: pointer;
  transition: transform var(--duration-fast) var(--ease-out);
}

.btn-primary:hover {
  background: var(--interactive-primary-hover);
}

.btn-primary:active {
  transform: scale(0.97);
  background: var(--interactive-primary-active);
}
```

### Button -- Secondary

```css
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: 10px 20px;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--interactive-secondary-border);
  border-radius: var(--radius-md);
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: 500;
  cursor: pointer;
  transition: border-color var(--duration-fast) ease;
}

.btn-secondary:hover {
  border-color: var(--text-primary);
}

.btn-secondary:active {
  transform: scale(0.97);
}
```

### Badge

```css
.badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: var(--text-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  border-radius: var(--radius-sm);
  line-height: 1.6;
}

.badge-good {
  background: var(--status-good-bg);
  color: var(--status-good-text);
}

.badge-review {
  background: var(--status-review-bg);
  color: var(--status-review-text);
}

.badge-poor {
  background: var(--status-poor-bg);
  color: var(--status-poor-text);
}

.badge-duplicate {
  background: var(--status-dup-bg);
  color: var(--status-dup-text);
}
```

### Input

```css
.input {
  width: 100%;
  padding: 10px 14px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  color: var(--text-primary);
  background: var(--surface-inset);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  outline: none;
  transition: border-color var(--duration-fast) ease;
}

.input:focus {
  border-color: var(--border-focus);
}

.input-label {
  display: block;
  margin-bottom: var(--space-xs);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-muted);
}
```

Label always above input. Never use placeholder as label.

### Progress Bar

```css
.progress-track {
  width: 100%;
  height: 4px;
  background: var(--surface-inset);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--text-primary);
  border-radius: 2px;
  transition: width 300ms var(--ease-out);
}
```

### Stat Card (Dashboard)

```css
.stat-card {
  padding: var(--space-lg);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  background: var(--surface-card);
}

.stat-value {
  font-family: var(--font-mono);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1;
  margin-bottom: var(--space-xs);
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
```

---

## 5. Photo Grid

```css
.photo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-md);
}

.photo-card {
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--surface-card);
  cursor: pointer;
  transition: border-color var(--duration-fast) ease;
}

.photo-card:hover {
  border-color: var(--border-strong);
}

.photo-card-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
  background: var(--surface-inset);
}

.photo-card-info {
  padding: var(--space-sm) var(--space-md);
}

.photo-card-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.photo-card-score {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  color: var(--text-muted);
}
```

---

## 6. Layout Structure

```css
.app-layout {
  display: grid;
  grid-template-columns: var(--sidebar-width) 1fr;
  min-height: 100vh;
}

.sidebar {
  background: var(--surface-raised);
  border-right: 1px solid var(--border-default);
  padding: var(--space-lg) var(--space-md);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.main-content {
  padding: var(--space-xl);
  max-width: var(--content-max-width);
}
```

---

## 7. Rules Summary

| Rule | Enforcement |
|------|-------------|
| No gradients | Solid colors only |
| No heavy shadows | var(--shadow-sm) max, prefer border |
| No emojis | Use text labels or simple SVG icons |
| No rounded-full on containers | var(--radius-lg) = 8px max |
| No placeholder-as-label | Label element always above input |
| No color for decoration | Color only for status semantics |
| Monospace for numbers | Scores, counts, metrics |
| Consistent radius | Same radius scale across all components |
| Active state on buttons | scale(0.97) on :active |
| Hover is border only | No shadow elevation on hover |
