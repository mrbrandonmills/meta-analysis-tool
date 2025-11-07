import React, { useMemo } from 'react';
import { ForestPlotProps, Study } from '@/types/meta-analysis';

/**
 * ForestPlot Component
 *
 * Displays a forest plot showing effect sizes with confidence intervals
 * for individual studies and the pooled effect size.
 */
export const ForestPlot: React.FC<ForestPlotProps> = ({
  results,
  title = 'Forest Plot',
  showWeights = true,
  showHeterogeneity = true,
  height = 600,
  className = '',
}) => {
  const { studies, overallEffect, heterogeneity, effectMeasure } = results;

  // Calculate plot dimensions and scales
  const plotData = useMemo(() => {
    // Find min and max effect sizes for scaling
    const allEffects = [
      ...studies.map(s => s.lowerCI),
      ...studies.map(s => s.upperCI),
      overallEffect.lowerCI,
      overallEffect.upperCI,
    ];

    const minEffect = Math.min(...allEffects);
    const maxEffect = Math.max(...allEffects);
    const range = maxEffect - minEffect;
    const padding = range * 0.1;

    return {
      minValue: minEffect - padding,
      maxValue: maxEffect + padding,
      nullValue: effectMeasure === 'MD' || effectMeasure === 'SMD' ? 0 : 1,
    };
  }, [studies, overallEffect, effectMeasure]);

  const plotWidth = 700;
  const studyHeight = 30;
  const headerHeight = 60;
  const footerHeight = showHeterogeneity ? 100 : 60;
  const leftMargin = 250;
  const rightMargin = 150;
  const effectWidth = plotWidth - leftMargin - rightMargin;

  // Convert effect size to x coordinate
  const effectToX = (value: number): number => {
    const { minValue, maxValue } = plotData;
    return leftMargin + ((value - minValue) / (maxValue - minValue)) * effectWidth;
  };

  // Calculate null line position
  const nullLineX = effectToX(plotData.nullValue);

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <h3 className="text-lg font-semibold mb-4">{title}</h3>

      <svg
        width={plotWidth}
        height={height}
        className="font-sans"
      >
        {/* Header */}
        <text x={10} y={30} className="text-sm font-semibold">
          Study
        </text>
        <text x={leftMargin - 80} y={30} className="text-sm font-semibold text-right">
          Year
        </text>
        {showWeights && (
          <text x={plotWidth - 100} y={30} className="text-sm font-semibold">
            Weight %
          </text>
        )}
        <text
          x={leftMargin + effectWidth / 2}
          y={30}
          textAnchor="middle"
          className="text-sm font-semibold"
        >
          {effectMeasure} [95% CI]
        </text>

        {/* Null effect line */}
        <line
          x1={nullLineX}
          y1={headerHeight}
          x2={nullLineX}
          y2={headerHeight + studies.length * studyHeight + 20}
          stroke="#cbd5e0"
          strokeWidth={2}
          strokeDasharray="4 4"
        />

        {/* Individual studies */}
        {studies.map((study, index) => {
          const yPos = headerHeight + index * studyHeight + 15;
          const x1 = effectToX(study.lowerCI);
          const x2 = effectToX(study.upperCI);
          const xCenter = effectToX(study.effectSize);
          const boxSize = Math.sqrt(study.weight) * 0.8;

          return (
            <g key={study.id}>
              {/* CI line */}
              <line
                x1={x1}
                y1={yPos}
                x2={x2}
                y2={yPos}
                stroke="#4a5568"
                strokeWidth={1.5}
              />

              {/* Effect size square */}
              <rect
                x={xCenter - boxSize / 2}
                y={yPos - boxSize / 2}
                width={boxSize}
                height={boxSize}
                fill="#4299e1"
                stroke="#2b6cb0"
                strokeWidth={1}
              />

              {/* Study label */}
              <text x={10} y={yPos + 4} className="text-xs">
                {study.author}
              </text>

              {/* Year */}
              <text x={leftMargin - 85} y={yPos + 4} className="text-xs">
                {study.year}
              </text>

              {/* Weight */}
              {showWeights && (
                <text x={plotWidth - 100} y={yPos + 4} className="text-xs">
                  {study.weight.toFixed(1)}
                </text>
              )}

              {/* Effect size and CI */}
              <text
                x={plotWidth - 20}
                y={yPos + 4}
                textAnchor="end"
                className="text-xs"
              >
                {study.effectSize.toFixed(2)} [{study.lowerCI.toFixed(2)}, {study.upperCI.toFixed(2)}]
              </text>
            </g>
          );
        })}

        {/* Separator line */}
        <line
          x1={10}
          y1={headerHeight + studies.length * studyHeight + 30}
          x2={plotWidth - 10}
          y2={headerHeight + studies.length * studyHeight + 30}
          stroke="#2d3748"
          strokeWidth={1}
        />

        {/* Overall effect (diamond) */}
        {(() => {
          const yPos = headerHeight + studies.length * studyHeight + 50;
          const xCenter = effectToX(overallEffect.effectSize);
          const xLeft = effectToX(overallEffect.lowerCI);
          const xRight = effectToX(overallEffect.upperCI);
          const diamondHeight = 12;

          return (
            <g>
              {/* Diamond shape for pooled effect */}
              <polygon
                points={`
                  ${xCenter},${yPos - diamondHeight}
                  ${xRight},${yPos}
                  ${xCenter},${yPos + diamondHeight}
                  ${xLeft},${yPos}
                `}
                fill="#38a169"
                stroke="#2f855a"
                strokeWidth={2}
              />

              {/* Label */}
              <text
                x={10}
                y={yPos + 4}
                className="text-sm font-semibold"
              >
                Overall Effect ({results.model === 'random' ? 'Random' : 'Fixed'})
              </text>

              {/* Effect size and CI */}
              <text
                x={plotWidth - 20}
                y={yPos + 4}
                textAnchor="end"
                className="text-sm font-semibold"
              >
                {overallEffect.effectSize.toFixed(2)} [{overallEffect.lowerCI.toFixed(2)}, {overallEffect.upperCI.toFixed(2)}]
              </text>
            </g>
          );
        })()}

        {/* X-axis */}
        <line
          x1={leftMargin}
          y1={height - footerHeight + 10}
          x2={leftMargin + effectWidth}
          y2={height - footerHeight + 10}
          stroke="#2d3748"
          strokeWidth={1}
        />

        {/* X-axis labels */}
        {(() => {
          const ticks = 5;
          const step = (plotData.maxValue - plotData.minValue) / (ticks - 1);
          return Array.from({ length: ticks }, (_, i) => {
            const value = plotData.minValue + step * i;
            const x = effectToX(value);
            return (
              <g key={i}>
                <line
                  x1={x}
                  y1={height - footerHeight + 10}
                  x2={x}
                  y2={height - footerHeight + 15}
                  stroke="#2d3748"
                  strokeWidth={1}
                />
                <text
                  x={x}
                  y={height - footerHeight + 30}
                  textAnchor="middle"
                  className="text-xs"
                >
                  {value.toFixed(2)}
                </text>
              </g>
            );
          });
        })()}

        {/* Heterogeneity statistics */}
        {showHeterogeneity && (
          <g>
            <text x={10} y={height - 30} className="text-xs">
              Heterogeneity: I² = {heterogeneity.I2.toFixed(1)}%, τ² = {heterogeneity.tau2.toFixed(3)},
              χ² = {heterogeneity.Q.toFixed(2)} (df = {heterogeneity.df}), p = {heterogeneity.pValue < 0.001 ? '<0.001' : heterogeneity.pValue.toFixed(3)}
            </text>
            <text x={10} y={height - 10} className="text-xs">
              Overall effect: Z = {overallEffect.zValue.toFixed(2)}, p = {overallEffect.pValue < 0.001 ? '<0.001' : overallEffect.pValue.toFixed(3)}
            </text>
          </g>
        )}
      </svg>

      {/* Legend */}
      <div className="mt-4 flex items-center gap-6 text-xs text-gray-600">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-blue-500 border border-blue-700"></div>
          <span>Individual studies (size proportional to weight)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-600 border border-green-800 transform rotate-45"></div>
          <span>Pooled effect size</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-0.5 border-t-2 border-dashed border-gray-400"></div>
          <span>No effect line ({plotData.nullValue})</span>
        </div>
      </div>
    </div>
  );
};

export default ForestPlot;
