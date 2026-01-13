import { useState, useEffect, useRef } from 'react';
import { AlertCircle, CheckCircle2, X, Lightbulb, ChevronDown } from 'lucide-react';
import { cn } from '../lib/utils';

export interface ColumnMapping {
  [key: string]: string | null; // requiredColumn: fileColumn
}

interface CustomDropdownProps {
  value: string | null;
  onChange: (value: string | null) => void;
  options: string[];
  placeholder: string;
  isMapped: boolean;
  disabled?: boolean;
}

function CustomDropdown({
  value,
  onChange,
  options,
  placeholder,
  isMapped,
  disabled = false,
}: CustomDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={dropdownRef} className="relative">
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={cn(
          'w-full px-4 py-2.5 rounded-lg border transition-all text-sm flex items-center justify-between',
          'focus:outline-none focus:ring-2 focus:ring-primary/50',
          isMapped
            ? 'border-primary/50 bg-primary/5'
            : 'border-slate-600/50 hover:border-slate-500/50 bg-slate-900/50',
          'text-slate-200',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <span className={value ? 'text-slate-200' : 'text-slate-500'}>
          {value || placeholder}
        </span>
        <ChevronDown
          className={cn(
            'w-4 h-4 transition-transform',
            isOpen ? 'rotate-180' : '',
            'text-slate-400'
          )}
        />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-slate-900 border border-slate-600/50 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto">
          <div className="p-1">
            {options.length === 0 ? (
              <div className="px-4 py-2 text-sm text-slate-400">No options available</div>
            ) : (
              options.map((option) => (
                <button
                  key={option}
                  onClick={() => {
                    onChange(option);
                    setIsOpen(false);
                  }}
                  className={cn(
                    'w-full text-left px-4 py-2 rounded text-sm transition-colors',
                    value === option
                      ? 'bg-primary/20 text-primary font-medium'
                      : 'text-slate-200 hover:bg-slate-800'
                  )}
                >
                  {option}
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}

interface ColumnMapperModalProps {
  isOpen: boolean;
  fileColumns: string[];
  requiredColumns: string[];
  initialMapping?: ColumnMapping;
  onConfirm: (mapping: ColumnMapping) => void;
  onCancel: () => void;
  suggestedMapping?: ColumnMapping;
}

export function ColumnMapperModal({
  isOpen,
  fileColumns,
  requiredColumns,
  initialMapping,
  onConfirm,
  onCancel,
  suggestedMapping,
}: ColumnMapperModalProps) {
  const [mapping, setMapping] = useState<ColumnMapping>(
    initialMapping || requiredColumns.reduce((acc, col) => ({ ...acc, [col]: null }), {})
  );

  // Update mapping when suggestedMapping changes
  useEffect(() => {
    if (suggestedMapping) {
      setMapping(suggestedMapping);
    }
  }, [suggestedMapping]);

  const isMappingComplete = requiredColumns.every((col) => mapping[col] !== null);

  const getUsedFileColumns = (): Set<string> => {
    return new Set(Object.values(mapping).filter((v) => v !== null) as string[]);
  };

  const availableColumnsForRequired = (requiredCol: string): string[] => {
    const usedColumns = getUsedFileColumns();
    const currentMapping = mapping[requiredCol];

    return fileColumns.filter((fileCol) => {
      if (fileCol === currentMapping) return true; // Always include current mapping
      return !usedColumns.has(fileCol);
    });
  };

  const handleMappingChange = (requiredCol: string, fileCol: string | null) => {
    setMapping((prev) => ({
      ...prev,
      [requiredCol]: fileCol,
    }));
  };

  const handleApplySuggested = () => {
    if (suggestedMapping) {
      setMapping(suggestedMapping);
    }
  };

  const handleReset = () => {
    setMapping(requiredColumns.reduce((acc, col) => ({ ...acc, [col]: null }), {}));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl border border-slate-700/50 shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-slate-900/95 backdrop-blur border-b border-slate-700/50 p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-white mb-1">Map Columns</h2>
              <p className="text-sm text-slate-400">
                Match your file columns to the required fields
              </p>
            </div>
            <button
              onClick={onCancel}
              className="p-2 hover:bg-slate-800 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-slate-400" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Suggestion Banner */}
          {suggestedMapping && !Object.values(suggestedMapping).every((v) => v === null) && (
            <div className="bg-primary/10 border border-primary/30 rounded-lg p-4 flex items-start gap-3">
              <Lightbulb className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-primary font-medium mb-2">Smart suggestion available</p>
                <p className="text-xs text-primary/80 mb-3">We detected your columns. Apply the suggestion or customize manually.</p>
                <button
                  onClick={handleApplySuggested}
                  className="text-xs font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Apply Suggestion
                </button>
              </div>
            </div>
          )}

          {/* File Columns Info */}
          <div className="bg-slate-800/50 rounded-lg p-4">
            <p className="text-xs text-slate-400 mb-2 font-medium">Available columns in your file:</p>
            <div className="flex flex-wrap gap-2">
              {fileColumns.map((col, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-slate-700/50 border border-slate-600/50 rounded-full text-xs text-slate-300"
                >
                  {col}
                </span>
              ))}
            </div>
          </div>

          {/* Mapping Section */}
          <div className="space-y-4">
            {requiredColumns.map((requiredCol) => {
              const currentMapping = mapping[requiredCol];
              const isMapped = currentMapping !== null;
              const availableColumns = availableColumnsForRequired(requiredCol);

              return (
                <div key={requiredCol} className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
                  <div className="flex items-center gap-3 mb-3">
                    {isMapped ? (
                      <CheckCircle2 className="w-5 h-5 text-success flex-shrink-0" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-slate-600 flex-shrink-0" />
                    )}
                    <label className="flex-1 text-sm font-medium text-slate-200">
                      {requiredCol}
                      <span className="text-danger ml-1">*</span>
                    </label>
                  </div>

                  <CustomDropdown
                    value={currentMapping}
                    onChange={(value) => handleMappingChange(requiredCol, value)}
                    options={availableColumns}
                    placeholder="Select a column..."
                    isMapped={isMapped}
                  />

                  {isMapped && (
                    <div className="mt-2 flex items-center gap-2 text-xs text-success">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Mapped to: <span className="font-medium">{currentMapping}</span></span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Validation Info */}
          <div className="bg-slate-800/30 rounded-lg p-4 border border-slate-700/50">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-slate-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-slate-300 font-medium mb-1">All fields required</p>
                <p className="text-xs text-slate-400">
                  You must map all {requiredColumns.length} columns before proceeding.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-slate-900/95 backdrop-blur border-t border-slate-700/50 p-6 flex gap-3">
          <button
            onClick={handleReset}
            className="px-4 py-2.5 rounded-lg border border-slate-600 text-slate-300 font-medium hover:bg-slate-800 transition-colors text-sm"
          >
            Reset
          </button>
          <button
            onClick={onCancel}
            className="px-4 py-2.5 rounded-lg bg-slate-800 text-slate-200 font-medium hover:bg-slate-700 transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            onClick={() => onConfirm(mapping)}
            disabled={!isMappingComplete}
            className={cn(
              'flex-1 px-4 py-2.5 rounded-lg font-medium text-sm transition-all',
              isMappingComplete
                ? 'bg-primary text-white hover:bg-primary/90 shadow-lg shadow-primary/20'
                : 'bg-slate-700 text-slate-400 cursor-not-allowed'
            )}
          >
            {isMappingComplete ? 'Confirm Mapping' : `Map All ${requiredColumns.length} Columns`}
          </button>
        </div>
      </div>
    </div>
  );
}
