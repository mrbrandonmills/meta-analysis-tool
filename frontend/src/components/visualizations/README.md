# Meta-Analysis Visualization Components

A comprehensive suite of React components for visualizing meta-analysis results, built with TypeScript, React 18, and Tailwind CSS.

## Components

### 1. ForestPlot

Displays effect sizes with confidence intervals for individual studies and pooled effect size.

**Features:**
- Effect sizes with confidence intervals
- Individual study results with weight visualization
- Pooled effect size displayed as a diamond
- Support for multiple effect measures (OR, RR, MD, SMD, HR)
- Heterogeneity statistics display
- Null effect reference line

**Usage:**
```typescript
import { ForestPlot } from '@/components/visualizations';

<ForestPlot
  results={metaAnalysisResults}
  title="Forest Plot - OR with 95% CI"
  showWeights={true}
  showHeterogeneity={true}
  height={600}
/>
```

**Props:**
- `results: MetaAnalysisResults` - Meta-analysis data
- `title?: string` - Plot title (default: "Forest Plot")
- `showWeights?: boolean` - Show study weights (default: true)
- `showHeterogeneity?: boolean` - Show heterogeneity stats (default: true)
- `height?: number` - Plot height in pixels (default: 600)
- `className?: string` - Additional CSS classes

---

### 2. FunnelPlot

Plots effect size vs standard error to assess publication bias.

**Features:**
- Interactive study tooltips on hover
- Egger's regression line
- 95% CI funnel contours
- Publication bias test results
- Trim and Fill visualization
- Asymmetry detection

**Usage:**
```typescript
import { FunnelPlot } from '@/components/visualizations';

<FunnelPlot
  studies={studies}
  overallEffect={overallEffect}
  publicationBias={publicationBias}
  showEggersLine={true}
  showContours={true}
  height={500}
/>
```

**Props:**
- `studies: Study[]` - Array of study data
- `overallEffect: OverallEffect` - Overall pooled effect
- `publicationBias?: PublicationBias` - Publication bias test results
- `showEggersLine?: boolean` - Display Egger's line (default: true)
- `showContours?: boolean` - Show funnel contours (default: true)
- `height?: number` - Plot height in pixels (default: 500)
- `className?: string` - Additional CSS classes

---

### 3. PRISMAFlow

Displays a PRISMA 2020 compliant flow diagram for systematic review process.

**Features:**
- Interactive boxes with tooltips
- Smooth animations
- Exclusion reasons breakdown
- Summary statistics
- Inclusion rate calculation
- Four-phase structure (Identification, Screening, Eligibility, Included)

**Usage:**
```typescript
import { PRISMAFlow } from '@/components/visualizations';

<PRISMAFlow
  data={prismaFlowData}
  interactive={true}
  showAnimations={true}
/>
```

**Props:**
- `data: PRISMAFlowData` - PRISMA flow data
- `interactive?: boolean` - Enable hover interactions (default: true)
- `showAnimations?: boolean` - Show entrance animations (default: true)
- `className?: string` - Additional CSS classes

---

### 4. StatisticsPanel

Comprehensive display of meta-analysis statistics with collapsible sections.

**Features:**
- Overall effect size with CI
- Heterogeneity metrics (I², τ², Q, H²)
- Publication bias tests (Egger's, Begg's, Trim & Fill)
- Subgroup analyses
- Sensitivity analyses
- Contextual interpretations
- Collapsible sections

**Usage:**
```typescript
import { StatisticsPanel } from '@/components/visualizations';

<StatisticsPanel
  results={metaAnalysisResults}
  showSubgroups={true}
  showSensitivity={true}
/>
```

**Props:**
- `results: MetaAnalysisResults` - Meta-analysis data
- `showSubgroups?: boolean` - Display subgroup analyses (default: true)
- `showSensitivity?: boolean` - Display sensitivity analyses (default: true)
- `className?: string` - Additional CSS classes

---

### 5. StudyCharacteristicsTable

Sortable and filterable table of study characteristics.

**Features:**
- Sortable columns
- Search functionality
- Subgroup filtering
- Quality score visualization
- CSV export
- Summary statistics
- Responsive design

**Usage:**
```typescript
import { StudyCharacteristicsTable } from '@/components/visualizations';

<StudyCharacteristicsTable
  studies={studies}
  effectMeasure="OR"
  showQualityScores={true}
  sortable={true}
  filterable={true}
/>
```

**Props:**
- `studies: Study[]` - Array of study data
- `effectMeasure: EffectMeasure` - Type of effect measure
- `showQualityScores?: boolean` - Display quality scores (default: true)
- `sortable?: boolean` - Enable column sorting (default: true)
- `filterable?: boolean` - Enable filtering (default: true)
- `className?: string` - Additional CSS classes

---

## Data Types

### Study
```typescript
interface Study {
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
  qualityScore?: number;
  subgroup?: string;
}
```

### MetaAnalysisResults
```typescript
interface MetaAnalysisResults {
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

### PRISMAFlowData
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
    exclusionReasons?: Record<string, number>;
  };
  eligibility: {
    fullTextAssessed: number;
    fullTextExcluded: number;
    exclusionReasons?: Record<string, number>;
  };
  included: {
    studiesIncluded: number;
    studiesInMetaAnalysis?: number;
  };
}
```

For complete type definitions, see `/src/types/meta-analysis.ts`.

---

## Installation

These components require the following dependencies:

```bash
npm install react react-dom
npm install framer-motion lucide-react
npm install d3 @types/d3
```

---

## Sample Data

Sample data is provided in `/src/data/sampleMetaAnalysis.ts`:

```typescript
import {
  sampleMetaAnalysisResults,
  samplePRISMAFlowData,
  sampleHighHeterogeneityResults,
} from '@/data/sampleMetaAnalysis';
```

---

## Complete Example

See `/src/pages/examples/meta-analysis-visualization.tsx` for a complete integration example showing all components together.

```typescript
import {
  ForestPlot,
  FunnelPlot,
  PRISMAFlow,
  StatisticsPanel,
  StudyCharacteristicsTable,
} from '@/components/visualizations';

function MetaAnalysisResults({ results, prismaData }) {
  return (
    <div className="space-y-8">
      <StatisticsPanel results={results} />
      <ForestPlot results={results} />
      <FunnelPlot
        studies={results.studies}
        overallEffect={results.overallEffect}
        publicationBias={results.publicationBias}
      />
      <StudyCharacteristicsTable
        studies={results.studies}
        effectMeasure={results.effectMeasure}
      />
      <PRISMAFlow data={prismaData} />
    </div>
  );
}
```

---

## Testing

All components have comprehensive test coverage using Vitest and React Testing Library.

Run tests:
```bash
npm test
```

Test files are located in `/tests/components/visualizations/`.

---

## Styling

Components use Tailwind CSS for styling. Ensure your project has Tailwind CSS configured.

Custom styles can be added via the `className` prop on each component.

---

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- React 18+
- TypeScript 5+

---

## Contributing

When adding new visualization components:

1. Create component in `/src/components/visualizations/`
2. Add TypeScript types in `/src/types/meta-analysis.ts`
3. Create tests in `/tests/components/visualizations/`
4. Update exports in `/src/components/visualizations/index.ts`
5. Add sample data if needed in `/src/data/sampleMetaAnalysis.ts`
6. Document component in this README

---

## License

Part of the Meta-Analysis Tool project.

---

## Support

For issues or questions, please refer to the main project documentation or create an issue in the repository.
