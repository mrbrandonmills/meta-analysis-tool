import React, { useState, useRef, useEffect } from 'react';
import { X, Tag } from 'lucide-react';
import { cn } from '@/lib/utils';
import { COMMON_RESEARCH_KEYWORDS } from '@/types/onboarding';

interface KeywordInputProps {
  keywords: string[];
  onChange: (keywords: string[]) => void;
  minKeywords?: number;
  maxKeywords?: number;
  className?: string;
}

export const KeywordInput: React.FC<KeywordInputProps> = ({
  keywords,
  onChange,
  minKeywords = 5,
  maxKeywords = 20,
  className,
}) => {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  const isAtMin = keywords.length >= minKeywords;
  const isAtMax = keywords.length >= maxKeywords;

  useEffect(() => {
    if (input.trim()) {
      const filtered = COMMON_RESEARCH_KEYWORDS.filter(
        (keyword) =>
          keyword.toLowerCase().includes(input.toLowerCase()) &&
          !keywords.includes(keyword)
      ).slice(0, 5);
      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }, [input, keywords]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current &&
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAddKeyword = (keyword: string) => {
    const trimmed = keyword.trim();
    if (trimmed && !keywords.includes(trimmed) && !isAtMax) {
      onChange([...keywords, trimmed]);
      setInput('');
      setSuggestions([]);
      setShowSuggestions(false);
      inputRef.current?.focus();
    }
  };

  const handleRemoveKeyword = (keyword: string) => {
    onChange(keywords.filter((k) => k !== keyword));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      if (suggestions.length > 0 && showSuggestions) {
        handleAddKeyword(suggestions[0]);
      } else if (input.trim()) {
        handleAddKeyword(input);
      }
    } else if (e.key === 'Backspace' && !input && keywords.length > 0) {
      handleRemoveKeyword(keywords[keywords.length - 1]);
    }
  };

  const getStatusColor = () => {
    if (isAtMin) return 'text-green-600';
    return 'text-orange-500';
  };

  const getStatusMessage = () => {
    if (keywords.length < minKeywords) {
      return `Add at least ${minKeywords - keywords.length} more keyword${
        minKeywords - keywords.length === 1 ? '' : 's'
      }`;
    }
    if (isAtMax) {
      return 'Maximum keywords reached';
    }
    return `${maxKeywords - keywords.length} more keyword${
      maxKeywords - keywords.length === 1 ? '' : 's'
    } available`;
  };

  return (
    <div className={cn('space-y-3', className)}>
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          Research Keywords
          <span className="text-red-500 ml-1">*</span>
        </label>
        <span className={cn('text-xs font-medium', getStatusColor())}>
          {keywords.length}/{maxKeywords} keywords
        </span>
      </div>

      {/* Keywords display */}
      <div
        className={cn(
          'min-h-[100px] p-3 border-2 rounded-lg transition-colors focus-within:border-green-500 focus-within:ring-2 focus-within:ring-green-200',
          keywords.length < minKeywords ? 'border-orange-300' : 'border-gray-300'
        )}
      >
        <div className="flex flex-wrap gap-2 mb-2">
          {keywords.map((keyword) => (
            <div
              key={keyword}
              className="group flex items-center gap-1 px-3 py-1.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full text-sm font-medium shadow-sm hover:shadow-md transition-shadow"
            >
              <Tag className="w-3 h-3" aria-hidden="true" />
              {keyword}
              <button
                type="button"
                onClick={() => handleRemoveKeyword(keyword)}
                className="ml-1 hover:bg-white/20 rounded-full p-0.5 transition-colors focus:outline-none focus:ring-2 focus:ring-white"
                aria-label={`Remove keyword ${keyword}`}
              >
                <X className="w-3 h-3" />
              </button>
            </div>
          ))}
        </div>

        {/* Input */}
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowSuggestions(suggestions.length > 0)}
            placeholder={
              isAtMax
                ? 'Maximum keywords reached'
                : 'Type and press Enter to add keywords...'
            }
            disabled={isAtMax}
            className="w-full px-2 py-1 text-sm bg-transparent outline-none disabled:cursor-not-allowed placeholder:text-gray-400"
            aria-label="Add keyword"
          />

          {/* Autocomplete suggestions */}
          {showSuggestions && suggestions.length > 0 && (
            <div
              ref={suggestionsRef}
              className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-48 overflow-y-auto"
            >
              {suggestions.map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => handleAddKeyword(suggestion)}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-green-50 focus:bg-green-50 focus:outline-none transition-colors flex items-center gap-2"
                >
                  <Tag className="w-3 h-3 text-green-600" aria-hidden="true" />
                  {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Status message */}
      <div className="flex items-center justify-between">
        <p className={cn('text-xs font-medium', getStatusColor())}>
          {getStatusMessage()}
        </p>
        {!isAtMin && (
          <p className="text-xs text-gray-500 italic">
            Minimum {minKeywords} required
          </p>
        )}
      </div>

      {/* Helper text */}
      <p className="text-xs text-gray-500 italic">
        Add specific research keywords like "fMRI", "working memory", "cognitive load" to help us match you with relevant papers
      </p>
    </div>
  );
};

export default KeywordInput;
