import React, { useState } from 'react';
import { StatisticsPanelProps } from '@/types/meta-analysis';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';

/**
 * StatisticsPanel Component
 *
 * Displays comprehensive meta-analysis statistics including overall effect,
 * heterogeneity, publication bias, subgroup and sensitivity analyses.
 */
export const StatisticsPanel: React.FC<StatisticsPanelProps> = ({
  results,
  showSubgroups = true,
  showSensitivity = true,
  className = '',
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['overall', 'heterogeneity'])
  );

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const { overallEffect, heterogeneity, publicationBias, subgroupAnalyses, sensitivityAnalyses, effectMeasure, model } = results;

  // Stat display component
  const StatRow: React.FC<{
    label: string;
    value: string | number;
    tooltip?: string;
    highlight?: boolean;
  }> = ({ label, value, tooltip, highlight = false }) => (
    <div className={`flex justify-between items-center py-2 px-3 rounded ${highlight ? 'bg-blue-50' : ''}`}>
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-700">{label}</span>
        {tooltip && (
          <div className="group relative">
            <Info className="w-3 h-3 text-gray-400 cursor-help" />
            <div className="absolute hidden group-hover:block z-10 w-64 p-2 text-xs bg-gray-800 text-white rounded shadow-lg bottom-full left-0 mb-2">
              {tooltip}
            </div>
          </div>
        )}
      </div>
      <span className={`text-sm font-medium ${highlight ? 'text-blue-700' : 'text-gray-900'}`}>
        {value}
      </span>
    </div>
  );

  // Section header component
  const SectionHeader: React.FC<{
    id: string;
    title: string;
    badge?: string;
  }> = ({ id, title, badge }) => {
    const isExpanded = expandedSections.has(id);
    return (
      <button
        onClick={() => toggleSection(id)}
        className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <div className="flex items-center gap-3">
          <h4 className="text-sm font-semibold text-gray-900">{title}</h4>
          {badge && (
            <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 text-blue-700 rounded">
              {badge}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        )}
      </button>
    );
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border p-6 space-y-4 ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold">Meta-Analysis Statistics</h3>
        <div className="text-sm text-gray-600">
          {model === 'random' ? 'Random Effects' : 'Fixed Effects'} Model
        </div>
      </div>

      {/* Overall Effect */}
      <div>
        <SectionHeader
          id="overall"
          title="Overall Effect"
          badge={`${results.studies.length} studies`}
        />
        {expandedSections.has('overall') && (
          <div className="mt-2 space-y-1 border border-gray-200 rounded-lg p-2">
            <StatRow
              label={`Pooled ${effectMeasure}`}
              value={`${overallEffect.effectSize.toFixed(3)} [${overallEffect.lowerCI.toFixed(3)}, ${overallEffect.upperCI.toFixed(3)}]`}
              highlight
              tooltip="Pooled effect size with 95% confidence interval"
            />
            <StatRow
              label="Z-value"
              value={overallEffect.zValue.toFixed(3)}
              tooltip="Test statistic for overall effect"
            />
            <StatRow
              label="P-value"
              value={overallEffect.pValue < 0.001 ? '<0.001' : overallEffect.pValue.toFixed(4)}
              tooltip="Statistical significance of overall effect"
            />
            <StatRow
              label="Standard Error"
              value={overallEffect.standardError.toFixed(4)}
            />
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className={`text-sm px-3 py-2 rounded ${
                overallEffect.pValue < 0.05
                  ? 'bg-green-50 text-green-800'
                  : 'bg-gray-50 text-gray-700'
              }`}>
                {overallEffect.pValue < 0.05 ? (
                  <>
                    <span className="font-semibold">Significant effect detected.</span>
                    {effectMeasure !== 'MD' && effectMeasure !== 'SMD' && (
                      <span className="ml-1">
                        {overallEffect.lowerCI > 1
                          ? 'Increased risk/odds'
                          : overallEffect.upperCI < 1
                          ? 'Decreased risk/odds'
                          : 'Effect includes null value'}
                      </span>
                    )}
                  </>
                ) : (
                  <span className="font-semibold">No significant effect detected.</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Heterogeneity */}
      <div>
        <SectionHeader id="heterogeneity" title="Heterogeneity Assessment" />
        {expandedSections.has('heterogeneity') && (
          <div className="mt-2 space-y-1 border border-gray-200 rounded-lg p-2">
            <StatRow
              label="I² statistic"
              value={`${heterogeneity.I2.toFixed(1)}%`}
              tooltip="Percentage of variation across studies due to heterogeneity rather than chance"
              highlight
            />
            <StatRow
              label="τ² (Tau-squared)"
              value={heterogeneity.tau2.toFixed(4)}
              tooltip="Estimate of between-study variance"
            />
            <StatRow
              label="Q statistic"
              value={heterogeneity.Q.toFixed(2)}
              tooltip="Cochran's Q test statistic"
            />
            <StatRow
              label="Degrees of freedom"
              value={heterogeneity.df}
            />
            <StatRow
              label="P-value (Q)"
              value={heterogeneity.pValue < 0.001 ? '<0.001' : heterogeneity.pValue.toFixed(4)}
              tooltip="P-value for heterogeneity test"
            />
            {heterogeneity.H2 !== undefined && (
              <StatRow
                label="H² statistic"
                value={heterogeneity.H2.toFixed(2)}
                tooltip="Relative excess in Q over its degrees of freedom"
              />
            )}
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className={`text-sm px-3 py-2 rounded ${
                heterogeneity.I2 < 25
                  ? 'bg-green-50 text-green-800'
                  : heterogeneity.I2 < 50
                  ? 'bg-yellow-50 text-yellow-800'
                  : heterogeneity.I2 < 75
                  ? 'bg-orange-50 text-orange-800'
                  : 'bg-red-50 text-red-800'
              }`}>
                <span className="font-semibold">
                  {heterogeneity.I2 < 25
                    ? 'Low heterogeneity'
                    : heterogeneity.I2 < 50
                    ? 'Moderate heterogeneity'
                    : heterogeneity.I2 < 75
                    ? 'Substantial heterogeneity'
                    : 'Considerable heterogeneity'}
                </span>
                {heterogeneity.I2 >= 50 && (
                  <span className="ml-1">- Consider subgroup analysis or random effects model</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Publication Bias */}
      {publicationBias && (
        <div>
          <SectionHeader id="publication" title="Publication Bias" />
          {expandedSections.has('publication') && (
            <div className="mt-2 space-y-1 border border-gray-200 rounded-lg p-2">
              {publicationBias.eggersTest && (
                <>
                  <div className="text-xs font-semibold text-gray-700 mb-2 px-3 pt-2">
                    Egger's Regression Test
                  </div>
                  <StatRow
                    label="Intercept"
                    value={publicationBias.eggersTest.intercept.toFixed(4)}
                  />
                  <StatRow
                    label="P-value"
                    value={publicationBias.eggersTest.pValue < 0.001 ? '<0.001' : publicationBias.eggersTest.pValue.toFixed(4)}
                    highlight={publicationBias.eggersTest.pValue < 0.05}
                  />
                </>
              )}

              {publicationBias.beggTest && (
                <>
                  <div className="text-xs font-semibold text-gray-700 mb-2 px-3 pt-3 mt-2 border-t">
                    Begg's Rank Correlation Test
                  </div>
                  <StatRow
                    label="Kendall's τ"
                    value={publicationBias.beggTest.tau.toFixed(4)}
                  />
                  <StatRow
                    label="P-value"
                    value={publicationBias.beggTest.pValue < 0.001 ? '<0.001' : publicationBias.beggTest.pValue.toFixed(4)}
                    highlight={publicationBias.beggTest.pValue < 0.05}
                  />
                </>
              )}

              {publicationBias.trimAndFill && (
                <>
                  <div className="text-xs font-semibold text-gray-700 mb-2 px-3 pt-3 mt-2 border-t">
                    Trim and Fill Analysis
                  </div>
                  <StatRow
                    label="Missing studies"
                    value={publicationBias.trimAndFill.missingStudies}
                  />
                  <StatRow
                    label="Adjusted effect size"
                    value={publicationBias.trimAndFill.adjustedEffectSize.toFixed(4)}
                  />
                </>
              )}

              <div className="mt-3 pt-3 border-t border-gray-200">
                <div className={`text-sm px-3 py-2 rounded ${
                  (publicationBias.eggersTest?.pValue ?? 1) < 0.05 ||
                  (publicationBias.beggTest?.pValue ?? 1) < 0.05
                    ? 'bg-amber-50 text-amber-800'
                    : 'bg-green-50 text-green-800'
                }`}>
                  {(publicationBias.eggersTest?.pValue ?? 1) < 0.05 ||
                  (publicationBias.beggTest?.pValue ?? 1) < 0.05 ? (
                    <span className="font-semibold">
                      Evidence of publication bias detected - interpret results with caution
                    </span>
                  ) : (
                    <span className="font-semibold">No significant publication bias detected</span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Subgroup Analyses */}
      {showSubgroups && subgroupAnalyses && subgroupAnalyses.length > 0 && (
        <div>
          <SectionHeader
            id="subgroups"
            title="Subgroup Analyses"
            badge={`${subgroupAnalyses.length} subgroups`}
          />
          {expandedSections.has('subgroups') && (
            <div className="mt-2 space-y-3 border border-gray-200 rounded-lg p-2">
              {subgroupAnalyses.map((subgroup, index) => (
                <div key={index} className="border-b border-gray-100 pb-3 last:border-b-0">
                  <div className="text-sm font-semibold text-gray-800 mb-2">
                    {subgroup.subgroupName}
                    <span className="ml-2 text-xs font-normal text-gray-500">
                      ({subgroup.studies.length} studies)
                    </span>
                  </div>
                  <div className="space-y-1 ml-3">
                    <StatRow
                      label="Effect Size"
                      value={`${subgroup.effectSize.toFixed(3)} [${subgroup.lowerCI.toFixed(3)}, ${subgroup.upperCI.toFixed(3)}]`}
                    />
                    <StatRow
                      label="P-value"
                      value={subgroup.pValue < 0.001 ? '<0.001' : subgroup.pValue.toFixed(4)}
                    />
                    <StatRow
                      label="I²"
                      value={`${subgroup.heterogeneity.I2.toFixed(1)}%`}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Sensitivity Analyses */}
      {showSensitivity && sensitivityAnalyses && sensitivityAnalyses.length > 0 && (
        <div>
          <SectionHeader
            id="sensitivity"
            title="Sensitivity Analyses"
            badge={`${sensitivityAnalyses.length} analyses`}
          />
          {expandedSections.has('sensitivity') && (
            <div className="mt-2 space-y-3 border border-gray-200 rounded-lg p-2">
              {sensitivityAnalyses.map((analysis, index) => (
                <div key={index} className="border-b border-gray-100 pb-3 last:border-b-0">
                  <div className="text-sm font-semibold text-gray-800 mb-1">
                    {analysis.name}
                  </div>
                  <div className="text-xs text-gray-600 mb-2">{analysis.description}</div>
                  <div className="space-y-1 ml-3">
                    <StatRow
                      label="Effect Size"
                      value={`${analysis.effectSize.toFixed(3)} [${analysis.lowerCI.toFixed(3)}, ${analysis.upperCI.toFixed(3)}]`}
                    />
                    {analysis.studiesRemoved && analysis.studiesRemoved.length > 0 && (
                      <div className="text-xs text-gray-600 mt-2">
                        Removed: {analysis.studiesRemoved.join(', ')}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default StatisticsPanel;
