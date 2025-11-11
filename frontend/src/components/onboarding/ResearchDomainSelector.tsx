import React, { useState } from 'react';
import { X, Plus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ResearchDomain, RESEARCH_DOMAINS } from '@/types/onboarding';

interface ResearchDomainSelectorProps {
  selectedDomains: ResearchDomain[];
  customDomains?: string[];
  onChange: (domains: ResearchDomain[], customDomains?: string[]) => void;
  maxSelections?: number;
  className?: string;
}

export const ResearchDomainSelector: React.FC<ResearchDomainSelectorProps> = ({
  selectedDomains,
  customDomains = [],
  onChange,
  maxSelections = 5,
  className,
}) => {
  const [customInput, setCustomInput] = useState('');
  const [showCustomInput, setShowCustomInput] = useState(false);

  const handleDomainToggle = (domain: ResearchDomain) => {
    if (selectedDomains.includes(domain)) {
      onChange(
        selectedDomains.filter((d) => d !== domain),
        customDomains
      );
    } else {
      if (selectedDomains.length < maxSelections) {
        onChange([...selectedDomains, domain], customDomains);
      }
    }
  };

  const handleAddCustomDomain = () => {
    const trimmed = customInput.trim();
    if (trimmed && !customDomains.includes(trimmed)) {
      const totalSelections = selectedDomains.length + customDomains.length;
      if (totalSelections < maxSelections) {
        onChange(selectedDomains, [...customDomains, trimmed]);
        setCustomInput('');
        setShowCustomInput(false);
      }
    }
  };

  const handleRemoveCustomDomain = (domain: string) => {
    onChange(
      selectedDomains,
      customDomains.filter((d) => d !== domain)
    );
  };

  const totalSelections = selectedDomains.length + customDomains.length;
  const canAddMore = totalSelections < maxSelections;

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Primary Research Domains
          <span className="text-red-500 ml-1">*</span>
        </label>
        <span className="text-xs text-gray-500">
          {totalSelections}/{maxSelections} selected
        </span>
      </div>

      {/* Predefined domains */}
      <div className="flex flex-wrap gap-2">
        {RESEARCH_DOMAINS.map((domain) => {
          const isSelected = selectedDomains.includes(domain.value);
          const isDisabled = !isSelected && !canAddMore;

          return (
            <button
              key={domain.value}
              type="button"
              onClick={() => handleDomainToggle(domain.value)}
              disabled={isDisabled}
              className={cn(
                'px-4 py-2 rounded-full text-sm font-medium transition-all duration-200',
                'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
                isSelected
                  ? 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-md hover:shadow-lg transform hover:scale-105'
                  : 'bg-white border-2 border-gray-300 text-gray-700 hover:border-green-400 hover:bg-green-50',
                isDisabled && 'opacity-50 cursor-not-allowed hover:border-gray-300 hover:bg-white'
              )}
              aria-pressed={isSelected}
            >
              {domain.label}
              {isSelected && <X className="inline-block ml-1 w-3 h-3" />}
            </button>
          );
        })}
      </div>

      {/* Custom domains */}
      {customDomains.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Custom Domains</p>
          <div className="flex flex-wrap gap-2">
            {customDomains.map((domain) => (
              <div
                key={domain}
                className="px-4 py-2 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 text-white text-sm font-medium shadow-md flex items-center gap-2"
              >
                {domain}
                <button
                  type="button"
                  onClick={() => handleRemoveCustomDomain(domain)}
                  className="hover:bg-white/20 rounded-full p-0.5 transition-colors focus:outline-none focus:ring-2 focus:ring-white"
                  aria-label={`Remove ${domain}`}
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add custom domain */}
      {showCustomInput ? (
        <div className="flex gap-2">
          <input
            type="text"
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleAddCustomDomain()}
            placeholder="Enter custom domain"
            className="flex-1 px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            autoFocus
          />
          <button
            type="button"
            onClick={handleAddCustomDomain}
            disabled={!customInput.trim()}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Add
          </button>
          <button
            type="button"
            onClick={() => {
              setShowCustomInput(false);
              setCustomInput('');
            }}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setShowCustomInput(true)}
          disabled={!canAddMore}
          className={cn(
            'flex items-center gap-2 px-4 py-2 text-sm font-medium text-green-600 border-2 border-dashed border-green-300 rounded-lg hover:bg-green-50 transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
            !canAddMore && 'opacity-50 cursor-not-allowed hover:bg-white'
          )}
        >
          <Plus className="w-4 h-4" />
          Add Custom Domain
        </button>
      )}

      <p className="text-xs text-gray-500 italic">
        Select up to {maxSelections} domains that best represent your research areas
      </p>
    </div>
  );
};

export default ResearchDomainSelector;
