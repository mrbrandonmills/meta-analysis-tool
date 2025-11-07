import React, { useMemo, useState } from 'react';
import { FunnelPlotProps } from '@/types/meta-analysis';

/**
 * FunnelPlot Component
 *
 * Displays a funnel plot to assess publication bias by plotting
 * effect size against standard error for each study.
 */
export const FunnelPlot: React.FC<FunnelPlotProps> = ({
  studies,
  overallEffect,
  publicationBias,
  showEggersLine = true,
  showContours = true,
  height = 500,
  className = '',
}) => {
  const [hoveredStudy, setHoveredStudy] = useState<string | null>(null);

  // Calculate plot dimensions and scales
  const plotData = useMemo(() => {
    const effectSizes = studies.map(s => s.effectSize);
    const standardErrors = studies.map(s => s.standardError);

    const minEffect = Math.min(...effectSizes, overallEffect.effectSize);
    const maxEffect = Math.max(...effectSizes, overallEffect.effectSize);
    const maxSE = Math.max(...standardErrors);

    const effectRange = maxEffect - minEffect;
    const effectPadding = effectRange * 0.2;

    return {
      minEffect: minEffect - effectPadding,
      maxEffect: maxEffect + effectPadding,
      maxSE: maxSE * 1.1,
      centerEffect: overallEffect.effectSize,
    };
  }, [studies, overallEffect]);

  // Egger's regression line calculation (simplified)
  const eggersLine = useMemo(() => {
    if (!showEggersLine || !publicationBias?.eggersTest) return null;

    // Simple linear regression through the origin adjusted by intercept
    const intercept = publicationBias.eggersTest.intercept;

    return {
      getY: (se: number) => plotData.centerEffect + (intercept * se),
      intercept,
    };
  }, [showEggersLine, publicationBias, plotData.centerEffect]);

  const plotWidth = 600;
  const plotHeight = height - 100;
  const leftMargin = 80;
  const rightMargin = 40;
  const topMargin = 40;
  const bottomMargin = 60;

  const effectWidth = plotWidth - leftMargin - rightMargin;
  const seHeight = plotHeight - topMargin - bottomMargin;

  // Convert effect size to x coordinate
  const effectToX = (effect: number): number => {
    return (
      leftMargin +
      ((effect - plotData.minEffect) / (plotData.maxEffect - plotData.minEffect)) *
        effectWidth
    );
  };

  // Convert standard error to y coordinate (inverted - smaller SE at top)
  const seToY = (se: number): number => {
    return topMargin + ((plotData.maxSE - se) / plotData.maxSE) * seHeight;
  };

  // Calculate center line x position
  const centerX = effectToX(plotData.centerEffect);

  // Generate contour lines for 95% CI funnel
  const contourPoints = useMemo(() => {
    if (!showContours) return [];

    const points: Array<{ x: number; y: number; label: string }> = [];
    const steps = 20;

    for (let i = 0; i <= steps; i++) {
      const se = (plotData.maxSE / steps) * i;
      const y = seToY(se);

      // 95% CI bounds (±1.96 * SE)
      const lowerBound = plotData.centerEffect - 1.96 * se;
      const upperBound = plotData.centerEffect + 1.96 * se;

      points.push(
        { x: effectToX(lowerBound), y, label: 'lower' },
        { x: effectToX(upperBound), y, label: 'upper' }
      );
    }

    return points;
  }, [showContours, plotData, effectToX, seToY]);

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Funnel Plot</h3>
        {publicationBias?.eggersTest && (
          <div className="text-sm text-gray-600">
            Egger's test: p = {publicationBias.eggersTest.pValue < 0.001
              ? '<0.001'
              : publicationBias.eggersTest.pValue.toFixed(3)}
            {publicationBias.eggersTest.pValue < 0.05 && (
              <span className="ml-2 text-amber-600 font-medium">
                (Possible publication bias)
              </span>
            )}
          </div>
        )}
      </div>

      <svg width={plotWidth} height={height} className="font-sans">
        {/* Funnel contours (95% CI) */}
        {showContours && contourPoints.length > 0 && (
          <g>
            {/* Left contour line */}
            <polyline
              points={contourPoints
                .filter(p => p.label === 'lower')
                .map(p => `${p.x},${p.y}`)
                .join(' ')}
              fill="none"
              stroke="#cbd5e0"
              strokeWidth={1}
              strokeDasharray="4 2"
            />

            {/* Right contour line */}
            <polyline
              points={contourPoints
                .filter(p => p.label === 'upper')
                .map(p => `${p.x},${p.y}`)
                .join(' ')}
              fill="none"
              stroke="#cbd5e0"
              strokeWidth={1}
              strokeDasharray="4 2"
            />

            {/* Shaded funnel area */}
            <polygon
              points={[
                ...contourPoints.filter(p => p.label === 'lower').map(p => `${p.x},${p.y}`),
                ...contourPoints.filter(p => p.label === 'upper').reverse().map(p => `${p.x},${p.y}`),
              ].join(' ')}
              fill="#edf2f7"
              opacity={0.3}
            />
          </g>
        )}

        {/* Center line (overall effect) */}
        <line
          x1={centerX}
          y1={topMargin}
          x2={centerX}
          y2={topMargin + seHeight}
          stroke="#4299e1"
          strokeWidth={2}
        />

        {/* Egger's regression line */}
        {eggersLine && (
          <line
            x1={effectToX(eggersLine.getY(0))}
            y1={seToY(0)}
            x2={effectToX(eggersLine.getY(plotData.maxSE))}
            y2={seToY(plotData.maxSE)}
            stroke="#f56565"
            strokeWidth={2}
            strokeDasharray="6 3"
          />
        )}

        {/* Data points */}
        {studies.map((study) => {
          const x = effectToX(study.effectSize);
          const y = seToY(study.standardError);
          const isHovered = hoveredStudy === study.id;

          return (
            <g
              key={study.id}
              onMouseEnter={() => setHoveredStudy(study.id)}
              onMouseLeave={() => setHoveredStudy(null)}
              style={{ cursor: 'pointer' }}
            >
              <circle
                cx={x}
                cy={y}
                r={isHovered ? 6 : 4}
                fill={isHovered ? '#2b6cb0' : '#4299e1'}
                stroke="#fff"
                strokeWidth={1.5}
                opacity={isHovered ? 1 : 0.8}
              />

              {/* Tooltip on hover */}
              {isHovered && (
                <g>
                  <rect
                    x={x + 10}
                    y={y - 35}
                    width={180}
                    height={50}
                    fill="#2d3748"
                    stroke="#4a5568"
                    strokeWidth={1}
                    rx={4}
                    opacity={0.95}
                  />
                  <text
                    x={x + 20}
                    y={y - 20}
                    fill="#fff"
                    className="text-xs font-medium"
                  >
                    {study.author} ({study.year})
                  </text>
                  <text
                    x={x + 20}
                    y={y - 5}
                    fill="#fff"
                    className="text-xs"
                  >
                    Effect: {study.effectSize.toFixed(3)}
                  </text>
                  <text
                    x={x + 20}
                    y={y + 10}
                    fill="#fff"
                    className="text-xs"
                  >
                    SE: {study.standardError.toFixed(3)}
                  </text>
                </g>
              )}
            </g>
          );
        })}

        {/* Y-axis (Standard Error) */}
        <line
          x1={leftMargin}
          y1={topMargin}
          x2={leftMargin}
          y2={topMargin + seHeight}
          stroke="#2d3748"
          strokeWidth={1}
        />

        {/* Y-axis ticks and labels */}
        {Array.from({ length: 6 }, (_, i) => {
          const se = (plotData.maxSE / 5) * i;
          const y = seToY(se);
          return (
            <g key={i}>
              <line
                x1={leftMargin - 5}
                y1={y}
                x2={leftMargin}
                y2={y}
                stroke="#2d3748"
                strokeWidth={1}
              />
              <text
                x={leftMargin - 10}
                y={y + 4}
                textAnchor="end"
                className="text-xs"
              >
                {se.toFixed(2)}
              </text>
            </g>
          );
        })}

        {/* Y-axis label */}
        <text
          x={-plotHeight / 2}
          y={20}
          textAnchor="middle"
          transform="rotate(-90)"
          className="text-sm font-medium"
        >
          Standard Error
        </text>

        {/* X-axis */}
        <line
          x1={leftMargin}
          y1={topMargin + seHeight}
          x2={leftMargin + effectWidth}
          y2={topMargin + seHeight}
          stroke="#2d3748"
          strokeWidth={1}
        />

        {/* X-axis ticks and labels */}
        {Array.from({ length: 7 }, (_, i) => {
          const effect = plotData.minEffect + ((plotData.maxEffect - plotData.minEffect) / 6) * i;
          const x = effectToX(effect);
          return (
            <g key={i}>
              <line
                x1={x}
                y1={topMargin + seHeight}
                x2={x}
                y2={topMargin + seHeight + 5}
                stroke="#2d3748"
                strokeWidth={1}
              />
              <text
                x={x}
                y={topMargin + seHeight + 20}
                textAnchor="middle"
                className="text-xs"
              >
                {effect.toFixed(2)}
              </text>
            </g>
          );
        })}

        {/* X-axis label */}
        <text
          x={leftMargin + effectWidth / 2}
          y={height - 10}
          textAnchor="middle"
          className="text-sm font-medium"
        >
          Effect Size
        </text>
      </svg>

      {/* Legend and interpretation */}
      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-6 text-xs text-gray-600">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span>Individual studies</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-0.5 bg-blue-500"></div>
            <span>Overall effect</span>
          </div>
          {showContours && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-0.5 border-t border-dashed border-gray-400"></div>
              <span>95% CI funnel</span>
            </div>
          )}
          {eggersLine && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-0.5 bg-red-500 border-dashed"></div>
              <span>Egger's line</span>
            </div>
          )}
        </div>

        {publicationBias?.trimAndFill && (
          <div className="text-xs text-gray-700 bg-amber-50 border border-amber-200 rounded p-3">
            <span className="font-medium">Trim and Fill:</span> {publicationBias.trimAndFill.missingStudies} potentially missing studies detected.
            Adjusted effect size: {publicationBias.trimAndFill.adjustedEffectSize.toFixed(3)}
          </div>
        )}

        <div className="text-xs text-gray-600 italic">
          A symmetric funnel-shaped distribution suggests no publication bias.
          Asymmetry may indicate small-study effects or publication bias.
        </div>
      </div>
    </div>
  );
};

export default FunnelPlot;
