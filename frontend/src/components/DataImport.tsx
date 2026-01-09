import React, { useState, useRef } from 'react';
import {
    Upload,
    Mail,
    FileSpreadsheet,
    CheckCircle,
    Loader2,
    AlertCircle,
    Sparkles,
    Shield,
    TrendingUp,
    Calendar
} from 'lucide-react';
import { cn } from '../lib/utils';

export type DateRangeOption = '30_days' | '60_days' | '90_days' | '1_year';

interface DataImportProps {
    onFileUpload: (file: File) => void;
    onEmailConnect: (tokenResponse: any, dateRange: DateRangeOption) => void;
    isLoading: boolean;
    isGoogleConfigured: boolean;
}

export function DataImport({ onFileUpload, onEmailConnect: _onEmailConnect, isLoading, isGoogleConfigured: _isGoogleConfigured }: DataImportProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [selectedMethod, setSelectedMethod] = useState<'csv' | 'email' | null>(null);
    const [fileName, setFileName] = useState('');
    const [error, setError] = useState('');
    const [dateRange, setDateRange] = useState<DateRangeOption>('30_days');

    const dateRangeOptions: { value: DateRangeOption; label: string }[] = [
        { value: '30_days', label: 'Last 30 Days' },
        { value: '60_days', label: 'Last 60 Days' },
        { value: '90_days', label: 'Last 90 Days' },
        { value: '1_year', label: 'Last Year' },
    ];

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;
        setFileName(file.name);
        setError('');
        onFileUpload(file);
    };

    const handleEmailSync = async () => {
        setError('');
        try {
            // Store date range in sessionStorage so it persists after OAuth redirect
            sessionStorage.setItem('email_date_range', dateRange);

            // Use server-side OAuth flow - get authorization URL from backend
            const response = await fetch('http://localhost:8000/api/auth/google/signup');
            const data = await response.json();

            if (data.authorization_url) {
                // Redirect to Google OAuth consent screen
                window.location.href = data.authorization_url;
            } else {
                setError('Failed to start Google OAuth. Please check backend configuration.');
            }
        } catch (err) {
            setError('Failed to connect to backend. Ensure the server is running.');
            console.error('OAuth error:', err);
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto">
            {/* Benefits Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                    <TrendingUp className="w-6 h-6 text-success mb-2" />
                    <h3 className="text-white font-medium mb-1">Detect Leaks</h3>
                    <p className="text-slate-400 text-sm">Find hidden subscriptions and recurring charges</p>
                </div>
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                    <Sparkles className="w-6 h-6 text-accent mb-2" />
                    <h3 className="text-white font-medium mb-1">AI Insights</h3>
                    <p className="text-slate-400 text-sm">Get smart recommendations powered by Gemini</p>
                </div>
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                    <Shield className="w-6 h-6 text-primary mb-2" />
                    <h3 className="text-white font-medium mb-1">Secure & Private</h3>
                    <p className="text-slate-400 text-sm">Your data never leaves your local machine</p>
                </div>
            </div>

            {/* Import Options Card */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 md:p-8 border border-white/20">
                <h2 className="text-xl font-semibold text-white mb-6 text-center">
                    Choose how to import your transactions
                </h2>

                {/* Error Message */}
                {error && (
                    <div className="mb-6 p-4 bg-danger/20 border border-danger/50 rounded-xl flex items-center gap-3">
                        <AlertCircle className="w-5 h-5 text-danger flex-shrink-0" />
                        <p className="text-red-300">{error}</p>
                    </div>
                )}

                {/* Loading State */}
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center py-12">
                        <Loader2 className="h-12 w-12 text-primary animate-spin" />
                        <p className="mt-4 text-lg font-medium text-white">Processing your data...</p>
                        <p className="text-slate-400">This might take a moment.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-1 gap-6">
                        {/* CSV Upload Option */}
                        <div
                            className={cn(
                                "relative p-6 rounded-xl border-2 transition-all cursor-pointer",
                                selectedMethod === 'csv'
                                    ? "border-primary bg-primary/10"
                                    : "border-white/20 bg-white/5 hover:border-primary/50 hover:bg-white/10"
                            )}
                            onClick={() => setSelectedMethod('csv')}
                        >
                            <div className="flex items-start gap-4">
                                <div className={cn(
                                    "p-3 rounded-xl",
                                    selectedMethod === 'csv' ? "bg-primary" : "bg-white/10"
                                )}>
                                    <FileSpreadsheet className={cn(
                                        "w-6 h-6",
                                        selectedMethod === 'csv' ? "text-white" : "text-primary"
                                    )} />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-white font-semibold mb-1">Upload Statement</h3>
                                    <p className="text-slate-400 text-sm mb-4">
                                        Upload your bank statement (CSV, Excel, or PDF)
                                    </p>

                                    {selectedMethod === 'csv' && (
                                        <div className="space-y-3">
                                            <input
                                                ref={fileInputRef}
                                                type="file"
                                                accept=".csv,.xlsx,.pdf"
                                                onChange={handleFileChange}
                                                className="hidden"
                                            />
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    fileInputRef.current?.click();
                                                }}
                                                className="w-full py-3 px-4 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
                                            >
                                                <Upload className="w-5 h-5" />
                                                Select File
                                            </button>
                                            {fileName && (
                                                <p className="text-sm text-slate-400 text-center">{fileName}</p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                            {selectedMethod === 'csv' && (
                                <div className="absolute top-3 right-3">
                                    <CheckCircle className="w-5 h-5 text-primary" />
                                </div>
                            )}
                        </div>

                        {/* Email Sync Option - COMMENTED OUT */}
                        {/* <div
                            className={cn(
                                "relative p-6 rounded-xl border-2 transition-all cursor-pointer",
                                selectedMethod === 'email'
                                    ? "border-accent bg-accent/10"
                                    : "border-white/20 bg-white/5 hover:border-accent/50 hover:bg-white/10"
                            )}
                            onClick={() => setSelectedMethod('email')}
                        >
                            <div className="flex items-start gap-4">
                                <div className={cn(
                                    "p-3 rounded-xl",
                                    selectedMethod === 'email' ? "bg-accent" : "bg-white/10"
                                )}>
                                    <Mail className={cn(
                                        "w-6 h-6",
                                        selectedMethod === 'email' ? "text-white" : "text-accent"
                                    )} />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-white font-semibold mb-1">Connect Email</h3>
                                    <p className="text-slate-400 text-sm mb-4">
                                        Scan bank transaction alerts from Gmail
                                    </p>

                                    {selectedMethod === 'email' && (
                                        <div className="space-y-4">
                                            <div className="space-y-2">
                                                <label className="flex items-center gap-2 text-sm text-slate-300 font-medium">
                                                    <Calendar className="w-4 h-4" />
                                                    Select Date Range
                                                </label>
                                                <div className="grid grid-cols-2 gap-2">
                                                    {dateRangeOptions.map((option) => (
                                                        <button
                                                            key={option.value}
                                                            type="button"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                setDateRange(option.value);
                                                            }}
                                                            className={cn(
                                                                "py-2 px-3 rounded-lg text-sm font-medium transition-all",
                                                                dateRange === option.value
                                                                    ? "bg-accent text-white"
                                                                    : "bg-white/10 text-slate-300 hover:bg-white/20"
                                                            )}
                                                        >
                                                            {option.label}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>

                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    handleEmailSync();
                                                }}
                                                className="w-full py-3 px-4 bg-accent text-white rounded-lg font-medium hover:bg-accent/90 transition-colors flex items-center justify-center gap-2"
                                            >
                                                <Mail className="w-5 h-5" />
                                                Connect with Google
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                            {selectedMethod === 'email' && (
                                <div className="absolute top-3 right-3">
                                    <CheckCircle className="w-5 h-5 text-accent" />
                                </div>
                            )}
                        </div> */}
                    </div>
                )}
            </div>

            {/* Footer */}
            <p className="text-center text-slate-500 text-sm mt-6">
                Your data is processed locally and never shared with third parties.
            </p>
        </div>
    );
}
