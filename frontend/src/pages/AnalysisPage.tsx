import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { api, authService } from '@/services/api';
import { LogOut, User as UserIcon, Zap } from 'lucide-react';
import type { DateRangeOption } from '@/components/DataImport';
import { Dashboard } from '@/components/Dashboard';
import { ShieldAlert, Lock, CheckCircle2 } from 'lucide-react';
import { DataImport } from '@/components/DataImport';

export default function App() {
    const [data, setData] = useState<any>(null);
    const [uploadedData, setUploadedData] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [showPasswordInput, setShowPasswordInput] = useState(false);
    const [fileToRetry, setFileToRetry] = useState<File | null>(null);
    const [password, setPassword] = useState("");
    const [userName, setUserName] = useState<string | null>(null);
    const navigate = useNavigate();
    const location = useLocation();

    useEffect(() => {
        const fetchUser = async () => {
            try {
                const user = await authService.getCurrentUser();
                setUserName(user.username || user.email.split('@')[0]);
            } catch (error) {
                console.error("Failed to fetch user", error);
            }
        };
        fetchUser();
    }, []);

    // Fetch latest analysis on mount to restore dashboard on refresh
    useEffect(() => {
        const fetchLatestAnalysis = async () => {
            try {
                const token = localStorage.getItem('auth_token');
                if (!token) return;

                const response = await fetch('http://localhost:8000/api/leaks/latest', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const result = await response.json();
                    // Only set data if leaks exist
                    if (result.leaks && result.leaks.length > 0) {
                        setData(result);
                        console.log('Latest analysis restored:', result);
                    }
                }
            } catch (error) {
                console.error("Failed to fetch latest analysis:", error);
            }
        };

        fetchLatestAnalysis();
    }, []);

    const handleLogout = async () => {
        try {
            await authService.logout();
            navigate('/login');
        } catch (error) {
            console.error("Logout failed", error);
            // Force logout on error
            localStorage.removeItem('auth_token');
            navigate('/login');
        }
    };

    // Handle OAuth callback tokens from URL (after Google redirect)
    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const oauthSuccess = urlParams.get('oauth_success');
        const accessToken = urlParams.get('access_token');
        const refreshToken = urlParams.get('refresh_token');
        const email = urlParams.get('email');
        const error = urlParams.get('error');

        if (error) {
            alert(`OAuth Error: ${error}`);
            // Clean up URL
            window.history.replaceState({}, '', window.location.pathname);
            return;
        }

        if (oauthSuccess && accessToken) {
            console.log(`OAuth successful for ${email}`);
            // Get date range from sessionStorage (stored before OAuth redirect)
            const storedDateRange = sessionStorage.getItem('email_date_range') as DateRangeOption || '30_days';
            sessionStorage.removeItem('email_date_range'); // Clean up

            // Trigger email scraping with the access token and date range
            handleEmailScrape({ token: accessToken, refresh_token: refreshToken, email }, storedDateRange);
            // Clean up URL
            window.history.replaceState({}, '', window.location.pathname);
        }
    }, []);

    const handleEmailScrape = async (
        tokenInfo: { token: string; refresh_token?: string | null; email?: string | null },
        dateRange: DateRangeOption = '30_days'
    ) => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/scrape-emails', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ...tokenInfo,
                    date_range: dateRange
                }),
            });
            const result = await response.json();
            if (result.leaks || result.transactions) {
                setData({
                    summary: {
                        total_spend: result.transactions?.reduce((acc: number, t: any) => acc + t.amount, 0) || 0,
                        transaction_count: result.count || 0,
                    },
                    leaks: result.leaks || [],
                    ai_insights: result.ai_insights || "Email analysis complete. Check leaks for details.",
                    raw_data_preview: result.transactions || []
                });
            }
        } catch (error) {
            console.error("Email scraping failed:", error);
            alert("Failed to scrape emails. Check console for details.");
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (file: File, filePassword?: string) => {
        setLoading(true);
        const formData = new FormData();
        formData.append('file', file);
        if (filePassword) {
            formData.append('password', filePassword);
        }

        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                throw new Error('Not authenticated. Please login again.');
            }

            const response = await fetch('http://localhost:8000/api/transactions/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData,
            });

            if (response.status === 423) {
                setFileToRetry(file);
                setShowPasswordInput(true);
                setLoading(false);
                return;
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                console.error('Upload error response:', response.status, errorData);
                throw new Error(errorData?.detail || `Error: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Upload successful:', result);
            
            // Store upload data but don't analyze yet
            setUploadedData(result);
            setShowPasswordInput(false);
            setFileToRetry(null);
            setPassword("");
        } catch (error) {
            console.error("Error uploading file:", error);
            alert(error instanceof Error ? error.message : "Failed to upload file. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    const analyzeForLeaks = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                throw new Error('Not authenticated. Please login again.');
            }

            const response = await fetch('http://localhost:8000/api/leaks/analyze', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                console.error('Analyze error response:', response.status, errorData);
                throw new Error(errorData?.detail || `Error: ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Analysis successful:', result);
            
            // Combine upload data with analysis results
            setData({
                ...uploadedData,
                ...result
            });
        } catch (error) {
            console.error("Error analyzing file:", error);
            alert(error instanceof Error ? error.message : "Failed to analyze file. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handlePasswordSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (fileToRetry && password) {
            handleUpload(fileToRetry, password);
        }
    };


    return (
        <div className="min-h-screen bg-background text-slate-100 selection:bg-primary/30">
            {/* Background Gradients */}
            <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 blur-[100px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-accent/20 blur-[100px] rounded-full" />
            </div>

            {/* Password Modal */}
            {showPasswordInput && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
                    <div className="bg-surface border border-slate-700 p-6 rounded-2xl w-full max-w-md shadow-2xl animate-in zoom-in-95">
                        <div className="flex items-center gap-3 mb-4 text-warning">
                            <Lock className="w-6 h-6 text-yellow-500" />
                            <h3 className="text-xl font-bold text-white">File Locked</h3>
                        </div>
                        <p className="text-slate-400 mb-6">This PDF is password protected. Please enter the password to unlock and analyze.</p>

                        <form onSubmit={handlePasswordSubmit} className="space-y-4">
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-background border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary placeholder:text-slate-600"
                                placeholder="Enter PDF password"
                                autoFocus
                            />
                            <div className="flex justify-end gap-3">
                                <button
                                    type="button"
                                    onClick={() => { setShowPasswordInput(false); setFileToRetry(null); }}
                                    className="px-4 py-2 text-slate-400 hover:text-white transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-6 py-2 bg-primary hover:bg-primary/90 text-white rounded-lg font-medium transition-colors"
                                >
                                    Unlock & Analyze
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
                {/* Header */}
                <header className="flex items-center justify-between mb-16">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-gradient-to-tr from-primary to-accent rounded-xl shadow-lg shadow-primary/20">
                            <ShieldAlert className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
                                LeakDetector
                            </h1>
                            <p className="text-xs text-slate-500 font-medium tracking-wide">FINANCIAL INSIGHTS</p>
                        </div>
                    </div>

                    {userName && (
                        <div className="flex items-center gap-4">
                            <div className="flex items-center gap-2 text-slate-300 bg-surface/50 px-3 py-1.5 rounded-full border border-white/10">
                                <UserIcon className="w-4 h-4" />
                                <span className="text-sm font-medium">{userName}</span>
                            </div>
                            <button
                                onClick={handleLogout}
                                className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-full transition-colors"
                                title="Logout"
                            >
                                <LogOut className="w-5 h-5" />
                            </button>
                        </div>
                    )}
                </header>

                {/* content */}
                <main className="transition-all duration-500">
                    {!data && !uploadedData ? (
                        <div className="flex flex-col items-center justify-center min-h-[60vh] animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <div className="text-center mb-10 space-y-4">
                                <h2 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-6">
                                    Stop the <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">Financial Bleeding</span>
                                </h2>
                                <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
                                    Upload your bank statement or connect your email to detect hidden subscriptions,
                                    recurring charges, and spending patterns.
                                </p>
                            </div>

                            <DataImport
                                onFileUpload={handleUpload}
                                onEmailConnect={(tokenResponse, dateRange) => handleEmailScrape(tokenResponse, dateRange)}
                                isLoading={loading}
                                isGoogleConfigured={true}
                            />
                        </div>
                    ) : uploadedData && !data ? (
                        <div className="flex flex-col items-center justify-center min-h-[60vh] animate-in fade-in slide-in-from-bottom-4 duration-700">
                            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 md:p-12 border border-white/20 max-w-md w-full space-y-6">
                                {/* Success Icon */}
                                <div className="flex justify-center">
                                    <div className="p-4 bg-green-500/20 rounded-full">
                                        <CheckCircle2 className="w-12 h-12 text-green-400" />
                                    </div>
                                </div>

                                {/* Success Message */}
                                <div className="text-center space-y-2">
                                    <h3 className="text-2xl font-bold text-white">File Uploaded Successfully! ✨</h3>
                                    <p className="text-slate-400 text-sm">
                                        {uploadedData.statistics?.transactions_stored || 0} transactions found and processed
                                    </p>
                                </div>

                                {/* Stats Preview */}
                                <div className="bg-white/5 rounded-xl p-4 space-y-3">
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-400 text-sm">Patterns Detected:</span>
                                        <span className="text-white font-semibold">{uploadedData.statistics?.pattern_stats_stored || 0}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-400 text-sm">Invalid Rows:</span>
                                        <span className="text-white font-semibold">{uploadedData.statistics?.invalid_rows || 0}</span>
                                    </div>
                                </div>

                                {/* Action Buttons */}
                                <div className="flex gap-3 pt-4">
                                    <button
                                        onClick={() => {
                                            setUploadedData(null);
                                        }}
                                        className="flex-1 py-2.5 px-4 bg-white/10 hover:bg-white/20 text-white rounded-lg font-medium transition-colors"
                                        disabled={loading}
                                    >
                                        Upload Different File
                                    </button>
                                    <button
                                        onClick={analyzeForLeaks}
                                        disabled={loading}
                                        className="flex-1 py-2.5 px-4 bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white rounded-lg font-medium transition-all disabled:opacity-60 flex items-center justify-center gap-2"
                                    >
                                        {loading ? (
                                            <>
                                                <span className="animate-spin">⏳</span>
                                                Analyzing...
                                            </>
                                        ) : (
                                            <>
                                                <Zap className="w-4 h-4" />
                                                Detect Leaks
                                            </>
                                        )}
                                    </button>
                                </div>

                                <p className="text-xs text-slate-500 text-center">
                                    Click "Detect Leaks" to analyze spending patterns and find hidden subscriptions
                                </p>
                            </div>
                        </div>
                    ) : data ? (
                        <Dashboard data={data} onReset={() => { setData(null); setUploadedData(null); }} />
                    ) : null}
                </main>
            </div>
        </div>
    );
}
