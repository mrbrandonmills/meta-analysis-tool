# Meta-Analysis Visualization Components - Complete Guide

## Overview

This guide provides comprehensive documentation for the five meta-analysis visualization components built with React 18, TypeScript, and Tailwind CSS. These components are production-ready and fully tested.

---

## Table of Contents

1. [Installation & Setup](#installation--setup)
2. [Components](#components)
   - [ForestPlot](#1-forestplot)
   - [FunnelPlot](#2-funnelplot)
   - [PRISMAFlow](#3-prismaflow)
   - [StatisticsPanel](#4-statisticspanel)
   - [StudyCharacteristicsTable](#5-studycharacteristicstable)
3. [Type Definitions](#type-definitions)
4. [Sample Data](#sample-data)
5. [Live Demo](#live-demo)
6. [Testing](#testing)
7. [Customization](#customization)
8. [Best Practices](#best-practices)

---

## Installation & Setup

### Prerequisites

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "14.0.0",
    "framer-motion": "^10.16.16",
    "lucide-react": "^0.294.0",
    "tailwindcss": "^3.3.0"
  },
  "devDependencies": {
    "typescript": "^5.3.2",
    "@types/react": "^18.2.42"
  }
}
```

### Installation

All components are already installed in the project. To use them:

```typescript
import {
  ForestPlot,
  FunnelPlot,
  PRISMAFlow,
  StatisticsPanel,
  StudyCharacteristicsTable,
} from '@/components/visualizations';
```

---

## Components

### 1. ForestPlot

**Purpose:** Displays effect sizes with confidence intervals for individual studies and pooled effect size.

**File Location:** `/frontend/src/components/visualizations/ForestPlot.tsx`

#### Features

- ✅ Individual study effect sizes with confidence intervals
- ✅ Study weights visualized as square sizes (proportional to weight)
- ✅ Pooled effect displayed as a diamond
- ✅ Null effect reference line
- ✅ Heterogeneity statistics (I², τ², Q, p-value)
- ✅ Support for multiple effect measures (OR, RR, MD, SMD, HR)
- ✅ Fixed and Random effects models
- ✅ Interactive legend

#### Props

```typescript
interface ForestPlotProps {
  results: MetaAnalysisResults;
  title?: string;                // Default: "Forest Plot"
  showWeights?: boolean;          // Default: true
  showHeterogeneity?: boolean;    // Default: true
  height?: number;                // Default: 600
  className?: string;
}
```

#### Usage Example

```typescript
import { ForestPlot } from '@/components/visualizations';
import { sampleMetaAnalysisResults } from '@/data/sampleMetaAnalysis';

function MyComponent() {
  return (
    <ForestPlot
      results={sampleMetaAnalysisResults}
      title="Forest Plot - Odds Ratio with 95% CI"
      showWeights={true}
      showHeterogeneity={true}
      height={600}
    />
  );
}
```

#### Interpretation Guide

- **Square Size:** Larger squares indicate higher study weight
- **Diamond:** Represents pooled effect size with 95% CI width
- **Dashed Line:** Null effect (1.0 for OR/RR/HR, 0 for MD/SMD)
- **Heterogeneity:**
  - I² < 25%: Low heterogeneity
  - I² 25-50%: Moderate heterogeneity
  - I² 50-75%: Substantial heterogeneity
  - I² > 75%: Considerable heterogeneity

---

### 2. FunnelPlot

**Purpose:** Visualizes publication bias by plotting effect size against standard error.

**File Location:** `/frontend/src/components/visualizations/FunnelPlot.tsx`

#### Features

- ✅ Interactive study markers with hover tooltips
- ✅ Egger's regression line for asymmetry detection
- ✅ 95% CI funnel contours
- ✅ Publication bias test results display
- ✅ Trim and Fill analysis visualization
- ✅ Asymmetry detection with visual cues
- ✅ Responsive axes with dynamic scaling

#### Props

```typescript
interface FunnelPlotProps {
  studies: Study[];
  overallEffect: OverallEffect;
  publicationBias?: PublicationBias;
  showEggersLine?: boolean;       // Default: true
  showContours?: boolean;         // Default: true
  height?: number;                // Default: 500
  className?: string;
}
```

#### Usage Example

```typescript
import { FunnelPlot } from '@/components/visualizations';

function MyComponent() {
  return (
    <FunnelPlot
      studies={metaAnalysisResults.studies}
      overallEffect={metaAnalysisResults.overallEffect}
      publicationBias={metaAnalysisResults.publicationBias}
      showEggersLine={true}
      showContours={true}
      height={500}
    />
  );
}
```

#### Interpretation Guide

- **Symmetric Funnel:** No evidence of publication bias
- **Asymmetric Funnel:** Possible publication bias or small-study effects
- **Egger's Test p < 0.05:** Significant asymmetry detected
- **Trim and Fill:** Shows estimated missing studies
- **Points Outside Funnel:** Studies with unusual precision/effect

---

### 3. PRISMAFlow

**Purpose:** Displays PRISMA 2020 compliant flow diagram for systematic review process.

**File Location:** `/frontend/src/components/visualizations/PRISMAFlow.tsx`

#### Features

- ✅ PRISMA 2020 compliant structure
- ✅ Four-phase display (Identification, Screening, Eligibility, Included)
- ✅ Interactive box tooltips with hover states
- ✅ Smooth entrance animations
- ✅ Exclusion reasons breakdown
- ✅ Summary statistics panel
- ✅ Inclusion rate calculation
- ✅ Color-coded boxes (blue, red, green)

#### Props

```typescript
interface PRISMAFlowProps {
  data: PRISMAFlowData;
  interactive?: boolean;          // Default: true
  showAnimations?: boolean;       // Default: true
  className?: string;
}
```

#### Usage Example

```typescript
import { PRISMAFlow } from '@/components/visualizations';
import { samplePRISMAFlowData } from '@/data/sampleMetaAnalysis';

function MyComponent() {
  return (
    <PRISMAFlow
      data={samplePRISMAFlowData}
      interactive={true}
      showAnimations={true}
    />
  );
}
```

#### Data Structure

```typescript
interface PRISMAFlowData {
  identification: {
    databasesSearched: number;
    recordsIdentified: number;
    duplicatesRemoved: number;
    recordsScreened: number;
  };
  screening: {
    recordsExcluded: number;
    exclusionReasons?: Record<string, number>;  // Optional breakdown
  };
  eligibility: {
    fullTextAssessed: number;
    fullTextExcluded: number;
    exclusionReasons?: Record<string, number>;  // Optional breakdown
  };
  included: {
    studiesIncluded: number;
    studiesInMetaAnalysis?: number;             // Optional if different
  };
}
```

---

### 4. StatisticsPanel

**Purpose:** Comprehensive display of meta-analysis statistics with collapsible sections.

**File Location:** `/frontend/src/components/visualizations/StatisticsPanel.tsx`

#### Features

- ✅ Overall effect size with confidence interval
- ✅ Heterogeneity metrics (I², τ², Q, H², p-value)
- ✅ Publication bias tests (Egger's, Begg's, Trim & Fill)
- ✅ Subgroup analysis results
- ✅ Sensitivity analysis results
- ✅ Collapsible sections with expand/collapse
- ✅ Contextual interpretations and guidance
- ✅ Color-coded significance indicators
- ✅ Tooltip help for complex statistics

#### Props

```typescript
interface StatisticsPanelProps {
  results: MetaAnalysisResults;
  showSubgroups?: boolean;        // Default: true
  showSensitivity?: boolean;      // Default: true
  className?: string;
}
```

#### Usage Example

```typescript
import { StatisticsPanel } from '@/components/visualizations';

function MyComponent() {
  return (
    <StatisticsPanel
      results={metaAnalysisResults}
      showSubgroups={true}
      showSensitivity={true}
    />
  );
}
```

#### Sections

1. **Overall Effect**
   - Pooled effect size with 95% CI
   - Z-value and p-value
   - Standard error
   - Significance interpretation

2. **Heterogeneity Assessment**
   - I² statistic with interpretation
   - τ² (between-study variance)
   - Q statistic with p-value
   - H² statistic
   - Recommendations based on heterogeneity level

3. **Publication Bias** (if available)
   - Egger's test results
   - Begg's test results
   - Trim and Fill analysis
   - Interpretation and warnings

4. **Subgroup Analyses** (if available)
   - Effect size per subgroup
   - Heterogeneity within subgroups
   - Number of studies per subgroup

5. **Sensitivity Analyses** (if available)
   - Named sensitivity analyses
   - Effect sizes after exclusions
   - Studies removed for each analysis

---

### 5. StudyCharacteristicsTable

**Purpose:** Sortable and filterable table displaying study characteristics and quality scores.

**File Location:** `/frontend/src/components/visualizations/StudyCharacteristicsTable.tsx`

#### Features

- ✅ Sortable columns (author, year, sample size, effect size, etc.)
- ✅ Search functionality across author, year, and design
- ✅ Subgroup filtering
- ✅ Quality score visualization with color coding
- ✅ CSV export functionality
- ✅ Summary statistics footer
- ✅ Responsive design with hover states
- ✅ Empty state handling
- ✅ Clear filters button

#### Props

```typescript
interface StudyCharacteristicsTableProps {
  studies: Study[];
  effectMeasure: EffectMeasure;
  showQualityScores?: boolean;    // Default: true
  sortable?: boolean;             // Default: true
  filterable?: boolean;           // Default: true
  className?: string;
}
```

#### Usage Example

```typescript
import { StudyCharacteristicsTable } from '@/components/visualizations';

function MyComponent() {
  return (
    <StudyCharacteristicsTable
      studies={metaAnalysisResults.studies}
      effectMeasure="OR"
      showQualityScores={true}
      sortable={true}
      filterable={true}
    />
  );
}
```

#### Features Detail

**Sorting:**
- Click column headers to sort
- Toggle ascending/descending
- Visual indicators (arrows)

**Filtering:**
- Real-time search
- Subgroup dropdown filter
- Result count display

**Quality Scores:**
- Green: 7-10 (high quality)
- Yellow: 4-6 (medium quality)
- Red: 1-3 (low quality)

**CSV Export:**
- Downloads all filtered studies
- Includes all columns
- Formatted with headers

**Summary Statistics:**
- Total studies count
- Total participants
- Mean effect size
- Mean quality score

---

## Type Definitions

All TypeScript interfaces are defined in `/frontend/src/types/meta-analysis.ts`:

### Core Types

```typescript
export type EffectMeasure = 'OR' | 'RR' | 'MD' | 'SMD' | 'HR';

export interface Study {
  id: string;
  author: string;
  year: number;
  sampleSize: number;
  studyDesign: string;
  effectSize: number;
  standardError: number;
  lowerCI: number;
  upperCI: number;
  weight: number;
  qualityScore?: number;      // 0-10 scale
  subgroup?: string;
}

export interface HeterogeneityStats {
  Q: number;                   // Cochran's Q statistic
  df: number;                  // Degrees of freedom
  pValue: number;
  I2: number;                  // I² percentage
  tau2: number;                // τ² (between-study variance)
  H2?: number;                 // H² statistic
}

export interface OverallEffect {
  effectSize: number;
  standardError: number;
  lowerCI: number;
  upperCI: number;
  zValue: number;
  pValue: number;
}

export interface PublicationBias {
  eggersTest?: {
    intercept: number;
    pValue: number;
  };
  beggTest?: {
    tau: number;              // Kendall's tau
    pValue: number;
  };
  trimAndFill?: {
    adjustedEffectSize: number;
    missingStudies: number;
  };
}

export interface SubgroupAnalysis {
  subgroupName: string;
  studies: Study[];
  effectSize: number;
  lowerCI: number;
  upperCI: number;
  heterogeneity: HeterogeneityStats;
  pValue: number;
}

export interface SensitivityAnalysis {
  name: string;
  description: string;
  effectSize: number;
  lowerCI: number;
  upperCI: number;
  studiesRemoved?: string[];
}

export interface MetaAnalysisResults {
  studies: Study[];
  overallEffect: OverallEffect;
  heterogeneity: HeterogeneityStats;
  publicationBias?: PublicationBias;
  subgroupAnalyses?: SubgroupAnalysis[];
  sensitivityAnalyses?: SensitivityAnalysis[];
  effectMeasure: EffectMeasure;
  model: 'fixed' | 'random';
}
```

---

## Sample Data

Sample data is provided in `/frontend/src/data/sampleMetaAnalysis.ts`:

### Available Datasets

1. **sampleMetaAnalysisResults** - Low heterogeneity dataset
   - 10 studies
   - I² = 0.0%
   - No publication bias
   - Includes subgroup analyses (Adults vs Children)
   - Includes sensitivity analyses

2. **sampleHighHeterogeneityResults** - High heterogeneity dataset
   - 6 studies
   - I² = 79.8%
   - Evidence of publication bias
   - Demonstrates handling of heterogeneous data

3. **samplePRISMAFlowData** - PRISMA flow data
   - Complete systematic review process
   - 2847 initial records
   - 10 final included studies
   - Detailed exclusion reasons

### Usage

```typescript
import {
  sampleMetaAnalysisResults,
  samplePRISMAFlowData,
  sampleHighHeterogeneityResults,
} from '@/data/sampleMetaAnalysis';

// Use in your components
<ForestPlot results={sampleMetaAnalysisResults} />
<PRISMAFlow data={samplePRISMAFlowData} />
```

---

## Live Demo

A complete demo page is available at:

**File:** `/frontend/src/pages/examples/meta-analysis-visualization.tsx`

**URL:** `http://localhost:3000/examples/meta-analysis-visualization`

### Demo Features

- Dataset selector (low vs high heterogeneity)
- All 5 components integrated
- Usage examples with code snippets
- Feature highlights
- Interactive demonstration

### Running the Demo

```bash
cd /Users/brandon/meta-analysis-tool/frontend
npm run dev
```

Then navigate to: `http://localhost:3000/examples/meta-analysis-visualization`

---

## Testing

All components have comprehensive test coverage using Vitest and React Testing Library.

**Test Location:** `/frontend/tests/components/visualizations/`

### Test Files

- `ForestPlot.test.tsx` - Forest plot rendering and interactions
- `FunnelPlot.test.tsx` - Funnel plot and hover states
- `PRISMAFlow.test.tsx` - PRISMA flow animations and interactions
- `StatisticsPanel.test.tsx` - Statistics display and collapsible sections
- `StudyCharacteristicsTable.test.tsx` - Sorting, filtering, and export

### Running Tests

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage

# Run specific test file
npm test ForestPlot.test.tsx
```

### Test Coverage

All components have:
- ✅ Component rendering tests
- ✅ Props validation tests
- ✅ User interaction tests
- ✅ Edge case handling
- ✅ Accessibility tests

---

## Customization

### Styling

All components use Tailwind CSS classes and can be customized via:

1. **className prop:** Add custom classes to any component
2. **Tailwind config:** Modify `/frontend/tailwind.config.js`
3. **Component styles:** Edit component files directly

Example:

```typescript
<ForestPlot
  results={results}
  className="shadow-xl rounded-xl border-2 border-blue-500"
/>
```

### Color Schemes

Current color scheme:
- Primary: Blue (`blue-500`, `blue-600`)
- Success: Green (`green-600`, `green-700`)
- Warning: Yellow/Amber (`yellow-500`, `amber-600`)
- Danger: Red (`red-500`, `red-600`)
- Neutral: Gray (`gray-500`, `gray-600`)

### Typography

- Headers: `font-semibold`, `font-bold`
- Body: `text-sm`, `text-base`
- Labels: `text-xs`, `uppercase`, `tracking-wide`

### Dimensions

All components accept height props:
- `ForestPlot`: Default 600px
- `FunnelPlot`: Default 500px
- Others: Auto-height based on content

---

## Best Practices

### 1. Data Validation

Always validate your data before passing to components:

```typescript
// Check for required fields
if (!results.studies || results.studies.length === 0) {
  return <EmptyState message="No studies available" />;
}

// Check for valid effect sizes
const validStudies = results.studies.filter(
  study => !isNaN(study.effectSize) && !isNaN(study.standardError)
);
```

### 2. Performance Optimization

For large datasets:

```typescript
// Use React.memo for expensive components
const MemoizedForestPlot = React.memo(ForestPlot);

// Debounce search inputs
const debouncedSearch = useMemo(
  () => debounce((value) => setSearchTerm(value), 300),
  []
);
```

### 3. Responsive Design

Components are responsive by default, but consider:

```typescript
// Mobile-friendly container
<div className="w-full overflow-x-auto">
  <ForestPlot results={results} />
</div>

// Adjust height for mobile
const isMobile = useMediaQuery('(max-width: 768px)');
<ForestPlot height={isMobile ? 400 : 600} />
```

### 4. Accessibility

Components include basic accessibility features:

- Semantic HTML structure
- ARIA labels where appropriate
- Keyboard navigation support
- Screen reader friendly

Enhance further:

```typescript
<div role="region" aria-label="Meta-analysis forest plot">
  <ForestPlot results={results} />
</div>
```

### 5. Error Handling

Wrap components in error boundaries:

```typescript
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
    </div>
  );
}

<ErrorBoundary FallbackComponent={ErrorFallback}>
  <ForestPlot results={results} />
</ErrorBoundary>
```

### 6. Loading States

Add loading indicators:

```typescript
function MyComponent() {
  const { data, isLoading } = useMetaAnalysisData();

  if (isLoading) {
    return <Skeleton />;
  }

  return <ForestPlot results={data} />;
}
```

---

## Integration Example

Complete example showing all components together:

```typescript
import React from 'react';
import {
  ForestPlot,
  FunnelPlot,
  PRISMAFlow,
  StatisticsPanel,
  StudyCharacteristicsTable,
} from '@/components/visualizations';
import { useMetaAnalysisData } from '@/hooks/useMetaAnalysisData';

export default function MetaAnalysisResults() {
  const { results, prismaData, isLoading, error } = useMetaAnalysisData();

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!results) return <EmptyState />;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Summary Statistics */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Statistical Summary</h2>
        <StatisticsPanel
          results={results}
          showSubgroups={true}
          showSensitivity={true}
        />
      </section>

      {/* Forest Plot */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Forest Plot</h2>
        <ForestPlot
          results={results}
          title={`${results.effectMeasure} with 95% CI`}
          showWeights={true}
          showHeterogeneity={true}
        />
      </section>

      {/* Funnel Plot */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Publication Bias</h2>
        <FunnelPlot
          studies={results.studies}
          overallEffect={results.overallEffect}
          publicationBias={results.publicationBias}
          showEggersLine={true}
          showContours={true}
        />
      </section>

      {/* Study Table */}
      <section>
        <h2 className="text-2xl font-bold mb-4">Study Characteristics</h2>
        <StudyCharacteristicsTable
          studies={results.studies}
          effectMeasure={results.effectMeasure}
          showQualityScores={true}
          sortable={true}
          filterable={true}
        />
      </section>

      {/* PRISMA Flow */}
      {prismaData && (
        <section>
          <h2 className="text-2xl font-bold mb-4">PRISMA Flow Diagram</h2>
          <PRISMAFlow
            data={prismaData}
            interactive={true}
            showAnimations={true}
          />
        </section>
      )}
    </div>
  );
}
```

---

## Troubleshooting

### Common Issues

**1. Components not rendering:**
- Check that all required props are provided
- Verify data structure matches TypeScript interfaces
- Check browser console for errors

**2. Styling issues:**
- Ensure Tailwind CSS is configured properly
- Check for CSS conflicts with other libraries
- Verify className prop is passed correctly

**3. Type errors:**
- Update TypeScript to version 5+
- Check that all interfaces are imported correctly
- Run `npm run type-check`

**4. Performance issues:**
- Use React.memo for expensive components
- Implement virtualization for large tables
- Debounce search/filter operations

---

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

Modern features used:
- CSS Grid & Flexbox
- SVG rendering
- ES2020+ JavaScript
- React 18 features

---

## Contributing

When modifying or adding components:

1. Update type definitions in `/src/types/meta-analysis.ts`
2. Add sample data in `/src/data/sampleMetaAnalysis.ts`
3. Create comprehensive tests in `/tests/components/visualizations/`
4. Update component exports in `/src/components/visualizations/index.ts`
5. Update this documentation
6. Run tests and type checking before committing

---

## Resources

### Documentation
- Component README: `/frontend/src/components/visualizations/README.md`
- Type definitions: `/frontend/src/types/meta-analysis.ts`
- Sample data: `/frontend/src/data/sampleMetaAnalysis.ts`
- Demo page: `/frontend/src/pages/examples/meta-analysis-visualization.tsx`

### External Resources
- [PRISMA 2020 Guidelines](http://www.prisma-statement.org/)
- [Cochrane Handbook](https://training.cochrane.org/handbook)
- [Meta-Analysis Methods](https://www.bmj.com/about-bmj/resources-readers/publications/statistics-square-one/12-survival-analysis)

---

## License

Part of the Meta-Analysis Tool project.

---

## Support

For issues, questions, or contributions:
- Review component README files
- Check test files for usage examples
- Run the demo page for interactive examples
- Consult TypeScript interfaces for data structures

---

## Summary

All five visualization components are fully implemented, tested, and production-ready:

✅ **ForestPlot** - Effect sizes with confidence intervals and pooled effect
✅ **FunnelPlot** - Publication bias assessment with interactive tooltips
✅ **PRISMAFlow** - PRISMA 2020 compliant flow diagram
✅ **StatisticsPanel** - Comprehensive statistics with collapsible sections
✅ **StudyCharacteristicsTable** - Sortable, filterable table with CSV export

All components include:
- TypeScript interfaces
- Comprehensive tests
- Sample data
- Interactive demo page
- Responsive design
- Accessibility features

**Total Files Created:**
- 5 Component files
- 5 Test files
- 1 Type definition file
- 1 Sample data file
- 1 Index file
- 1 Demo page
- 2 Documentation files

**Ready for production use!**
