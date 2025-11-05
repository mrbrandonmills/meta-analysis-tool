import React, { useState } from 'react';
import Button from '@/components/shared/Button';
import { Card, CardHeader, CardContent } from '@/components/shared/Card';
import { Search, Plus, X } from 'lucide-react';

interface SearchFormProps {
  onSubmit: (data: SearchFormData) => void;
  loading?: boolean;
}

export interface SearchFormData {
  researchQuestion: string;
  topic: string;
  inclusionCriteria: string[];
  exclusionCriteria: string[];
  databases: string[];
  peerReviewOnly: boolean;
}

const availableDatabases = [
  { id: 'pubmed', name: 'PubMed', description: '35M+ biomedical literature' },
  { id: 'arxiv', name: 'arXiv', description: 'Preprints in physics, math, CS' },
  { id: 'europepmc', name: 'Europe PMC', description: 'European biomedical database' },
  { id: 'core', name: 'CORE', description: 'Open access research papers' }
];

export const SearchForm: React.FC<SearchFormProps> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = useState<SearchFormData>({
    researchQuestion: '',
    topic: '',
    inclusionCriteria: ['Randomized controlled trial', 'Adult population (18+)', 'Published in peer-reviewed journal'],
    exclusionCriteria: ['Non-English language', 'Qualitative studies'],
    databases: ['pubmed', 'arxiv', 'europepmc', 'core'],
    peerReviewOnly: false
  });

  const [newInclusion, setNewInclusion] = useState('');
  const [newExclusion, setNewExclusion] = useState('');

  const addCriteria = (type: 'inclusion' | 'exclusion') => {
    const value = type === 'inclusion' ? newInclusion : newExclusion;
    if (!value.trim()) return;

    setFormData(prev => ({
      ...prev,
      [type === 'inclusion' ? 'inclusionCriteria' : 'exclusionCriteria']: [
        ...prev[type === 'inclusion' ? 'inclusionCriteria' : 'exclusionCriteria'],
        value.trim()
      ]
    }));

    if (type === 'inclusion') setNewInclusion('');
    else setNewExclusion('');
  };

  const removeCriteria = (type: 'inclusion' | 'exclusion', index: number) => {
    setFormData(prev => ({
      ...prev,
      [type === 'inclusion' ? 'inclusionCriteria' : 'exclusionCriteria']:
        prev[type === 'inclusion' ? 'inclusionCriteria' : 'exclusionCriteria'].filter((_, i) => i !== index)
    }));
  };

  const toggleDatabase = (dbId: string) => {
    setFormData(prev => ({
      ...prev,
      databases: prev.databases.includes(dbId)
        ? prev.databases.filter(id => id !== dbId)
        : [...prev.databases, dbId]
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Card variant="bordered">
        <CardHeader title="Research Question" subtitle="Define your meta-analysis research question" />
        <CardContent>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Research Question *
              </label>
              <input
                type="text"
                value={formData.researchQuestion}
                onChange={(e) => setFormData({ ...formData, researchQuestion: e.target.value })}
                placeholder="e.g., What is the effect of mindfulness on anxiety?"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Topic *
              </label>
              <input
                type="text"
                value={formData.topic}
                onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                placeholder="e.g., Mindfulness and Anxiety"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card variant="bordered">
        <CardHeader title="Inclusion Criteria" subtitle="Studies must meet these criteria to be included" />
        <CardContent>
          <div className="space-y-3">
            {formData.inclusionCriteria.map((criteria, index) => (
              <div key={index} className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg px-4 py-2">
                <span className="text-sm text-gray-700">{criteria}</span>
                <button
                  type="button"
                  onClick={() => removeCriteria('inclusion', index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}

            <div className="flex space-x-2">
              <input
                type="text"
                value={newInclusion}
                onChange={(e) => setNewInclusion(e.target.value)}
                placeholder="Add inclusion criterion"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCriteria('inclusion'))}
              />
              <Button
                type="button"
                variant="outline"
                icon={<Plus className="w-4 h-4" />}
                onClick={() => addCriteria('inclusion')}
              >
                Add
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card variant="bordered">
        <CardHeader title="Exclusion Criteria" subtitle="Studies meeting these criteria will be excluded" />
        <CardContent>
          <div className="space-y-3">
            {formData.exclusionCriteria.map((criteria, index) => (
              <div key={index} className="flex items-center justify-between bg-red-50 border border-red-200 rounded-lg px-4 py-2">
                <span className="text-sm text-gray-700">{criteria}</span>
                <button
                  type="button"
                  onClick={() => removeCriteria('exclusion', index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}

            <div className="flex space-x-2">
              <input
                type="text"
                value={newExclusion}
                onChange={(e) => setNewExclusion(e.target.value)}
                placeholder="Add exclusion criterion"
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addCriteria('exclusion'))}
              />
              <Button
                type="button"
                variant="outline"
                icon={<Plus className="w-4 h-4" />}
                onClick={() => addCriteria('exclusion')}
              >
                Add
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card variant="bordered">
        <CardHeader title="Databases" subtitle="Select databases to search" />
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {availableDatabases.map((db) => (
              <label
                key={db.id}
                className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  formData.databases.includes(db.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="checkbox"
                  checked={formData.databases.includes(db.id)}
                  onChange={() => toggleDatabase(db.id)}
                  className="mt-1 mr-3"
                />
                <div>
                  <p className="font-medium text-gray-900">{db.name}</p>
                  <p className="text-sm text-gray-600">{db.description}</p>
                </div>
              </label>
            ))}
          </div>

          <div className="mt-4 flex items-center">
            <input
              type="checkbox"
              id="peerReviewOnly"
              checked={formData.peerReviewOnly}
              onChange={(e) => setFormData({ ...formData, peerReviewOnly: e.target.checked })}
              className="mr-2"
            />
            <label htmlFor="peerReviewOnly" className="text-sm text-gray-700">
              Peer-reviewed studies only (exclude preprints)
            </label>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end space-x-4">
        <Button variant="outline" type="button">
          Save as Draft
        </Button>
        <Button
          variant="primary"
          type="submit"
          loading={loading}
          icon={<Search className="w-4 h-4" />}
        >
          Start Meta-Analysis
        </Button>
      </div>
    </form>
  );
};

export default SearchForm;
