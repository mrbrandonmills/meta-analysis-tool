import React, { useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import {
  ChevronUp,
  ChevronDown,
  User,
  Building2,
  Award,
  DollarSign,
  CheckCircle2,
  Search,
  Filter
} from 'lucide-react';
import { ResearcherListItem } from '@/lib/payment-types';

interface ReviewerTableProps {
  researchers: ResearcherListItem[];
  onResearcherClick?: (researcher: ResearcherListItem) => void;
  itemsPerPage?: number;
}

type SortField = 'name' | 'hIndex' | 'lifetimeEarnings' | 'lifetimeReviews' | 'averageReviewQuality';
type SortDirection = 'asc' | 'desc';

export const ReviewerTable: React.FC<ReviewerTableProps> = ({
  researchers,
  onResearcherClick,
  itemsPerPage = 10
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<SortField>('hIndex');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDomain, setFilterDomain] = useState<string>('');

  // Get unique domains for filter
  const uniqueDomains = useMemo(() => {
    const domains = new Set<string>();
    researchers.forEach(r => r.expertiseDomains.forEach(d => domains.add(d)));
    return Array.from(domains).sort();
  }, [researchers]);

  // Filter and sort
  const filteredAndSortedResearchers = useMemo(() => {
    let filtered = researchers.filter(r => {
      const matchesSearch = searchQuery === '' ||
        r.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.institution.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.email.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesDomain = filterDomain === '' ||
        r.expertiseDomains.some(d => d.toLowerCase().includes(filterDomain.toLowerCase()));

      return matchesSearch && matchesDomain;
    });

    // Sort
    filtered.sort((a, b) => {
      let aVal: number | string = 0;
      let bVal: number | string = 0;

      switch (sortField) {
        case 'name':
          aVal = a.name;
          bVal = b.name;
          break;
        case 'hIndex':
          aVal = a.hIndex || 0;
          bVal = b.hIndex || 0;
          break;
        case 'lifetimeEarnings':
          aVal = a.lifetimeEarnings;
          bVal = b.lifetimeEarnings;
          break;
        case 'lifetimeReviews':
          aVal = a.lifetimeReviews;
          bVal = b.lifetimeReviews;
          break;
        case 'averageReviewQuality':
          aVal = a.averageReviewQuality;
          bVal = b.averageReviewQuality;
          break;
      }

      if (typeof aVal === 'string' && typeof bVal === 'string') {
        return sortDirection === 'asc'
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      }

      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    });

    return filtered;
  }, [researchers, searchQuery, filterDomain, sortField, sortDirection]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedResearchers.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedResearchers = filteredAndSortedResearchers.slice(
    startIndex,
    startIndex + itemsPerPage
  );

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return null;
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4" />
    ) : (
      <ChevronDown className="w-4 h-4" />
    );
  };

  return (
    <div className="space-y-4">
      {/* Search and Filter */}
      <div className="flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name, email, or institution..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
          />
        </div>
        <div className="relative min-w-[200px]">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <select
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all appearance-none bg-white"
            value={filterDomain}
            onChange={(e) => {
              setFilterDomain(e.target.value);
              setCurrentPage(1);
            }}
          >
            <option value="">All Domains</option>
            {uniqueDomains.map(domain => (
              <option key={domain} value={domain}>{domain}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border-2 border-gray-200 overflow-hidden bg-white">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th
                  className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('name')}
                >
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    Researcher
                    <SortIcon field="name" />
                  </div>
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-4 h-4" />
                    Institution
                  </div>
                </th>
                <th
                  className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('hIndex')}
                >
                  <div className="flex items-center gap-2">
                    <Award className="w-4 h-4" />
                    H-Index
                    <SortIcon field="hIndex" />
                  </div>
                </th>
                <th
                  className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('lifetimeReviews')}
                >
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" />
                    Reviews
                    <SortIcon field="lifetimeReviews" />
                  </div>
                </th>
                <th
                  className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100 transition-colors"
                  onClick={() => handleSort('lifetimeEarnings')}
                >
                  <div className="flex items-center gap-2">
                    <DollarSign className="w-4 h-4" />
                    Earnings
                    <SortIcon field="lifetimeEarnings" />
                  </div>
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {paginatedResearchers.map((researcher, index) => (
                <motion.tr
                  key={researcher.id}
                  className="hover:bg-gray-50 transition-colors cursor-pointer"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.02 }}
                  onClick={() => onResearcherClick?.(researcher)}
                >
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-semibold text-gray-900">{researcher.name}</div>
                      <div className="text-sm text-gray-500">{researcher.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-700">
                    {researcher.institution}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 text-sm font-semibold">
                        {researcher.hIndex || '--'}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                    {researcher.lifetimeReviews}
                  </td>
                  <td className="px-6 py-4 text-sm font-semibold text-green-600">
                    ${researcher.lifetimeEarnings.toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium ${
                      researcher.isPayingMember
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      <div className={`w-2 h-2 rounded-full ${
                        researcher.isPayingMember ? 'bg-green-500' : 'bg-gray-400'
                      }`} />
                      {researcher.isPayingMember ? 'Active' : 'Inactive'}
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Showing {startIndex + 1} to {Math.min(startIndex + itemsPerPage, filteredAndSortedResearchers.length)} of{' '}
            {filteredAndSortedResearchers.length} researchers
          </div>
          <div className="flex gap-2">
            <button
              className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              onClick={() => setCurrentPage(p => p - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </button>
            <div className="flex gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const page = i + 1;
                return (
                  <button
                    key={page}
                    className={`px-3 py-2 rounded-lg font-medium transition-colors ${
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                    onClick={() => setCurrentPage(page)}
                  >
                    {page}
                  </button>
                );
              })}
              {totalPages > 5 && <span className="px-2 py-2 text-gray-500">...</span>}
            </div>
            <button
              className="px-4 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              onClick={() => setCurrentPage(p => p + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReviewerTable;
