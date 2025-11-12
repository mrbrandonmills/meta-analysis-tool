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
  Filter,
  Download,
  Eye,
  Ban,
  MoreVertical,
  Calendar,
  Mail
} from 'lucide-react';
import { ResearcherListItem } from '@/lib/payment-types';
import { Button } from '../shared/Button';
import { downloadBlob } from '@/lib/utils';

interface EnhancedResearcherTableProps {
  researchers: ResearcherListItem[];
  onResearcherClick?: (researcher: ResearcherListItem) => void;
  onSuspend?: (researcherId: string) => void;
  onViewActivity?: (researcherId: string) => void;
  itemsPerPage?: number;
}

type SortField = 'name' | 'hIndex' | 'lifetimeEarnings' | 'lifetimeReviews' | 'averageReviewQuality';
type SortDirection = 'asc' | 'desc';

export const EnhancedResearcherTable: React.FC<EnhancedResearcherTableProps> = ({
  researchers,
  onResearcherClick,
  onSuspend,
  onViewActivity,
  itemsPerPage = 10
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortField, setSortField] = useState<SortField>('hIndex');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all');
  const [filterDomain, setFilterDomain] = useState<string>('');
  const [selectedRows, setSelectedRows] = useState<Set<string>>(new Set());
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

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

      const matchesStatus = filterStatus === 'all' ||
        (filterStatus === 'active' && r.isPayingMember) ||
        (filterStatus === 'inactive' && !r.isPayingMember);

      const matchesDomain = filterDomain === '' ||
        r.expertiseDomains.some(d => d.toLowerCase().includes(filterDomain.toLowerCase()));

      return matchesSearch && matchesStatus && matchesDomain;
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

      const numA = aVal as number;
      const numB = bVal as number;
      return sortDirection === 'asc' ? numA - numB : numB - numA;
    });

    return filtered;
  }, [researchers, searchQuery, filterStatus, filterDomain, sortField, sortDirection]);

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

  const handleSelectAll = () => {
    if (selectedRows.size === paginatedResearchers.length) {
      setSelectedRows(new Set());
    } else {
      setSelectedRows(new Set(paginatedResearchers.map(r => r.id)));
    }
  };

  const handleSelectRow = (id: string) => {
    const newSelected = new Set(selectedRows);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedRows(newSelected);
  };

  const exportToCSV = () => {
    const dataToExport = selectedRows.size > 0
      ? filteredAndSortedResearchers.filter(r => selectedRows.has(r.id))
      : filteredAndSortedResearchers;

    const headers = [
      'Name',
      'Email',
      'Institution',
      'H-Index',
      'Expertise Domains',
      'Subscription Status',
      'Member Since',
      'Lifetime Reviews',
      'Lifetime Earnings',
      'Average Review Quality',
      'Stripe Connect Status'
    ];

    const rows = dataToExport.map(r => [
      r.name,
      r.email,
      r.institution,
      r.hIndex || 'N/A',
      r.expertiseDomains.join('; '),
      r.subscriptionStatus,
      r.memberSince || 'N/A',
      r.lifetimeReviews,
      r.lifetimeEarnings.toFixed(2),
      r.averageReviewQuality.toFixed(2),
      r.stripeConnectStatus
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    downloadBlob(blob, `researchers-export-${new Date().toISOString().split('T')[0]}.csv`);
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
      {/* Search and Filters */}
      <div className="flex gap-4 flex-wrap">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name, email, or institution..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
          />
        </div>

        <select
          className="px-4 py-2.5 rounded-xl border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all appearance-none bg-white"
          value={filterStatus}
          onChange={(e) => {
            setFilterStatus(e.target.value as any);
            setCurrentPage(1);
          }}
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>

        <div className="relative min-w-[200px]">
          <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <select
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all appearance-none bg-white"
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

        <Button
          variant="outline"
          icon={<Download className="w-4 h-4" />}
          onClick={exportToCSV}
        >
          Export {selectedRows.size > 0 ? `(${selectedRows.size})` : 'All'}
        </Button>
      </div>

      {/* Summary Stats */}
      <div className="flex items-center justify-between text-sm text-gray-600 bg-gray-50 rounded-xl p-4">
        <div className="flex items-center gap-6">
          <span>
            Showing <strong className="text-gray-900">{startIndex + 1}</strong> to{' '}
            <strong className="text-gray-900">
              {Math.min(startIndex + itemsPerPage, filteredAndSortedResearchers.length)}
            </strong>{' '}
            of <strong className="text-gray-900">{filteredAndSortedResearchers.length}</strong> researchers
          </span>
          {selectedRows.size > 0 && (
            <span className="px-3 py-1 rounded-full bg-blue-100 text-blue-700 font-medium">
              {selectedRows.size} selected
            </span>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="rounded-2xl border-2 border-gray-200 overflow-hidden bg-white">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th className="px-6 py-4 text-left">
                  <input
                    type="checkbox"
                    checked={selectedRows.size === paginatedResearchers.length && paginatedResearchers.length > 0}
                    onChange={handleSelectAll}
                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                </th>
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
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {paginatedResearchers.map((researcher, index) => (
                <motion.tr
                  key={researcher.id}
                  className="hover:bg-gray-50 transition-colors"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.02 }}
                >
                  <td className="px-6 py-4">
                    <input
                      type="checkbox"
                      checked={selectedRows.has(researcher.id)}
                      onChange={() => handleSelectRow(researcher.id)}
                      className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-semibold">
                        {researcher.name.split(' ').map(n => n[0]).join('').substring(0, 2)}
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{researcher.name}</div>
                        <div className="text-sm text-gray-500 flex items-center gap-1">
                          <Mail className="w-3 h-3" />
                          {researcher.email}
                        </div>
                      </div>
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
                  <td className="px-6 py-4">
                    <div className="relative">
                      <button
                        onClick={() => setActiveDropdown(activeDropdown === researcher.id ? null : researcher.id)}
                        className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <MoreVertical className="w-4 h-4 text-gray-600" />
                      </button>

                      {activeDropdown === researcher.id && (
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border-2 border-gray-200 z-10">
                          <button
                            onClick={() => {
                              onResearcherClick?.(researcher);
                              setActiveDropdown(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2 rounded-t-xl"
                          >
                            <Eye className="w-4 h-4" />
                            View Profile
                          </button>
                          <button
                            onClick={() => {
                              onViewActivity?.(researcher.id);
                              setActiveDropdown(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-2"
                          >
                            <Calendar className="w-4 h-4" />
                            View Activity
                          </button>
                          <button
                            onClick={() => {
                              onSuspend?.(researcher.id);
                              setActiveDropdown(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm text-red-700 hover:bg-red-50 flex items-center gap-2 rounded-b-xl"
                          >
                            <Ban className="w-4 h-4" />
                            Suspend Account
                          </button>
                        </div>
                      )}
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
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => p - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <div className="flex gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let page;
                if (totalPages <= 5) {
                  page = i + 1;
                } else if (currentPage <= 3) {
                  page = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  page = totalPages - 4 + i;
                } else {
                  page = currentPage - 2 + i;
                }

                return (
                  <button
                    key={page}
                    className={`px-3 py-2 rounded-lg font-medium transition-colors ${
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'bg-white border-2 border-gray-300 text-gray-700 hover:bg-gray-50'
                    }`}
                    onClick={() => setCurrentPage(page)}
                  >
                    {page}
                  </button>
                );
              })}
              {totalPages > 5 && currentPage < totalPages - 2 && (
                <span className="px-2 py-2 text-gray-500">...</span>
              )}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(p => p + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}

      {/* Click outside to close dropdown */}
      {activeDropdown && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setActiveDropdown(null)}
        />
      )}
    </div>
  );
};

export default EnhancedResearcherTable;
