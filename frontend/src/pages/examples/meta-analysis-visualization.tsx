import React, { useState } from 'react';
import Head from 'next/head';
import { ForestPlot } from '@/components/visualizations/ForestPlot';
import { FunnelPlot } from '@/components/visualizations/FunnelPlot';
import { PRISMAFlow } from '@/components/visualizations/PRISMAFlow';
import { StatisticsPanel } from '@/components/visualizations/StatisticsPanel';
import { StudyCharacteristicsTable } from '@/components/visualizations/StudyCharacteristicsTable';
import {
  sampleMetaAnalysisResults,
  samplePRISMAFlowData,
  sampleHighHeterogeneityResults,
} from '@/data/sampleMetaAnalysis';

/**
 * Meta-Analysis Visualization Example Page
 *
 * This page demonstrates the complete integration of all meta-analysis
 * visualization components with sample data.
 */
export default function MetaAnalysisVisualizationExample() {
  const [selectedDataset, setSelectedDataset] = useState<'low' | 'high'>('low');

  const currentResults = selectedDataset === 'low'
    ? sampleMetaAnalysisResults
    : sampleHighHeterogeneityResults;

  return (
    <>
      <Head>
        <title>Meta-Analysis Visualization Example</title>
        <meta
          name="description"
          content="Complete example of meta-analysis visualization components"
        />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Meta-Analysis Visualization Example
                </h1>
                <p className="mt-2 text-gray-600">
                  Comprehensive visualization of meta-analysis results using React components
                </p>
              </div>

              {/* Dataset selector */}
              <div className="flex items-center gap-3">
                <label className="text-sm font-medium text-gray-700">
                  Sample Dataset:
                </label>
                <select
                  value={selectedDataset}
                  onChange={(e) => setSelectedDataset(e.target.value as 'low' | 'high')}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">Low Heterogeneity</option>
                  <option value="high">High Heterogeneity</option>
                </select>
              </div>
            </div>
          </div>
        </header>

        {/* Main content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="space-y-8">
            {/* Overview Section */}
            <section>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                <h2 className="text-xl font-semibold text-blue-900 mb-3">
                  Dataset Overview
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <div className="text-blue-700 font-medium">Studies</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {currentResults.studies.length}
                    </div>
                  </div>
                  <div>
                    <div className="text-blue-700 font-medium">Effect Measure</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {currentResults.effectMeasure}
                    </div>
                  </div>
                  <div>
                    <div className="text-blue-700 font-medium">Model</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {currentResults.model === 'random' ? 'Random' : 'Fixed'} Effects
                    </div>
                  </div>
                  <div>
                    <div className="text-blue-700 font-medium">I² Statistic</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {currentResults.heterogeneity.I2.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Statistics Panel */}
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Statistical Summary
              </h2>
              <StatisticsPanel
                results={currentResults}
                showSubgroups={true}
                showSensitivity={true}
              />
            </section>

            {/* Forest Plot */}
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Forest Plot
              </h2>
              <ForestPlot
                results={currentResults}
                title={`Forest Plot - ${currentResults.effectMeasure} with 95% CI`}
                showWeights={true}
                showHeterogeneity={true}
                height={600}
              />
            </section>

            {/* Funnel Plot */}
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Publication Bias Assessment
              </h2>
              <FunnelPlot
                studies={currentResults.studies}
                overallEffect={currentResults.overallEffect}
                publicationBias={currentResults.publicationBias}
                showEggersLine={true}
                showContours={true}
                height={500}
              />
            </section>

            {/* Study Characteristics Table */}
            <section>
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                Study Characteristics
              </h2>
              <StudyCharacteristicsTable
                studies={currentResults.studies}
                effectMeasure={currentResults.effectMeasure}
                showQualityScores={true}
                sortable={true}
                filterable={true}
              />
            </section>

            {/* PRISMA Flow Diagram (only for low heterogeneity dataset) */}
            {selectedDataset === 'low' && (
              <section>
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">
                  PRISMA Flow Diagram
                </h2>
                <PRISMAFlow
                  data={samplePRISMAFlowData}
                  interactive={true}
                  showAnimations={true}
                />
              </section>
            )}

            {/* Component Usage Guide */}
            <section className="bg-white border border-gray-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Component Usage Guide
              </h2>

              <div className="space-y-4 text-sm">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">ForestPlot</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    <code>{`<ForestPlot
  results={metaAnalysisResults}
  title="Forest Plot - OR with 95% CI"
  showWeights={true}
  showHeterogeneity={true}
  height={600}
/>`}</code>
                  </pre>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">FunnelPlot</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    <code>{`<FunnelPlot
  studies={studies}
  overallEffect={overallEffect}
  publicationBias={publicationBias}
  showEggersLine={true}
  showContours={true}
  height={500}
/>`}</code>
                  </pre>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">PRISMAFlow</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    <code>{`<PRISMAFlow
  data={prismaFlowData}
  interactive={true}
  showAnimations={true}
/>`}</code>
                  </pre>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">StatisticsPanel</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    <code>{`<StatisticsPanel
  results={metaAnalysisResults}
  showSubgroups={true}
  showSensitivity={true}
/>`}</code>
                  </pre>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">StudyCharacteristicsTable</h3>
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    <code>{`<StudyCharacteristicsTable
  studies={studies}
  effectMeasure="OR"
  showQualityScores={true}
  sortable={true}
  filterable={true}
/>`}</code>
                  </pre>
                </div>
              </div>
            </section>

            {/* Features */}
            <section className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Key Features
              </h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Forest Plot</h3>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• Effect sizes with confidence intervals</li>
                    <li>• Individual study weights visualization</li>
                    <li>• Pooled effect size (diamond)</li>
                    <li>• Heterogeneity statistics display</li>
                    <li>• Support for multiple effect measures</li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Funnel Plot</h3>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• Publication bias assessment</li>
                    <li>• Interactive study hover tooltips</li>
                    <li>• Egger's regression line</li>
                    <li>• 95% CI funnel contours</li>
                    <li>• Trim and fill results</li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">PRISMA Flow</h3>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• PRISMA 2020 compliant diagram</li>
                    <li>• Interactive box tooltips</li>
                    <li>• Animated transitions</li>
                    <li>• Exclusion reasons breakdown</li>
                    <li>• Summary statistics</li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Statistics Panel</h3>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• Comprehensive statistics display</li>
                    <li>• Collapsible sections</li>
                    <li>• Subgroup analysis results</li>
                    <li>• Sensitivity analysis results</li>
                    <li>• Contextual interpretations</li>
                  </ul>
                </div>

                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Study Table</h3>
                  <ul className="space-y-1 text-sm text-gray-700">
                    <li>• Sortable columns</li>
                    <li>• Searchable and filterable</li>
                    <li>• Quality score visualization</li>
                    <li>• CSV export functionality</li>
                    <li>• Summary statistics</li>
                  </ul>
                </div>
              </div>
            </section>
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-sm text-gray-600 text-center">
              Meta-Analysis Visualization Components - Built with React, TypeScript, and Tailwind CSS
            </p>
          </div>
        </footer>
      </div>
    </>
  );
}
