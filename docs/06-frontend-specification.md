# PhotoSort -- Frontend Specification Document

**Version:** 1.0  
**Date:** 2026-09-23  
**Status:** Draft

---

## 1. Design Direction

The PhotoSort interface follows a utilitarian, tool-grade aesthetic. It is a productivity application for reviewing photographs, not a marketing website. The design prioritizes:

- **Clarity over decoration.** Every element has a purpose.
- **Density where appropriate.** Photo grids should show as many thumbnails as practical.
- **Quiet surfaces.** Warm off-white backgrounds, thin borders, no gradients, no heavy shadows.
- **Typographic hierarchy.** Size and weight differentiate information, not color.
- **Muted semantic color.** Color used only for status indicators (good/review/poor), never for decoration.

### What this is NOT

- No gradients. No glassmorphism. No neon accents.
- No generic AI-purple glow.
- No heavy drop shadows.
- No rounded-full pill containers on cards or sections.
- No emojis anywhere in the interface.
- No placeholder images or fake screenshots.

---

## 2. Typography

| Role | Font | Size | Weight | Color |
|------|------|------|--------|-------|
| Display heading | Geist Sans / system sans-serif | 32-40px | 600 | #111111 |
| Section heading | Geist Sans / system sans-serif | 20-24px | 500 | #111111 |
| Body text | Geist Sans / system sans-serif | 14-16px | 400 | #2F3437 |
| Secondary/meta | Geist Sans / system sans-serif | 12-13px | 400 | #787774 |
| Monospace (scores, data) | Geist Mono / JetBrains Mono / system monospace | 12-13px | 500 | #2F3437 |
| Label/eyebrow | system sans-serif | 11px | 500, uppercase, tracking 0.12em | #787774 |

Body text line-height: 1.6. Display line-height: 1.1. Letter-spacing on display: -0.02em.

---

## 3. Color Palette

### Surfaces

| Token | Value | Usage |
|-------|-------|-------|
| --surface-page | #FAFAF9 | Page background |
| --surface-card | #FFFFFF | Card/panel backgrounds |
| --surface-raised | #F5F5F4 | Sidebar, hover states |
| --surface-inset | #F0EFED | Input backgrounds, inset areas |

### Borders

| Token | Value | Usage |
|-------|-------|-------|
| --border-default | #E5E4E2 | Card borders, dividers |
| --border-strong | #D4D3D1 | Active/focus borders |

### Text

| Token | Value | Usage |
|-------|-------|-------|
| --text-primary | #111111 | Headings, primary content |
| --text-body | #2F3437 | Body text |
| --text-muted | #787774 | Secondary, meta, captions |
| --text-faint | #A3A09C | Disabled states |

### Status Colors (Muted, Desaturated)

| Token | Background | Text | Usage |
|-------|-----------|------|-------|
| --status-good-bg | #EDF3EC | #346538 | Good/Select category |
| --status-good-text | #346538 | -- | Good label text |
| --status-review-bg | #FBF3DB | #956400 | Review category |
| --status-review-text | #956400 | -- | Review label text |
| --status-poor-bg | #FDEBEC | #9F2F2D | Poor Quality category |
| --status-poor-text | #9F2F2D | -- | Poor label text |
| --status-duplicate-bg | #E1F3FE | #1F6C9F | Duplicate indicator |
| --status-duplicate-text | #1F6C9F | -- | Duplicate label text |

### Interactive

| Token | Value | Usage |
|-------|-------|-------|
| --interactive-primary | #111111 | Primary buttons (dark) |
| --interactive-primary-text | #FFFFFF | Text on primary buttons |
| --interactive-hover | #2F3437 | Primary button hover |
| --interactive-active | #000000 | Primary button active |

---

## 4. Component Specifications

### 4.1 Cards

```
Border: 1px solid var(--border-default)
Border-radius: 8px
Background: var(--surface-card)
Padding: 16px
Shadow: none (or 0 1px 2px rgba(0,0,0,0.03) max)
```

No rounded-full containers. No heavy elevation. Cards are flat containers with thin borders.

### 4.2 Buttons

**Primary:**
```
Background: var(--interactive-primary)
Text: var(--interactive-primary-text)
Border-radius: 6px
Padding: 10px 20px
Font-size: 14px, weight 500
Transition: transform 160ms ease-out
Active: scale(0.97)
```

**Secondary:**
```
Background: transparent
Border: 1px solid var(--border-default)
Text: var(--text-primary)
Border-radius: 6px
Padding: 10px 20px
```

### 4.3 Badges (Status Labels)

```
Font-size: 11px
Font-weight: 600
Text-transform: uppercase
Letter-spacing: 0.04em
Padding: 3px 8px
Border-radius: 4px
Background: var(--status-*-bg)
Color: var(--status-*-text)
```

### 4.4 Sidebar Navigation

```
Width: 240px
Background: var(--surface-raised)
Border-right: 1px solid var(--border-default)
Padding: 16px
```

Nav items:
```
Padding: 8px 12px
Border-radius: 6px
Font-size: 14px
Color: var(--text-muted)
Active: background var(--surface-card), color var(--text-primary), font-weight 500
```

### 4.5 Progress Bar

```
Background track: var(--surface-inset)
Fill: var(--text-primary)
Height: 4px
Border-radius: 2px
Transition: width 300ms ease-out
```

No animated stripes. No color gradients. Solid fill.

---

## 5. Pages

### 5.1 Dashboard

The landing view after importing a project.

**Layout:**
```
+-------+-----------------------------------------------+
|       |                                               |
| Side  |   PHOTOSORT                                   |
| bar   |                                               |
|       |   Photos    Processed   Good   Review   Poor  |
|       |   1,248     1,240       742    301      197   |
|       |                                               |
|       |   Duplicates: 34 groups (86 photos)           |
|       |   Average Score: 68.4                         |
|       |                                               |
|       |   Issues Detected                             |
|       |   Blurry: 89  Underexposed: 42                |
|       |   Overexposed: 18  Low Res: 31                |
|       |   Closed Eyes: 15                             |
|       |                                               |
+-------+-----------------------------------------------+
```

Stat cards use monospace numbers for alignment. No icon decorations. Numbers are the focus.

### 5.2 Import View

**Layout:**
```
+-------+-----------------------------------------------+
|       |                                               |
| Side  |   Import Photos                               |
| bar   |                                               |
|       |   Folder Path                                 |
|       |   [________________________________] [Browse]  |
|       |                                               |
|       |   Project Name (optional)                     |
|       |   [________________________________]          |
|       |                                               |
|       |   [Start Processing]                          |
|       |                                               |
|       |   Files Found: --                             |
|       |   Supported: --                               |
|       |   Skipped: --                                 |
|       |                                               |
+-------+-----------------------------------------------+
```

Input fields use var(--surface-inset) background with var(--border-default) border. Label above input, never placeholder-as-label.

### 5.3 Processing View

**Layout:**
```
+-------+-----------------------------------------------+
|       |                                               |
| Side  |   Processing                                  |
| bar   |                                               |
|       |   897 / 1,248 photos                          |
|       |   [==============================----] 71.9%  |
|       |                                               |
|       |   Current: IMG_0897.jpg                       |
|       |   Step: Exposure Analysis                     |
|       |                                               |
|       |   Completed  897                              |
|       |   Failed     3                                |
|       |   Remaining  348                              |
|       |                                               |
+-------+-----------------------------------------------+
```

Progress is real. The progress bar width reflects actual processed/total ratio. Current file and step update via polling.

### 5.4 Results View (Photo Grid)

**Layout:**
```
+-------+-----------------------------------------------+
|       |                                               |
| Side  |   Results                                     |
| bar   |                                               |
|       |   [All] [Good 742] [Review 301] [Poor 197]    |
|       |                                               |
|       |   Sort: Score (desc)  v                       |
|       |                                               |
|       |   +------+ +------+ +------+ +------+        |
|       |   |      | |      | |      | |      |        |
|       |   | thumb| | thumb| | thumb| | thumb|        |
|       |   |      | |      | |      | |      |        |
|       |   | name | | name | | name | | name |        |
|       |   | 91   | | 84   | | 72   | | 65   |        |
|       |   | GOOD | | GOOD | | REV  | | REV  |        |
|       |   +------+ +------+ +------+ +------+        |
|       |                                               |
|       |   +------+ +------+ +------+ +------+        |
|       |   | ...  | | ...  | | ...  | | ...  |        |
|       |   +------+ +------+ +------+ +------+        |
|       |                                               |
|       |   < 1 2 3 4 5 ... 15 >                       |
|       |                                               |
+-------+-----------------------------------------------+
```

Category filter tabs show counts. Photo cards are clickable. Grid uses CSS Grid with auto-fill columns.

### 5.5 Photo Detail View

Opens as a slide-over panel or full page.

**Layout:**
```
+-------+-----------------------------------------------+
|       |                                               |
| Side  |   < Back to Results                           |
| bar   |                                               |
|       |   +---------------------------+  Score        |
|       |   |                           |  87 / 100    |
|       |   |      Large Preview        |  GOOD        |
|       |   |                           |               |
|       |   |                           |  Analysis     |
|       |   +---------------------------+  Sharpness    824.2   Sharp
|       |                                  Resolution   12.4 MP  OK
|       |   IMG_1048.jpg                   Brightness   126.7    Good
|       |   4032 x 3024 | 4.5 MB | JPG    Faces        3        --
|       |                                  Eyes         Open     --
|       |                                  Duplicate    No       --
|       |                                               |
|       |   Issues                                      |
|       |   No issues detected.                         |
|       |                                               |
|       |   Actions                                     |
|       |   [Move to Review] [Move to Poor]             |
|       |                                               |
+-------+-----------------------------------------------+
```

Analysis table uses a clean two-column layout: metric name (left, muted) and value (right, monospace). Status labels right-aligned as badges.

### 5.6 Duplicate View

**Layout:**
```
+-------+-----------------------------------------------+
|       |                                               |
| Side  |   Duplicates                                  |
| bar   |   34 groups, 86 photos                        |
|       |                                               |
|       |   Group 01 | Near-duplicate | 96% similar     |
|       |   +------+ +------+ +------+                  |
|       |   | thumb| | thumb| | thumb|                  |
|       |   | 82.1 | | 79.3 | | 85.7 |                  |
|       |   +------+ +------+ +------+                  |
|       |                                               |
|       |   ---                                         |
|       |                                               |
|       |   Group 02 | Exact duplicate | 100%           |
|       |   +------+ +------+                           |
|       |   | thumb| | thumb|                           |
|       |   | 74.2 | | 74.2 |                           |
|       |   +------+ +------+                           |
|       |                                               |
+-------+-----------------------------------------------+
```

Groups displayed vertically. Each group shows its type and similarity. Clicking a photo opens the detail view.

### 5.7 Export View

**Layout:**
```
+-------+-----------------------------------------------+
|       |                                               |
| Side  |   Export                                      |
| bar   |                                               |
|       |   Export Type                                  |
|       |   ( ) Good photos only (742)                  |
|       |   ( ) Good + Review (1,043)                   |
|       |   ( ) All processed (1,240)                   |
|       |   ( ) By category (separate folders)          |
|       |                                               |
|       |   Output Folder                               |
|       |   [________________________________] [Browse]  |
|       |                                               |
|       |   [Export]                                     |
|       |                                               |
|       |   Note: Original files are never modified.    |
|       |   Selected photos will be copied to the       |
|       |   output folder.                              |
|       |                                               |
+-------+-----------------------------------------------+
```

---

## 6. Sidebar Navigation

```
PHOTOSORT

  Dashboard
  Import
  Processing
  Results
  Duplicates
  Export

  ---

  Settings (future)
```

Active item has a subtle background fill. Navigation items are plain text with consistent 14px size.

---

## 7. Responsive Behavior

For a college project, the primary target is desktop (1024px+). The sidebar collapses to a top nav on screens below 768px. Photo grid adapts column count based on available width:

| Viewport | Grid Columns |
|----------|-------------|
| 1280px+  | 5-6 columns |
| 1024px   | 4 columns   |
| 768px    | 3 columns   |
| 480px    | 2 columns   |

---

## 8. Interaction Details

### Photo Card Hover

```
Border-color transitions to var(--border-strong)
Transition: border-color 150ms ease
```

No scale transforms on hover. No shadow changes. Subtle border darkening only.

### Button Active State

```
transform: scale(0.97)
transition: transform 160ms ease-out
```

### Category Change

When a user changes a photo's category via the detail view:
1. PATCH request sent to API
2. Badge updates immediately (optimistic UI)
3. If API fails, badge reverts and error toast appears
4. Dashboard counts refresh on next navigation

### Processing Polling

While processing:
- Frontend polls `/api/projects/{id}/status` every 2 seconds
- Progress bar, current file, and counts update
- On completion, redirect to Results view

---

## 9. Animation Policy

This is a productivity tool viewed repeatedly. Per Emil Kowalski's framework:

| Element | Animation |
|---------|-----------|
| Page transitions | None |
| Modal/panel open | None or 150ms fade |
| Progress bar | 300ms width transition |
| Hover states | 150ms border/background transition |
| Button press | 160ms scale(0.97) |
| Toast notifications | 200ms translate-y entrance, 150ms exit |

No decorative animations. No page-load animations. No scroll animations. The interface should feel instant.
