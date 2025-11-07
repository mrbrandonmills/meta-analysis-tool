import React, { useState, useMemo } from 'react';
import { StudyCharacteristicsTableProps, Study } from '@/types/meta-analysis';
import { ArrowUp, ArrowDown, Search, Download } from 'lucide-react';

type SortField = keyof Study;
type SortDirection = 'asc' | 'desc';

/**
 * StudyCharacteristicsTable Component
 *
 * Displays a sortable and filterable table of study characteristics
 * with effect sizes and quality assessment scores.
 */
export const StudyCharacteristicsTable: React.FC<StudyCharacteristicsTableProps> = ({
  studies,
  effectMeasure,
  showQualityScores = true,
  sortable = true,
  filterable = true,
  className = '',
}) => {
  const [sortField, setSortField] = useState<SortField>('year');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [subgroupFilter, setSubgroupFilter] = useState<string>('all');

  // Get unique subgroups
  const subgroups = useMemo(() => {
    const groups = new Set(studies.map(s => s.subgroup).filter(Boolean));
    return Array.from(groups) as string[];
  }, [studies]);

  // Filter and sort studies
  const processedStudies = useMemo(() => {
    let filtered = [...studies];

    // Apply search filter
    if (filterable && searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(
        study =>
          study.author.toLowerCase().includes(term) ||
          study.year.toString().includes(term) ||
          study.studyDesign.toLowerCase().includes(term)
      );
    }

    // Apply subgroup filter
    if (subgroupFilter !== 'all') {
      filtered = filtered.filter(study => study.subgroup === subgroupFilter);
    }

    // Apply sorting
    if (sortable) {
      filtered.sort((a, b) => {
        const aValue = a[sortField];
        const bValue = b[sortField];

        if (typeof aValue === 'string' && typeof bValue === 'string') {
          return sortDirection === 'asc'
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
        }

        if (typeof aValue === 'number' && typeof bValue === 'number') {
          return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
        }

        return 0;
      });
    }

    return filtered;
  }, [studies, searchTerm, subgroupFilter, sortField, sortDirection, sortable, filterable]);

  // Handle sort
  const handleSort = (field: SortField) => {
    if (!sortable) return;

    if (sortField === field) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Export to CSV
  const exportToCSV = () => {
    const headers = [
      'Author',
      'Year',
      'Sample Size',
      'Study Design',
      'Effect Size',
      'Lower CI',
      'Upper CI',
      'SE',
      'Weight',
      ...(showQualityScores ? ['Quality Score'] : []),
      ...(subgroups.length > 0 ? ['Subgroup'] : []),
    ];

    const rows = processedStudies.map(study => [
      study.author,
      study.year,
      study.sampleSize,
      study.studyDesign,
      study.effectSize.toFixed(4),
      study.lowerCI.toFixed(4),
      study.upperCI.toFixed(4),
      study.standardError.toFixed(4),
      study.weight.toFixed(2),
      ...(showQualityScores ? [study.qualityScore ?? 'N/A'] : []),
      ...(subgroups.length > 0 ? [study.subgroup ?? 'N/A'] : []),
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.join(',')),
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'study-characteristics.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Table header component
  const TableHeader: React.FC<{
    field: SortField;
    label: string;
    align?: 'left' | 'right' | 'center';
  }> = ({ field, label, align = 'left' }) => {
    const isSorted = sortField === field;
    const textAlign = align === 'right' ? 'text-right' : align === 'center' ? 'text-center' : 'text-left';

    return (
      <th
        className={`px-4 py-3 text-xs font-semibold text-gray-700 uppercase tracking-wider ${textAlign} ${
          sortable ? 'cursor-pointer hover:bg-gray-100' : ''
        }`}
        onClick={() => handleSort(field)}
      >
        <div className={`flex items-center gap-1 ${align === 'right' ? 'justify-end' : align === 'center' ? 'justify-center' : 'justify-start'}`}>
          {label}
          {sortable && isSorted && (
            <span className="ml-1">
              {sortDirection === 'asc' ? (
                <ArrowUp className="w-3 h-3" />
              ) : (
                <ArrowDown className="w-3 h-3" />
              )}
            </span>
          )}
        </div>
      </th>
    );
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Study Characteristics</h3>
          <button
            onClick={exportToCSV}
            className="flex items-center gap-2 px-3 py-1.5 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </button>
        </div>

        {/* Filters */}
        {filterable && (
          <div className="flex gap-3">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by author, year, or study design..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Subgroup filter */}
            {subgroups.length > 0 && (
              <select
                value={subgroupFilter}
                onChange={(e) => setSubgroupFilter(e.target.value)}
                className="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All subgroups</option>
                {subgroups.map(group => (
                  <option key={group} value={group}>
                    {group}
                  </option>
                ))}
              </select>
            )}
          </div>
        )}

        {/* Results count */}
        <div className="mt-2 text-sm text-gray-600">
          Showing {processedStudies.length} of {studies.length} studies
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <TableHeader field="author" label="Study" />
              <TableHeader field="year" label="Year" align="center" />
              <TableHeader field="sampleSize" label="N" align="right" />
              <TableHeader field="studyDesign" label="Design" />
              <TableHeader field="effectSize" label={effectMeasure} align="right" />
              <TableHeader field="lowerCI" label="95% CI" align="center" />
              <TableHeader field="weight" label="Weight %" align="right" />
              {showQualityScores && (
                <TableHeader field="qualityScore" label="Quality" align="center" />
              )}
              {subgroups.length > 0 && (
                <TableHeader field="subgroup" label="Subgroup" />
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {processedStudies.map((study, index) => (
              <tr
                key={study.id}
                className={`hover:bg-gray-50 transition-colors ${
                  index % 2 === 0 ? 'bg-white' : 'bg-gray-25'
                }`}
              >
                <td className="px-4 py-3 text-sm text-gray-900 font-medium">
                  {study.author}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700 text-center">
                  {study.year}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700 text-right">
                  {study.sampleSize.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700">
                  <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs">
                    {study.studyDesign}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-900 font-medium text-right">
                  {study.effectSize.toFixed(3)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-700 text-center whitespace-nowrap">
                  [{study.lowerCI.toFixed(3)}, {study.upperCI.toFixed(3)}]
                </td>
                <td className="px-4 py-3 text-sm text-gray-700 text-right">
                  {study.weight.toFixed(1)}%
                </td>
                {showQualityScores && (
                  <td className="px-4 py-3 text-center">
                    {study.qualityScore !== undefined ? (
                      <div className="inline-flex items-center justify-center">
                        <div className={`w-12 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                          study.qualityScore >= 7
                            ? 'bg-green-100 text-green-700'
                            : study.qualityScore >= 4
                            ? 'bg-yellow-100 text-yellow-700'
                            : 'bg-red-100 text-red-700'
                        }`}>
                          {study.qualityScore}/10
                        </div>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-xs">N/A</span>
                    )}
                  </td>
                )}
                {subgroups.length > 0 && (
                  <td className="px-4 py-3 text-sm">
                    {study.subgroup ? (
                      <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs">
                        {study.subgroup}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-xs">-</span>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>

        {/* Empty state */}
        {processedStudies.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-sm">No studies found matching your filters.</p>
            <button
              onClick={() => {
                setSearchTerm('');
                setSubgroupFilter('all');
              }}
              className="mt-2 text-sm text-blue-500 hover:text-blue-600"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>

      {/* Summary statistics */}
      <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <div className="text-gray-600 text-xs mb-1">Total Studies</div>
            <div className="font-semibold text-gray-900">{processedStudies.length}</div>
          </div>
          <div>
            <div className="text-gray-600 text-xs mb-1">Total Participants</div>
            <div className="font-semibold text-gray-900">
              {processedStudies.reduce((sum, s) => sum + s.sampleSize, 0).toLocaleString()}
            </div>
          </div>
          <div>
            <div className="text-gray-600 text-xs mb-1">Mean Effect Size</div>
            <div className="font-semibold text-gray-900">
              {(processedStudies.reduce((sum, s) => sum + s.effectSize, 0) / processedStudies.length).toFixed(3)}
            </div>
          </div>
          {showQualityScores && (
            <div>
              <div className="text-gray-600 text-xs mb-1">Mean Quality Score</div>
              <div className="font-semibold text-gray-900">
                {(() => {
                  const studiesWithQuality = processedStudies.filter(s => s.qualityScore !== undefined);
                  if (studiesWithQuality.length === 0) return 'N/A';
                  const mean = studiesWithQuality.reduce((sum, s) => sum + (s.qualityScore ?? 0), 0) / studiesWithQuality.length;
                  return `${mean.toFixed(1)}/10`;
                })()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudyCharacteristicsTable;
