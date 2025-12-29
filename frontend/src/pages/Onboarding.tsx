import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Upload,
    Mail,
    FileSpreadsheet,
    ArrowRight,
    CheckCircle,
    Loader2,
    AlertCircle,
    Sparkles,
    Shield,
    TrendingUp
} from 'lucide-react';
import api, { authService } from '../services/api';

const Onboarding: React.FC = () => {
    const navigate = useNavigate();
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [selectedMethod, setSelectedMethod] = useState<'csv' | 'email' | null>(null);
    const [uploading, setUploading] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [fileName, setFileName] = useState('');

    const handleCsvUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        setFileName(file.name);
        setError('');
        setSuccess('');
        setUploading(true);

        try {
            const result = await api.uploadCsv(file);
            setSuccess(`Successfully imported ${result.transactions_count || result.count || 'your'} transactions!`);

            // Wait a moment then redirect to dashboard
            setTimeout(() => {
                navigate('/');
            }, 2000);
        } catch (err: any) {
            setError(err.message || 'Failed to upload CSV file');
            setFileName('');
        } finally {
            setUploading(false);
        }
    };

    const handleEmailSync = async () => {
        setError('');
        setSuccess('');
        setSyncing(true);

        try {
            // First check if we have Google OAuth connected
            const { authorization_url } = await authService.initiateGoogleLogin();
            // Redirect to Google OAuth for email access
            window.location.href = authorization_url;
        } catch (err: any) {
            // If already authenticated with Google, try to sync
            try {
                const result = await api.syncEmails(30, 100);
                setSuccess(`Successfully synced ${result.transactions_found} transactions from your emails!`);

                setTimeout(() => {
                    navigate('/');
                }, 2000);
            } catch (syncErr: any) {
                setError(syncErr.message || 'Failed to sync emails. Please try again.');
            }
        } finally {
            setSyncing(false);
        }
    };

    const handleSkip = () => {
        // Mark onboarding as complete even without data
        localStorage.setItem('onboarding_complete', 'true');
        navigate('/');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
            <div className="max-w-4xl w-full">
                {/* Header */}
                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-purple-500/20 rounded-2xl mb-4">
                        <Sparkles className="w-8 h-8 text-purple-400" />
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
                        Welcome to FinGuard! 🎉
                    </h1>
                    <p className="text-gray-300 text-lg max-w-xl mx-auto">
                        Let's get you set up. Import your transactions to start tracking your spending and get smart insights.
                    </p>
                </div>

                {/* Benefits */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10">
                    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                        <TrendingUp className="w-6 h-6 text-green-400 mb-2" />
                        <h3 className="text-white font-medium mb-1">Track Spending</h3>
                        <p className="text-gray-400 text-sm">See where your money goes with automatic categorization</p>
                    </div>
                    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                        <Sparkles className="w-6 h-6 text-purple-400 mb-2" />
                        <h3 className="text-white font-medium mb-1">Smart Insights</h3>
                        <p className="text-gray-400 text-sm">Get AI-powered recommendations to save more</p>
                    </div>
                    <div className="bg-white/5 backdrop-blur-sm rounded-xl p-4 border border-white/10">
                        <Shield className="w-6 h-6 text-blue-400 mb-2" />
                        <h3 className="text-white font-medium mb-1">Secure & Private</h3>
                        <p className="text-gray-400 text-sm">Your data is encrypted and never shared</p>
                    </div>
                </div>

                {/* Import Options */}
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 md:p-8 border border-white/20">
                    <h2 className="text-xl font-semibold text-white mb-6 text-center">
                        Choose how to import your transactions
                    </h2>

                    {/* Error/Success Messages */}
                    {error && (
                        <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-xl flex items-center gap-3">
                            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                            <p className="text-red-300">{error}</p>
                        </div>
                    )}
                    {success && (
                        <div className="mb-6 p-4 bg-green-500/20 border border-green-500/50 rounded-xl flex items-center gap-3">
                            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                            <p className="text-green-300">{success}</p>
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* CSV Upload Option */}
                        <div
                            className={`relative p-6 rounded-xl border-2 transition-all cursor-pointer ${selectedMethod === 'csv'
                                    ? 'border-purple-500 bg-purple-500/10'
                                    : 'border-white/20 bg-white/5 hover:border-purple-500/50 hover:bg-white/10'
                                }`}
                            onClick={() => setSelectedMethod('csv')}
                        >
                            <div className="flex items-start gap-4">
                                <div className={`p-3 rounded-xl ${selectedMethod === 'csv' ? 'bg-purple-500' : 'bg-white/10'}`}>
                                    <FileSpreadsheet className={`w-6 h-6 ${selectedMethod === 'csv' ? 'text-white' : 'text-purple-400'}`} />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-white font-semibold mb-1">Upload CSV File</h3>
                                    <p className="text-gray-400 text-sm mb-4">
                                        Export transactions from your bank and upload the CSV file
                                    </p>

                                    {selectedMethod === 'csv' && (
                                        <div className="space-y-3">
                                            <input
                                                ref={fileInputRef}
                                                type="file"
                                                accept=".csv"
                                                onChange={handleCsvUpload}
                                                className="hidden"
                                            />
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    fileInputRef.current?.click();
                                                }}
                                                disabled={uploading}
                                                className="w-full py-3 px-4 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                                            >
                                                {uploading ? (
                                                    <>
                                                        <Loader2 className="w-5 h-5 animate-spin" />
                                                        Uploading...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Upload className="w-5 h-5" />
                                                        Select CSV File
                                                    </>
                                                )}
                                            </button>
                                            {fileName && !uploading && (
                                                <p className="text-sm text-gray-400 text-center">{fileName}</p>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                            {selectedMethod === 'csv' && (
                                <div className="absolute top-3 right-3">
                                    <CheckCircle className="w-5 h-5 text-purple-400" />
                                </div>
                            )}
                        </div>

                        {/* Email Sync Option */}
                        <div
                            className={`relative p-6 rounded-xl border-2 transition-all cursor-pointer ${selectedMethod === 'email'
                                    ? 'border-purple-500 bg-purple-500/10'
                                    : 'border-white/20 bg-white/5 hover:border-purple-500/50 hover:bg-white/10'
                                }`}
                            onClick={() => setSelectedMethod('email')}
                        >
                            <div className="flex items-start gap-4">
                                <div className={`p-3 rounded-xl ${selectedMethod === 'email' ? 'bg-purple-500' : 'bg-white/10'}`}>
                                    <Mail className={`w-6 h-6 ${selectedMethod === 'email' ? 'text-white' : 'text-purple-400'}`} />
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-white font-semibold mb-1">Connect Email</h3>
                                    <p className="text-gray-400 text-sm mb-4">
                                        Automatically import transactions from bank email alerts
                                    </p>

                                    {selectedMethod === 'email' && (
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                handleEmailSync();
                                            }}
                                            disabled={syncing}
                                            className="w-full py-3 px-4 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                                        >
                                            {syncing ? (
                                                <>
                                                    <Loader2 className="w-5 h-5 animate-spin" />
                                                    Connecting...
                                                </>
                                            ) : (
                                                <>
                                                    <Mail className="w-5 h-5" />
                                                    Connect with Google
                                                </>
                                            )}
                                        </button>
                                    )}
                                </div>
                            </div>
                            {selectedMethod === 'email' && (
                                <div className="absolute top-3 right-3">
                                    <CheckCircle className="w-5 h-5 text-purple-400" />
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Skip Option */}
                    <div className="mt-8 text-center">
                        <button
                            onClick={handleSkip}
                            className="text-gray-400 hover:text-white text-sm transition-colors flex items-center gap-1 mx-auto"
                        >
                            Skip for now, I'll add transactions later
                            <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Footer */}
                <p className="text-center text-gray-500 text-sm mt-6">
                    Your data is encrypted and stored securely. We never share your information.
                </p>
            </div>
        </div>
    );
};

export default Onboarding;
