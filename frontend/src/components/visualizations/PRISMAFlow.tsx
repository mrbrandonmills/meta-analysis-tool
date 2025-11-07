import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { PRISMAFlowProps } from '@/types/meta-analysis';

/**
 * PRISMAFlow Component
 *
 * Displays a PRISMA flow diagram showing the systematic review
 * and study selection process.
 */
export const PRISMAFlow: React.FC<PRISMAFlowProps> = ({
  data,
  interactive = true,
  showAnimations = true,
  className = '',
}) => {
  const [hoveredBox, setHoveredBox] = useState<string | null>(null);

  const { identification, screening, eligibility, included } = data;

  // Box component
  const Box: React.FC<{
    id: string;
    title: string;
    value: number;
    subtitle?: string;
    color: 'blue' | 'gray' | 'green' | 'red';
    details?: Record<string, number>;
  }> = ({ id, title, value, subtitle, color, details }) => {
    const isHovered = interactive && hoveredBox === id;

    const colorClasses = {
      blue: 'bg-blue-50 border-blue-400 text-blue-900',
      gray: 'bg-gray-50 border-gray-400 text-gray-900',
      green: 'bg-green-50 border-green-400 text-green-900',
      red: 'bg-red-50 border-red-400 text-red-900',
    };

    const BoxWrapper = showAnimations ? motion.div : 'div';
    const animationProps = showAnimations
      ? {
          initial: { opacity: 0, y: -20 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.5, delay: parseInt(id) * 0.1 },
        }
      : {};

    return (
      <BoxWrapper
        {...animationProps}
        className={`
          relative border-2 rounded-lg p-4 min-w-[280px]
          ${colorClasses[color]}
          ${interactive ? 'cursor-pointer hover:shadow-lg transition-shadow' : ''}
          ${isHovered ? 'shadow-lg ring-2 ring-offset-2 ring-blue-500' : ''}
        `}
        onMouseEnter={() => interactive && setHoveredBox(id)}
        onMouseLeave={() => interactive && setHoveredBox(null)}
      >
        <div className="text-sm font-medium mb-2">{title}</div>
        <div className="text-3xl font-bold mb-1">{value.toLocaleString()}</div>
        {subtitle && <div className="text-xs text-gray-600">{subtitle}</div>}

        {/* Details tooltip */}
        {isHovered && details && Object.keys(details).length > 0 && (
          <div className="absolute z-10 top-full mt-2 left-0 bg-white border-2 border-gray-300 rounded-lg shadow-xl p-3 min-w-[250px]">
            <div className="text-xs font-semibold mb-2">Breakdown:</div>
            {Object.entries(details).map(([key, val]) => (
              <div key={key} className="text-xs flex justify-between py-1">
                <span className="text-gray-700">{key}:</span>
                <span className="font-medium">{val.toLocaleString()}</span>
              </div>
            ))}
          </div>
        )}
      </BoxWrapper>
    );
  };

  // Arrow component
  const Arrow: React.FC<{
    vertical?: boolean;
    label?: string;
    dashed?: boolean;
  }> = ({ vertical = true, label, dashed = false }) => {
    const ArrowWrapper = showAnimations ? motion.div : 'div';
    const animationProps = showAnimations
      ? {
          initial: { opacity: 0 },
          animate: { opacity: 1 },
          transition: { duration: 0.3, delay: 0.5 },
        }
      : {};

    return (
      <ArrowWrapper
        {...animationProps}
        className={`flex ${vertical ? 'flex-col' : 'flex-row'} items-center justify-center`}
      >
        {vertical ? (
          <>
            <div
              className={`w-0.5 h-8 ${dashed ? 'border-l-2 border-dashed' : 'bg-gray-400'}`}
            ></div>
            <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-gray-400"></div>
          </>
        ) : (
          <>
            <div
              className={`h-0.5 w-12 ${dashed ? 'border-t-2 border-dashed' : 'bg-gray-400'}`}
            ></div>
            <div className="w-0 h-0 border-t-[6px] border-t-transparent border-b-[6px] border-b-transparent border-l-[8px] border-l-gray-400"></div>
          </>
        )}
        {label && (
          <div className="text-xs text-gray-600 font-medium mt-1 px-2 whitespace-nowrap">
            {label}
          </div>
        )}
      </ArrowWrapper>
    );
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
      <h3 className="text-lg font-semibold mb-6">PRISMA Flow Diagram</h3>

      <div className="flex flex-col items-center space-y-4">
        {/* IDENTIFICATION */}
        <div className="w-full flex flex-col items-center">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-4">
            Identification
          </div>

          <Box
            id="1"
            title="Records identified through database searching"
            value={identification.recordsIdentified}
            color="blue"
            details={{ 'Databases searched': identification.databasesSearched }}
          />

          <Arrow />

          <Box
            id="2"
            title="Records after duplicates removed"
            value={identification.recordsScreened}
            subtitle={`${identification.duplicatesRemoved.toLocaleString()} duplicates removed`}
            color="blue"
          />
        </div>

        <Arrow />

        {/* SCREENING */}
        <div className="w-full flex flex-col items-center">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-4">
            Screening
          </div>

          <div className="flex items-center gap-4">
            <Box
              id="3"
              title="Records screened"
              value={identification.recordsScreened}
              color="blue"
            />

            <Arrow vertical={false} />

            <Box
              id="4"
              title="Records excluded"
              value={screening.recordsExcluded}
              color="red"
              details={screening.exclusionReasons}
            />
          </div>
        </div>

        <Arrow />

        {/* ELIGIBILITY */}
        <div className="w-full flex flex-col items-center">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-4">
            Eligibility
          </div>

          <div className="flex items-center gap-4">
            <Box
              id="5"
              title="Full-text articles assessed for eligibility"
              value={eligibility.fullTextAssessed}
              color="blue"
            />

            <Arrow vertical={false} />

            <Box
              id="6"
              title="Full-text articles excluded"
              value={eligibility.fullTextExcluded}
              color="red"
              details={eligibility.exclusionReasons}
            />
          </div>
        </div>

        <Arrow />

        {/* INCLUDED */}
        <div className="w-full flex flex-col items-center">
          <div className="text-xs font-bold text-gray-500 uppercase tracking-wide mb-4">
            Included
          </div>

          <Box
            id="7"
            title="Studies included in qualitative synthesis"
            value={included.studiesIncluded}
            color="green"
          />

          {included.studiesInMetaAnalysis !== undefined && (
            <>
              <Arrow />
              <Box
                id="8"
                title="Studies included in quantitative synthesis (meta-analysis)"
                value={included.studiesInMetaAnalysis}
                color="green"
              />
            </>
          )}
        </div>
      </div>

      {/* Summary statistics */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="bg-gray-50 rounded p-3">
            <div className="text-gray-600 text-xs mb-1">Initial Records</div>
            <div className="text-xl font-bold text-gray-900">
              {identification.recordsIdentified.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <div className="text-gray-600 text-xs mb-1">Total Excluded</div>
            <div className="text-xl font-bold text-red-600">
              {(screening.recordsExcluded + eligibility.fullTextExcluded).toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <div className="text-gray-600 text-xs mb-1">Final Included</div>
            <div className="text-xl font-bold text-green-600">
              {included.studiesIncluded.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <div className="text-gray-600 text-xs mb-1">Inclusion Rate</div>
            <div className="text-xl font-bold text-blue-600">
              {((included.studiesIncluded / identification.recordsIdentified) * 100).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Footer note */}
      <div className="mt-4 text-xs text-gray-500 italic text-center">
        Flow diagram follows PRISMA 2020 guidelines
        {interactive && ' (hover over boxes for details)'}
      </div>
    </div>
  );
};

export default PRISMAFlow;
