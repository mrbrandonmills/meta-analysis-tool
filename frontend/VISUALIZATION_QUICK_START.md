# Meta-Analysis Visualizations - Quick Start Guide

## 5-Minute Setup

Get started with meta-analysis visualizations in 5 minutes.

---

## Step 1: Import Components

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

## Step 2: Import Sample Data

```typescript
import {
  sampleMetaAnalysisResults,
  samplePRISMAFlowData,
} from '@/data/sampleMetaAnalysis';
```

---

## Step 3: Use Components

### Option A: All Components Together

```typescript
export default function MyPage() {
  return (
    <div className="space-y-8 p-8">
      <StatisticsPanel results={sampleMetaAnalysisResults} />
      <ForestPlot results={sampleMetaAnalysisResults} />
      <FunnelPlot
        studies={sampleMetaAnalysisResults.studies}
        overallEffect={sampleMetaAnalysisResults.overallEffect}
        publicationBias={sampleMetaAnalysisResults.publicationBias}
      />
      <StudyCharacteristicsTable
        studies={sampleMetaAnalysisResults.studies}
        effectMeasure={sampleMetaAnalysisResults.effectMeasure}
      />
      <PRISMAFlow data={samplePRISMAFlowData} />
    </div>
  );
}
```

### Option B: Individual Components

#### Forest Plot Only

```typescript
export default function ForestPlotPage() {
  return (
    <ForestPlot
      results={sampleMetaAnalysisResults}
      title="Treatment Effect - Odds Ratio"
      showWeights={true}
      showHeterogeneity={true}
      height={600}
    />
  );
}
```

#### Statistics Panel Only

```typescript
export default function StatsPage() {
  return (
    <StatisticsPanel
      results={sampleMetaAnalysisResults}
      showSubgroups={true}
      showSensitivity={true}
    />
  );
}
```

#### Study Table Only

```typescript
export default function TablePage() {
  return (
    <StudyCharacteristicsTable
      studies={sampleMetaAnalysisResults.studies}
      effectMeasure="OR"
      showQualityScores={true}
      sortable={true}
      filterable={true}
    />
  );
}
```

---

## Step 4: Use Your Own Data

### Create Your Data Object

```typescript
import { MetaAnalysisResults } from '@/types/meta-analysis';

const myResults: MetaAnalysisResults = {
  studies: [
    {
      id: '1',
      author: 'Smith et al.',
      year: 2023,
      sampleSize: 200,
      studyDesign: 'RCT',
      effectSize: 1.5,
      standardError: 0.2,
      lowerCI: 1.1,
      upperCI: 1.9,
      weight: 15.0,
      qualityScore: 8,
      subgroup: 'Adults',
    },
    // ... more studies
  ],
  overallEffect: {
    effectSize: 1.45,
    standardError: 0.1,
    lowerCI: 1.25,
    upperCI: 1.65,
    zValue: 4.5,
    pValue: 0.00001,
  },
  heterogeneity: {
    Q: 10.5,
    df: 9,
    pValue: 0.31,
    I2: 14.3,
    tau2: 0.02,
    H2: 1.17,
  },
  effectMeasure: 'OR',
  model: 'random',
};
```

### Use Your Data

```typescript
<ForestPlot results={myResults} />
<StatisticsPanel results={myResults} />
```

---

## Step 5: Customize Appearance

### Add Custom Styles

```typescript
<ForestPlot
  results={myResults}
  className="shadow-2xl rounded-xl border-4 border-blue-500"
  height={800}
/>
```

### Conditional Rendering

```typescript
export default function ConditionalPage() {
  const [showForest, setShowForest] = useState(true);
  const [showFunnel, setShowFunnel] = useState(true);

  return (
    <div>
      <div className="mb-4 space-x-4">
        <button onClick={() => setShowForest(!showForest)}>
          Toggle Forest Plot
        </button>
        <button onClick={() => setShowFunnel(!showFunnel)}>
          Toggle Funnel Plot
        </button>
      </div>

      {showForest && <ForestPlot results={myResults} />}
      {showFunnel && (
        <FunnelPlot
          studies={myResults.studies}
          overallEffect={myResults.overallEffect}
        />
      )}
    </div>
  );
}
```

---

## Common Patterns

### 1. Loading State

```typescript
export default function MyPage() {
  const [results, setResults] = useState<MetaAnalysisResults | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData().then(data => {
      setResults(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!results) return <div>No data</div>;

  return <ForestPlot results={results} />;
}
```

### 2. Dataset Switcher

```typescript
export default function DatasetSwitcher() {
  const [dataset, setDataset] = useState<'low' | 'high'>('low');

  const results = dataset === 'low'
    ? sampleMetaAnalysisResults
    : sampleHighHeterogeneityResults;

  return (
    <div>
      <select value={dataset} onChange={(e) => setDataset(e.target.value as any)}>
        <option value="low">Low Heterogeneity</option>
        <option value="high">High Heterogeneity</option>
      </select>

      <ForestPlot results={results} />
      <StatisticsPanel results={results} />
    </div>
  );
}
```

### 3. Export Functionality

```typescript
export default function ExportPage() {
  const handleExport = () => {
    // Table already has CSV export built-in
    // For custom exports:
    const data = JSON.stringify(sampleMetaAnalysisResults, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'meta-analysis-results.json';
    a.click();
  };

  return (
    <div>
      <button onClick={handleExport}>Export JSON</button>
      <StudyCharacteristicsTable
        studies={sampleMetaAnalysisResults.studies}
        effectMeasure="OR"
      />
    </div>
  );
}
```

### 4. Responsive Layout

```typescript
export default function ResponsivePage() {
  return (
    <div className="container mx-auto px-4">
      {/* Mobile: Stack vertically */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <ForestPlot results={sampleMetaAnalysisResults} height={400} />
        </div>
        <div>
          <FunnelPlot
            studies={sampleMetaAnalysisResults.studies}
            overallEffect={sampleMetaAnalysisResults.overallEffect}
            height={400}
          />
        </div>
      </div>

      {/* Full width */}
      <div className="mt-8">
        <StatisticsPanel results={sampleMetaAnalysisResults} />
      </div>
    </div>
  );
}
```

---

## Quick Reference

### All Props at a Glance

```typescript
// ForestPlot
<ForestPlot
  results={MetaAnalysisResults}    // Required
  title="string"                   // Optional
  showWeights={boolean}            // Optional, default: true
  showHeterogeneity={boolean}      // Optional, default: true
  height={number}                  // Optional, default: 600
  className="string"               // Optional
/>

// FunnelPlot
<FunnelPlot
  studies={Study[]}                // Required
  overallEffect={OverallEffect}    // Required
  publicationBias={PublicationBias} // Optional
  showEggersLine={boolean}         // Optional, default: true
  showContours={boolean}           // Optional, default: true
  height={number}                  // Optional, default: 500
  className="string"               // Optional
/>

// PRISMAFlow
<PRISMAFlow
  data={PRISMAFlowData}            // Required
  interactive={boolean}            // Optional, default: true
  showAnimations={boolean}         // Optional, default: true
  className="string"               // Optional
/>

// StatisticsPanel
<StatisticsPanel
  results={MetaAnalysisResults}    // Required
  showSubgroups={boolean}          // Optional, default: true
  showSensitivity={boolean}        // Optional, default: true
  className="string"               // Optional
/>

// StudyCharacteristicsTable
<StudyCharacteristicsTable
  studies={Study[]}                // Required
  effectMeasure={EffectMeasure}    // Required
  showQualityScores={boolean}      // Optional, default: true
  sortable={boolean}               // Optional, default: true
  filterable={boolean}             // Optional, default: true
  className="string"               // Optional
/>
```

---

## Data Structure Quick Reference

### Minimal Study Object

```typescript
const study: Study = {
  id: '1',
  author: 'Smith et al.',
  year: 2023,
  sampleSize: 200,
  studyDesign: 'RCT',
  effectSize: 1.5,
  standardError: 0.2,
  lowerCI: 1.1,
  upperCI: 1.9,
  weight: 15.0,
  // Optional fields:
  qualityScore: 8,
  subgroup: 'Adults',
};
```

### Minimal MetaAnalysisResults Object

```typescript
const results: MetaAnalysisResults = {
  studies: [study1, study2, ...],
  overallEffect: {
    effectSize: 1.45,
    standardError: 0.1,
    lowerCI: 1.25,
    upperCI: 1.65,
    zValue: 4.5,
    pValue: 0.00001,
  },
  heterogeneity: {
    Q: 10.5,
    df: 9,
    pValue: 0.31,
    I2: 14.3,
    tau2: 0.02,
  },
  effectMeasure: 'OR', // or 'RR', 'MD', 'SMD', 'HR'
  model: 'random',     // or 'fixed'
};
```

### Minimal PRISMAFlowData Object

```typescript
const prismaData: PRISMAFlowData = {
  identification: {
    databasesSearched: 5,
    recordsIdentified: 1000,
    duplicatesRemoved: 200,
    recordsScreened: 800,
  },
  screening: {
    recordsExcluded: 700,
  },
  eligibility: {
    fullTextAssessed: 100,
    fullTextExcluded: 90,
  },
  included: {
    studiesIncluded: 10,
  },
};
```

---

## Testing Your Implementation

### 1. Start Dev Server

```bash
cd /Users/brandon/meta-analysis-tool/frontend
npm run dev
```

### 2. View Demo Page

Navigate to: `http://localhost:3000/examples/meta-analysis-visualization`

### 3. Create Test Page

Create `/frontend/src/pages/test-viz.tsx`:

```typescript
import { ForestPlot, StatisticsPanel } from '@/components/visualizations';
import { sampleMetaAnalysisResults } from '@/data/sampleMetaAnalysis';

export default function TestViz() {
  return (
    <div className="p-8 space-y-8">
      <h1 className="text-3xl font-bold">Test Visualizations</h1>
      <StatisticsPanel results={sampleMetaAnalysisResults} />
      <ForestPlot results={sampleMetaAnalysisResults} />
    </div>
  );
}
```

### 4. View Your Test Page

Navigate to: `http://localhost:3000/test-viz`

---

## Troubleshooting Quick Fixes

### Error: "Cannot find module '@/components/visualizations'"

**Fix:** Check your `tsconfig.json` has the path alias:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### Error: "Property 'effectSize' does not exist"

**Fix:** Import the type and check your data structure:

```typescript
import { Study } from '@/types/meta-analysis';

// Ensure your study object has all required fields
const study: Study = { /* ... */ };
```

### Components not styling correctly

**Fix:** Ensure Tailwind is configured:

```bash
# Check tailwind.config.js includes components path
content: [
  './src/**/*.{js,ts,jsx,tsx}',
],
```

### SVG not rendering

**Fix:** Check if Next.js is configured to handle SVG:

```javascript
// next.config.js
module.exports = {
  webpack(config) {
    config.module.rules.push({
      test: /\.svg$/,
      use: ['@svgr/webpack'],
    });
    return config;
  },
};
```

---

## Next Steps

1. ✅ **Read Full Guide:** See `VISUALIZATION_COMPONENTS_GUIDE.md`
2. ✅ **View Demo:** Run `npm run dev` and visit `/examples/meta-analysis-visualization`
3. ✅ **Check Tests:** Run `npm test` to see component tests
4. ✅ **Customize:** Modify components to fit your needs
5. ✅ **Integrate:** Add to your existing application

---

## Get Help

- **Component Docs:** `/frontend/src/components/visualizations/README.md`
- **Type Definitions:** `/frontend/src/types/meta-analysis.ts`
- **Sample Data:** `/frontend/src/data/sampleMetaAnalysis.ts`
- **Demo Page:** `/frontend/src/pages/examples/meta-analysis-visualization.tsx`

---

**You're ready to go! Start with the demo page and customize from there.**
