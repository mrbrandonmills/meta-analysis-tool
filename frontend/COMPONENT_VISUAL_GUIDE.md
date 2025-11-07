# Visual Component Guide

A visual reference for all meta-analysis visualization components with ASCII diagrams and layout descriptions.

---

## 1. ForestPlot Component

### Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Forest Plot - OR with 95% CI                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Study          Year    Weight%      OR [95% CI]                           │
│  ───────────────────────────────────────────────────────────────────────── │
│                            |                                                │
│  Smith 2020      ▪────     12.5       1.45 [1.16, 1.74]                   │
│  Johnson 2019     ▪───     9.8        1.62 [1.27, 1.97]                   │
│  Williams 2021   ▪────     15.2       1.38 [1.15, 1.61]                   │
│  Brown 2018       ▪──      7.3        1.55 [1.12, 1.98]                   │
│  Davis 2022      ▪────     13.1       1.42 [1.15, 1.69]                   │
│                            |                                                │
│  ─────────────────────────────────────────────────────────────────────────  │
│                            |                                                │
│  Overall (Random)    ◆     100        1.45 [1.36, 1.54]                   │
│                      └─────┘                                               │
│                            |                                                │
│  ───────────────────────────────────────────────────────────────────────── │
│       0.5          1.0         1.5         2.0         2.5                 │
│                                                                              │
│  Heterogeneity: I²=0.0%, τ²=0.000, χ²=8.45 (df=9), p=0.488               │
│  Overall effect: Z=9.20, p<0.001                                           │
│                                                                              │
│  Legend: ▪ Individual studies (size ∝ weight)  ◆ Pooled effect  | No effect│
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Visual Elements

- **Square markers (▪):** Size proportional to study weight
- **Horizontal lines (─):** Confidence intervals
- **Diamond (◆):** Pooled effect size with CI width
- **Vertical dashed line (|):** Null effect reference
- **X-axis:** Effect size scale
- **Y-axis:** Studies listed vertically

### Color Scheme

- Squares: Blue (#4299e1)
- Diamond: Green (#38a169)
- CI lines: Gray (#4a5568)
- Null line: Light gray dashed (#cbd5e0)
- Text: Dark gray (#2d3748)

---

## 2. FunnelPlot Component

### Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Funnel Plot                         Egger's test: p = 0.645 ✓ No bias    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SE  ↑                                                                      │
│      │                                                                      │
│ 0.00 │                    ·                                                │
│      │                   / \                                               │
│ 0.05 │                  /   \                                              │
│      │                 /  ·  \                                             │
│ 0.10 │                /   |   \                                            │
│      │               / ·  |  · \                                           │
│ 0.15 │              /     |     \                                          │
│      │             / ·    |    · \                                         │
│ 0.20 │            /    ·  |  ·    \                                        │
│      │           /        |        \                                       │
│ 0.25 │          ──────────┼──────────                                      │
│      └───────────────────────────────────→                                │
│          0.5    1.0    1.5    2.0    2.5           Effect Size           │
│                        │                                                    │
│                    Overall                                                  │
│                                                                              │
│  Legend: · Studies  / \ Funnel (95% CI)  │ Overall effect  ─ Egger's line│
│                                                                              │
│  ⚠ Asymmetric funnel suggests possible publication bias                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Visual Elements

- **Dots (·):** Individual studies (hover for details)
- **Funnel outline (/ \):** 95% confidence interval bounds
- **Vertical line (│):** Overall pooled effect
- **Dashed line (─):** Egger's regression line
- **Inverted Y-axis:** Smaller SE at top (more precise studies)

### Interaction

```
Hover on study point:
┌──────────────────────┐
│ Smith et al. (2020)  │
│ Effect: 1.450        │
│ SE: 0.150            │
└──────────────────────┘
```

### Color Scheme

- Study points: Blue (#4299e1)
- Hovered point: Dark blue (#2b6cb0)
- Center line: Blue (#4299e1)
- Egger's line: Red (#f56565)
- Funnel contours: Light gray (#cbd5e0)

---

## 3. PRISMAFlow Component

### Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PRISMA Flow Diagram                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                           IDENTIFICATION                                    │
│                  ┌─────────────────────────────┐                           │
│                  │  Records identified         │                           │
│                  │  through database searching │                           │
│                  │         2,847               │                           │
│                  └─────────────────────────────┘                           │
│                              ↓                                              │
│                  ┌─────────────────────────────┐                           │
│                  │  Records after duplicates   │                           │
│                  │  removed: 1,955             │                           │
│                  │  (892 duplicates removed)   │                           │
│                  └─────────────────────────────┘                           │
│                              ↓                                              │
│                            SCREENING                                        │
│      ┌─────────────────────────────┐      →      ┌──────────────────┐     │
│      │  Records screened           │              │  Records excluded │     │
│      │         1,955               │              │      1,823        │     │
│      └─────────────────────────────┘              └──────────────────┘     │
│                    ↓                                                        │
│                          ELIGIBILITY                                        │
│      ┌─────────────────────────────┐      →      ┌──────────────────┐     │
│      │  Full-text articles         │              │  Full-text       │     │
│      │  assessed for eligibility   │              │  excluded: 122   │     │
│      │         132                 │              │                  │     │
│      └─────────────────────────────┘              └──────────────────┘     │
│                    ↓                                                        │
│                           INCLUDED                                          │
│                  ┌─────────────────────────────┐                           │
│                  │  Studies included in        │                           │
│                  │  qualitative synthesis      │                           │
│                  │          10                 │                           │
│                  └─────────────────────────────┘                           │
│                              ↓                                              │
│                  ┌─────────────────────────────┐                           │
│                  │  Studies included in        │                           │
│                  │  meta-analysis: 10          │                           │
│                  └─────────────────────────────┘                           │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Summary: 2,847 initial → 1,945 excluded → 10 final (0.4% inclusion rate) │
│                                                                              │
│  ℹ Hover over boxes for exclusion reason breakdown                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Visual Elements

- **Blue boxes:** Identification/screening phases
- **Red boxes:** Exclusions
- **Green boxes:** Final included studies
- **Arrows (↓ →):** Flow direction
- **Animations:** Boxes fade in sequentially

### Hover Tooltip Example

```
Hover on "Records excluded":
┌─────────────────────────┐
│ Breakdown:              │
│ • Not relevant: 1,245   │
│ • Wrong intervention: 342│
│ • Wrong population: 156 │
│ • Wrong outcome: 80     │
└─────────────────────────┘
```

### Color Scheme

- Identification: Blue-50 background, Blue-400 border
- Exclusions: Red-50 background, Red-400 border
- Included: Green-50 background, Green-400 border
- Text: Dark (Blue-900, Red-900, Green-900)

---

## 4. StatisticsPanel Component

### Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Meta-Analysis Statistics                         Random Effects Model     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ▼ Overall Effect                                          [10 studies]    │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Pooled OR                    1.450 [1.360, 1.540]                   │  │
│  │  Z-value                      9.200                                   │  │
│  │  P-value                      <0.001                                  │  │
│  │  Standard Error               0.0500                                  │  │
│  │  ─────────────────────────────────────────────────────────────────   │  │
│  │  ✓ Significant effect detected. Increased risk/odds.                │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ▼ Heterogeneity Assessment                                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  I² statistic                 0.0%                                    │  │
│  │  τ² (Tau-squared)             0.0000                                 │  │
│  │  Q statistic                  8.45                                    │  │
│  │  Degrees of freedom           9                                       │  │
│  │  P-value (Q)                  0.488                                   │  │
│  │  H² statistic                 0.94                                    │  │
│  │  ─────────────────────────────────────────────────────────────────   │  │
│  │  ✓ Low heterogeneity                                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ▶ Publication Bias                                         [Click to expand]│
│                                                                              │
│  ▶ Subgroup Analyses                                        [2 subgroups]   │
│                                                                              │
│  ▶ Sensitivity Analyses                                     [3 analyses]    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Visual Elements

- **▼ Expanded sections:** Show full content
- **▶ Collapsed sections:** Click to expand
- **Blue highlights:** Primary statistics
- **Color-coded interpretations:**
  - Green: Good/acceptable
  - Yellow: Caution/moderate
  - Red: Warning/high
- **Info icons (ⓘ):** Hover for explanations

### Expanded Subgroup Section

```
▼ Subgroup Analyses                                        [2 subgroups]
┌──────────────────────────────────────────────────────────────────────┐
│  Adults (5 studies)                                                  │
│    Effect Size           1.460 [1.350, 1.570]                       │
│    P-value              <0.001                                       │
│    I²                   0.0%                                         │
│  ──────────────────────────────────────────────────────────────────  │
│  Children (5 studies)                                                │
│    Effect Size           1.430 [1.270, 1.590]                       │
│    P-value              <0.001                                       │
│    I²                   0.0%                                         │
└──────────────────────────────────────────────────────────────────────┘
```

### Color Scheme

- Section headers: Gray-50 background
- Highlighted stats: Blue-50 background
- Green interpretation: Green-50 background
- Yellow warning: Yellow-50 background
- Red alert: Red-50 background

---

## 5. StudyCharacteristicsTable Component

### Visual Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Study Characteristics                              [Export CSV ↓]         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  🔍 Search: [________________________]     Subgroup: [All subgroups ▼]     │
│                                                                              │
│  Showing 10 of 10 studies                                                   │
│                                                                              │
├───────┬──────┬─────┬────────┬────────┬────────────┬────────┬─────────┬─────┤
│ Study │ Year │  N  │ Design │   OR   │   95% CI   │ Weight │ Quality │ Sub │
│   ↑   │  ↓   │     │        │        │            │   %    │         │group│
├───────┼──────┼─────┼────────┼────────┼────────────┼────────┼─────────┼─────┤
│Smith  │ 2020 │ 250 │  RCT   │ 1.450  │[1.16,1.74] │  12.5  │ [8/10] │Adults│
│       │      │     │        │        │            │        │  ●●●   │      │
├───────┼──────┼─────┼────────┼────────┼────────────┼────────┼─────────┼─────┤
│Johnson│ 2019 │ 180 │  RCT   │ 1.620  │[1.27,1.97] │   9.8  │ [7/10] │Adults│
│       │      │     │        │        │            │        │  ●●    │      │
├───────┼──────┼─────┼────────┼────────┼────────────┼────────┼─────────┼─────┤
│Williams│2021 │ 320 │  RCT   │ 1.380  │[1.15,1.61] │  15.2  │ [9/10] │Adults│
│       │      │     │        │        │            │        │  ●●●   │      │
├───────┼──────┼─────┼────────┼────────┼────────────┼────────┼─────────┼─────┤
│ ...   │ ...  │ ... │  ...   │  ...   │    ...     │  ...   │  ...   │ ... │
└───────┴──────┴─────┴────────┴────────┴────────────┴────────┴─────────┴─────┘
│                                                                              │
│  Summary Statistics:                                                        │
│  ┌─────────┬─────────┬─────────┬─────────┐                                │
│  │ Total   │ Total   │  Mean   │  Mean   │                                │
│  │ Studies │ Partici-│ Effect  │ Quality │                                │
│  │         │  pants  │  Size   │  Score  │                                │
│  ├─────────┼─────────┼─────────┼─────────┤                                │
│  │   10    │  2,160  │  1.450  │  7.6/10 │                                │
│  └─────────┴─────────┴─────────┴─────────┘                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Visual Elements

- **Search box (🔍):** Real-time filtering
- **Dropdown filters:** Subgroup selection
- **Sortable headers (↑↓):** Click to sort
- **Quality pills (●●●):**
  - Green: High quality (7-10)
  - Yellow: Medium quality (4-6)
  - Red: Low quality (1-3)
- **Summary panel:** Statistics footer
- **Export button:** Download CSV

### Sorting States

```
Before click:  Study
First click:   Study ↑  (ascending)
Second click:  Study ↓  (descending)
```

### Empty State

```
┌──────────────────────────────────┐
│                                  │
│   No studies found matching      │
│   your filters.                  │
│                                  │
│   [Clear filters]                │
│                                  │
└──────────────────────────────────┘
```

### Color Scheme

- Header: Gray-50 background
- Rows: Alternating white/gray-25
- Hover: Light gray-50
- Quality high: Green-100
- Quality medium: Yellow-100
- Quality low: Red-100

---

## Component Comparison

### Size Reference

```
ForestPlot:           FunnelPlot:          PRISMAFlow:
┌──────────────┐      ┌──────────┐         ┌──────────────┐
│              │      │    ·     │         │  ┌────────┐  │
│  ▪──         │      │   / \    │         │  │        │  │
│   ▪───       │      │  /   \   │         │  └────────┘  │
│  ▪──         │      │ / · · \  │         │      ↓       │
│              │      │/       \ │         │  ┌────────┐  │
│  ──◆──       │      └──────────┘         │  │        │  │
└──────────────┘                           │  └────────┘  │
 700x600px          600x500px              └──────────────┘
                                            Auto height

StatisticsPanel:                StudyCharacteristicsTable:
┌──────────────────┐             ┌────────────────────────┐
│ ▼ Section 1      │             │ ┌────┐ Search  Filter │
│ ├──────────────┐ │             │ ├────┼────┼────┼────┤ │
│ │ Stats...     │ │             │ │Row │Row │Row │Row │ │
│ └──────────────┘ │             │ │Row │Row │Row │Row │ │
│                  │             │ │Row │Row │Row │Row │ │
│ ▶ Section 2      │             │ └────┴────┴────┴────┘ │
│                  │             │ Summary panel         │
│ ▶ Section 3      │             └────────────────────────┘
└──────────────────┘              Full width, auto height
Auto height
```

---

## Responsive Behavior

### Desktop (>1024px)

```
┌─────────────────────────────────────────────────────┐
│  ┌──────────────┐       ┌──────────────┐          │
│  │  ForestPlot  │       │  FunnelPlot  │          │
│  │              │       │              │          │
│  └──────────────┘       └──────────────┘          │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │         StudyCharacteristicsTable           │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │            StatisticsPanel                  │ │
│  └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

### Tablet (768px - 1024px)

```
┌────────────────────────────────┐
│  ┌──────────────────────────┐  │
│  │      ForestPlot          │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │      FunnelPlot          │  │
│  └──────────────────────────┘  │
│                                 │
│  ┌──────────────────────────┐  │
│  │ StudyCharacteristicsTable│  │
│  └──────────────────────────┘  │
└────────────────────────────────┘
```

### Mobile (<768px)

```
┌──────────────┐
│ ┌──────────┐ │
│ │ Forest   │ │
│ │ Plot     │ │
│ │ (scroll) │ │
│ └──────────┘ │
│              │
│ ┌──────────┐ │
│ │ Funnel   │ │
│ │ Plot     │ │
│ │ (scroll) │ │
│ └──────────┘ │
│              │
│ ┌──────────┐ │
│ │  Table   │ │
│ │ (scroll) │ │
│ └──────────┘ │
└──────────────┘
```

---

## Interaction Patterns

### ForestPlot
```
User Action: None (static visualization)
Response: Display only
```

### FunnelPlot
```
User Action: Hover over study point
Response: ┌──────────────────┐
          │ Tooltip appears  │
          │ Point enlarges   │
          └──────────────────┘

User Action: Move away
Response: Tooltip disappears, point shrinks
```

### PRISMAFlow
```
User Action: Hover over box
Response: ┌──────────────────┐
          │ Box highlights   │
          │ Tooltip shows    │
          │ breakdown        │
          └──────────────────┘

User Action: Click (no action)
Response: Visual feedback only
```

### StatisticsPanel
```
User Action: Click section header (▶)
Response: ▶ becomes ▼
          Section expands
          Content animates in

User Action: Click expanded section (▼)
Response: ▼ becomes ▶
          Section collapses
          Content hides
```

### StudyCharacteristicsTable
```
User Action: Type in search box
Response: Table filters in real-time
          "Showing X of Y" updates

User Action: Click column header
Response: Table sorts by column
          Arrow indicator appears (↑/↓)
          Toggle asc/desc on repeat click

User Action: Select subgroup filter
Response: Table filters to subgroup
          Count updates

User Action: Click Export CSV
Response: File download begins
          All filtered data exported
```

---

## Accessibility Features Visual Guide

### Keyboard Navigation

```
Tab Order:
┌─────────────────────────────────────┐
│  1. Header/Title                    │
│  2. Search input    ←─┐             │
│  3. Filter dropdown   │ Tab key    │
│  4. Table headers     │             │
│  5. Export button  ─┘               │
│  6. ... (continues)                 │
└─────────────────────────────────────┘
```

### Focus Indicators

```
Normal state:      Focused state:
┌──────────┐       ┌──────────┐
│  Button  │       │  Button  │ ← Blue ring
└──────────┘       └──────────┘   (focus:ring-2)
```

### Screen Reader Annotations

```
<svg aria-label="Forest plot showing effect sizes">
  <title>Forest Plot - Odds Ratio with 95% CI</title>
  ...
</svg>

<button aria-expanded="false" aria-controls="section-1">
  Heterogeneity Assessment
</button>

<table role="table" aria-label="Study characteristics">
  <thead role="rowgroup">
    <tr role="row">
      <th role="columnheader">Study</th>
      ...
```

---

## Theme Variations (Future)

### Light Theme (Current)

```
Background: White (#ffffff)
Text: Dark gray (#1f2937)
Borders: Light gray (#e5e7eb)
Accent: Blue (#3b82f6)
```

### Dark Theme (Potential)

```
Background: Dark gray (#1f2937)
Text: Light gray (#f3f4f6)
Borders: Gray (#4b5563)
Accent: Blue (#60a5fa)
```

---

## Print Layout

### Optimized for Printing

```
@media print {
  ┌─────────────────────────────┐
  │  Study Name                 │  ← Remove colors
  │                              │  ← High contrast
  │  Forest Plot                 │  ← Scale to fit
  │  [Visualization]             │  ← B&W friendly
  │                              │
  │  Statistics Table            │  ← Page breaks
  │  [Rows...]                   │     between sections
  └─────────────────────────────┘
}
```

---

## Component State Diagram

```
                    ┌─────────────┐
                    │   Initial   │
                    │    Load     │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
      ┌────▼────┐     ┌────▼────┐    ┌────▼────┐
      │ Loading │     │  Empty  │    │  Error  │
      └────┬────┘     └─────────┘    └─────────┘
           │
      ┌────▼────┐
      │ Loaded  │
      │ (Ready) │
      └────┬────┘
           │
      ┌────▼──────────────────┐
      │ Interactive States:   │
      │ • Hovering            │
      │ • Filtering           │
      │ • Sorting             │
      │ • Expanding/Collapsing│
      │ • Exporting           │
      └───────────────────────┘
```

---

## Data Flow Diagram

```
Backend API               Component Layer           Visual Layer
┌──────────┐             ┌──────────────┐         ┌──────────┐
│          │   Fetch     │              │ Render  │          │
│  REST    │────────────→│  React       │────────→│  SVG/    │
│  API     │             │  Component   │         │  HTML    │
│          │             │              │         │          │
└──────────┘             └──────┬───────┘         └──────────┘
                                │
                                │ Props
                                ▼
                         ┌──────────────┐
                         │  TypeScript  │
                         │  Interfaces  │
                         └──────────────┘
                                │
                                │ Validation
                                ▼
                         ┌──────────────┐
                         │  Sample      │
                         │  Data        │
                         └──────────────┘
```

---

## File Organization Visual

```
src/
├── components/
│   └── visualizations/
│       ├── ForestPlot.tsx          ← Main components
│       ├── FunnelPlot.tsx
│       ├── PRISMAFlow.tsx
│       ├── StatisticsPanel.tsx
│       ├── StudyCharacteristicsTable.tsx
│       ├── index.ts                ← Exports
│       └── README.md               ← Documentation
│
├── types/
│   └── meta-analysis.ts            ← Type definitions
│
├── data/
│   └── sampleMetaAnalysis.ts       ← Test data
│
└── pages/
    └── examples/
        └── meta-analysis-visualization.tsx  ← Demo page
```

---

**Visual Guide Complete!**

This guide provides ASCII art representations and visual descriptions of all components to help understand their layout and appearance without needing to run the application.

For interactive examples, run the demo page:
```bash
npm run dev
# Visit: http://localhost:3000/examples/meta-analysis-visualization
```
