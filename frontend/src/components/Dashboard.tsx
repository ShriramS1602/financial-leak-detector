import { ArrowLeft, DollarSign, Activity, Banknote, TrendingUp, AlertCircle, X, ChevronDown, RotateCcw, ShieldAlert } from 'lucide-react';
import { cn, formatCurrency, formatCurrencyDetailed } from '../lib/utils';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { useState } from 'react';

interface DashboardProps {
    data: any;
    onReset: () => void;
}

export function Dashboard({ data, onReset }: DashboardProps) {
    // Handle both old and new response formats
    const summary = data.statistics || { total_spend: 0, transaction_count: 0 };
    const leaks = (data.leaks || []).sort((a: any, b: any) =>
        (b.leak_probability || 0) - (a.leak_probability || 0)
    );
    const total_saving = data.total_estimated_annual_saving || 0;

    // Filter state - start with no filters selected
    const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
    const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set());
    const [detailsModal, setDetailsModal] = useState<{ index: number; merchant: string } | null>(null);
    const [detailsTransactions, setDetailsTransactions] = useState<any[]>([]);
    const [loadingDetails, setLoadingDetails] = useState(false);

    // Get unique categories with counts
    const categoryMap = leaks.reduce((acc: any, leak: any) => {
        const category = leak.leak_category || 'Other';
        acc[category] = (acc[category] || 0) + 1;
        return acc;
    }, {});

    // Filter leaks based on selected categories
    const filteredLeaks = leaks.filter((leak: any) =>
        selectedCategories.length === 0 || selectedCategories.includes(leak.leak_category || 'Other')
    );

    // Toggle category selection
    const toggleCategory = (category: string) => {
        setSelectedCategories((prev) =>
            prev.includes(category)
                ? prev.filter((c) => c !== category)
                : [...prev, category]
        );
    };

    // Exclusive selection for chart click
    const selectCategoryExclusive = (category: string) => {
        setSelectedCategories([category]);
    };

    // Select/deselect all
    const selectAll = () => {
        setSelectedCategories([]);
    };

    // Calculate confidence distribution
    const confidenceDistribution = {
        high: leaks.filter((l: any) => (l.leak_probability || 0) > 0.7).length,
        medium: leaks.filter((l: any) => (l.leak_probability || 0) >= 0.4 && (l.leak_probability || 0) <= 0.7).length,
        low: leaks.filter((l: any) => (l.leak_probability || 0) < 0.4).length,
    };

    // Toggle card expansion
    const toggleCardExpansion = (index: number) => {
        const newExpanded = new Set(expandedCards);
        if (newExpanded.has(index)) {
            newExpanded.delete(index);
        } else {
            newExpanded.add(index);
        }
        setExpandedCards(newExpanded);
    };

    // Open details modal
    const openDetailsModal = async (index: number, merchant: string) => {
        console.log('=== OPENING DETAILS MODAL ===');
        console.log('Index:', index);
        console.log('Merchant:', merchant);
        console.log('Full leak data:', filteredLeaks[index]);
        
        setDetailsModal({ index, merchant });
        setLoadingDetails(true);
        try {
            // Get token from localStorage - try both keys
            const token = localStorage.getItem('auth_token') || localStorage.getItem('access_token');
            
            console.log('Token exists:', !!token);
            console.log('Token value:', token?.substring(0, 20) + '...' || 'none');
            
            if (!token) {
                console.error('No auth_token or access_token found in localStorage');
                setDetailsTransactions([]);
                setLoadingDetails(false);
                return;
            }

            console.log('Fetching transactions with token...');
            
            // Fetch all transactions for this user
            const response = await fetch('/api/transactions/raw-transactions?limit=1000', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });
            
            console.log('Response status:', response.status);
            
            if (response.status === 401) {
                console.error('Authentication failed (401). Token may be expired.');
                // Clear tokens and redirect to login
                localStorage.removeItem('auth_token');
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return;
            }
            
            if (!response.ok) {
                console.error('Failed to fetch transactions:', response.statusText);
                setDetailsTransactions([]);
                setLoadingDetails(false);
                return;
            }
            
            const data = await response.json();
            
            console.log('API Response:', data);
            console.log('Total transactions received:', data.transactions?.length || 0);
            
            if (data.transactions && data.transactions.length > 0) {
                console.log('Sample transaction:', JSON.stringify(data.transactions[0], null, 2));
            }
            
            // Filter by merchant hint - try multiple matching strategies
            const merchantTransactions = (data.transactions || []).filter((t: any) => {
                const txnMerchant = t.merchant || t.merchant_hint || '';
                const merchantLower = merchant.toLowerCase();
                const txnMerchantLower = txnMerchant.toLowerCase();

                const matches = txnMerchantLower.includes(merchantLower) ||
                    merchantLower.includes(txnMerchantLower) ||
                    txnMerchantLower === merchantLower;

                if (matches) {
                    console.log('✓ Matched transaction:', txnMerchant);
                }
                
                return matches;
            });
            
            console.log('Filtered transactions count:', merchantTransactions.length);
            console.log('Filtered transactions:', merchantTransactions);
            setDetailsTransactions(merchantTransactions);
        } catch (error) {
            console.error('Exception in openDetailsModal:', error);
            setDetailsTransactions([]);
        } finally {
            setLoadingDetails(false);
        }
    };

    // Close details modal
    const closeDetailsModal = () => {
        setDetailsModal(null);
        setDetailsTransactions([]);
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
            <button
                onClick={onReset}
                className="flex items-center gap-2 text-sm text-slate-400 hover:text-primary transition-colors mb-4 group"
            >
                <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                Back to Upload
            </button>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div title={formatCurrencyDetailed(summary.total_spend || 0)}>
                    <StatsCard
                        title="Total Spend"
                        value={formatCurrency(summary.total_spend || 0)}
                        icon={<DollarSign className="w-5 h-5" />}
                        trend={`${leaks.length} leaks detected`}
                        color="primary"
                    />
                </div>
                <StatsCard
                    title="Transactions"
                    value={summary.transaction_count || 0}
                    icon={<Activity className="w-5 h-5" />}
                    trend="Patterns analyzed"
                    color="accent"
                />
                <div title={formatCurrencyDetailed(total_saving)}>
                    <StatsCard
                        title="Potential Savings"
                        value={formatCurrency(total_saving)}
                        icon={<Banknote className="w-5 h-5" />}
                        trend="Annual estimate"
                        color="success"
                    />
                </div>
            </div>

            {/* Leak Categories Breakdown - Donut Chart (Full Width) */}
            {leaks.length > 0 && (
                <div className="bg-surface/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-xl font-bold text-slate-200 flex items-center gap-2">
                            <AlertCircle className="w-5 h-5 text-primary" />
                            Leak Categories Breakdown
                        </h3>

                        {selectedCategories.length > 0 && (
                            <button
                                onClick={selectAll}
                                className="flex items-center gap-1.5 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-full transition-all border border-slate-700 animate-in fade-in zoom-in duration-200"
                            >
                                <RotateCcw className="w-3.5 h-3.5" />
                                Reset View
                            </button>
                        )}
                    </div>
                    <LeakCategoryChart
                        leaks={leaks}
                        onCategoryClick={selectCategoryExclusive}
                        selectedCategory={selectedCategories.length > 0 ? selectedCategories[0] : null}
                    />
                </div>
            )}

            {/* Confidence Distribution */}
            {leaks.length > 0 && (
                <div className="bg-surface/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
                    <h3 className="text-xl font-bold text-slate-200 mb-6 flex items-center gap-2">
                        <ShieldAlert className="w-5 h-5 text-primary" />
                        Leak Detection Confidence
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* High Confidence */}
                        <div className="bg-slate-800/50 rounded-xl border border-emerald-500/30 p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-emerald-400 font-semibold">High Confidence</span>
                                <span className="text-2xl font-bold text-emerald-400">{confidenceDistribution.high}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-emerald-500" 
                                        style={{ width: `${leaks.length > 0 ? (confidenceDistribution.high / leaks.length) * 100 : 0}%` }}
                                    />
                                </div>
                                <span className="text-sm text-slate-400 min-w-fit">
                                    {leaks.length > 0 ? ((confidenceDistribution.high / leaks.length) * 100).toFixed(0) : 0}%
                                </span>
                            </div>
                            <p className="text-xs text-slate-500 mt-2">Probability &gt; 0.7</p>
                        </div>

                        {/* Medium Confidence */}
                        <div className="bg-slate-800/50 rounded-xl border border-amber-500/30 p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-amber-400 font-semibold">Medium Confidence</span>
                                <span className="text-2xl font-bold text-amber-400">{confidenceDistribution.medium}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-amber-500" 
                                        style={{ width: `${leaks.length > 0 ? (confidenceDistribution.medium / leaks.length) * 100 : 0}%` }}
                                    />
                                </div>
                                <span className="text-sm text-slate-400 min-w-fit">
                                    {leaks.length > 0 ? ((confidenceDistribution.medium / leaks.length) * 100).toFixed(0) : 0}%
                                </span>
                            </div>
                            <p className="text-xs text-slate-500 mt-2">Probability 0.4 - 0.7</p>
                        </div>

                        {/* Low Confidence */}
                        <div className="bg-slate-800/50 rounded-xl border border-red-500/30 p-4">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-red-400 font-semibold">Low Confidence</span>
                                <span className="text-2xl font-bold text-red-400">{confidenceDistribution.low}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                                    <div 
                                        className="h-full bg-red-500" 
                                        style={{ width: `${leaks.length > 0 ? (confidenceDistribution.low / leaks.length) * 100 : 0}%` }}
                                    />
                                </div>
                                <span className="text-sm text-slate-400 min-w-fit">
                                    {leaks.length > 0 ? ((confidenceDistribution.low / leaks.length) * 100).toFixed(0) : 0}%
                                </span>
                            </div>
                            <p className="text-xs text-slate-500 mt-2">Probability &lt; 0.4</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Detected Leaks - Full Width with Scroll */}
            <div className="bg-surface/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-slate-200 mb-6 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-danger" />
                    Detected Leaks ({filteredLeaks.length} of {leaks.length})
                </h3>

                {/* Category Filter Buttons - Redesigned as scrollable pills */}
                {leaks.length > 0 && (
                    <div className="mb-6 pb-4 border-b border-slate-700/50">
                        <div className="flex flex-wrap gap-2 items-center">
                            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider mr-2">Filter by:</span>
                            <button
                                onClick={selectAll}
                                className={cn(
                                    "px-4 py-1.5 rounded-full text-xs font-bold transition-all shadow-sm border",
                                    selectedCategories.length === 0
                                        ? "bg-primary text-primary-foreground border-primary shadow-primary/25 shadow-md scale-105"
                                        : "bg-slate-800/50 text-slate-400 border-slate-700 hover:border-slate-600 hover:bg-slate-800"
                                )}
                            >
                                All
                            </button>
                            
                            {Object.entries(categoryMap).map(([category, count]) => {
                                const isSelected = selectedCategories.includes(category);
                                const formatted = category
                                    .replace(/_/g, ' ')
                                    .split(' ')
                                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                                    .join(' ');
                                
                                return (
                                    <button
                                        key={category}
                                        onClick={() => toggleCategory(category)}
                                        className={cn(
                                            "px-4 py-1.5 rounded-full text-xs font-medium transition-all border flex items-center gap-1.5",
                                            isSelected
                                                ? "bg-slate-100 text-slate-900 border-slate-200 shadow-md scale-105"
                                                : "bg-slate-800/30 text-slate-400 border-slate-700/50 hover:bg-slate-800/50 hover:border-slate-600"
                                        )}
                                    >
                                        <div className={cn("w-1.5 h-1.5 rounded-full", isSelected ? "bg-primary" : "bg-slate-500")} />
                                        {formatted}
                                        <span className="opacity-50 text-[10px] ml-0.5">({count as number})</span>
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                )}

                <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                    {filteredLeaks.length === 0 ? (
                        <div className="text-slate-500 text-center py-10">
                            {leaks.length === 0 ? "No leaks detected! Great job." : "No leaks in selected categories."}
                        </div>
                    ) : (
                        [...filteredLeaks].sort((a: any, b: any) => (b.leak_probability || 0) - (a.leak_probability || 0)).map((leak: any, i: number) => {
                            const isExpanded = expandedCards.has(i);
                            return (
                                <div key={i} className="bg-slate-800/50 rounded-xl border border-slate-700 hover:border-danger/30 transition-colors overflow-hidden">
                                    {/* Clickable Header - Merchant & Savings */}
                                    <button
                                        onClick={() => toggleCardExpansion(i)}
                                        className="w-full p-4 flex items-center justify-between hover:bg-slate-800/70 transition-colors text-left"
                                    >
                                        <div className="flex items-center gap-3 flex-1 min-w-0">
                                            <div className="p-2 bg-danger/10 rounded-lg text-danger flex-shrink-0">
                                                {leak.leak_category === 'subscription' ? <Activity className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="text-xs text-slate-400 mb-1">
                                                    {/* DEBUG: Log the tags */}
                                                    {console.log('Leak data:', { 
                                                        merchant: leak.merchant_hint,
                                                        level_1: leak.dominant_level_1_tag,
                                                        level_2: leak.dominant_level_2_tag
                                                    })}
                                                    {leak.dominant_level_1_tag && leak.dominant_level_2_tag 
                                                        ? `${leak.dominant_level_1_tag} - ${leak.dominant_level_2_tag}` 
                                                        : leak.dominant_level_1_tag 
                                                        ? leak.dominant_level_1_tag 
                                                        : 'Uncategorized'}
                                                </div>
                                                <h4 className="font-bold text-base text-slate-100 truncate">
                                                    {(leak.merchant_hint || 'Unknown Merchant')
                                                        .split(' ')
                                                        .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                                                        .join(' ')}
                                                </h4>
                                                <p className="text-xs text-slate-400 mt-1">
                                                    {(leak.leak_probability * 100).toFixed(0)}% Confidence
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-3 flex-shrink-0 ml-4">
                                            <div className="text-right">
                                                <div className="text-lg font-bold text-green-400">₹{(leak.estimated_annual_saving || 0).toFixed(0)}</div>
                                                <div className="text-xs text-slate-500">Savings</div>
                                            </div>
                                            <ChevronDown 
                                                className={`w-5 h-5 text-slate-400 transition-transform flex-shrink-0 ${isExpanded ? 'rotate-180' : ''}`}
                                            />
                                        </div>
                                    </button>

                                    {/* Expanded Details - Conditional Rendering */}
                                    {isExpanded && (
                                        <>
                                            {/* Category & Tags Section */}
                                            <div className="px-4 py-3 border-t border-slate-700/50 bg-slate-900/30">
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <p className="text-xs text-slate-500 font-medium mb-2">Leak Category</p>
                                                        <div className="inline-flex items-center px-3 py-1 rounded-full bg-gradient-to-r from-slate-800 to-slate-900 border border-slate-700/50 shadow-sm">
                                                            <div className="w-2 h-2 rounded-full bg-indigo-500 mr-2 animate-pulse"></div>
                                                            <p className="text-sm font-bold text-slate-100 capitalize tracking-wide">
                                                                {(leak.leak_category || 'Other')
                                                                    .replace(/_/g, ' ')
                                                                    .split(' ')
                                                                    .map((word: string) => word.charAt(0).toUpperCase() + word.slice(1))
                                                                    .join(' ')}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs text-slate-500 font-medium mb-1">Frequency</p>
                                                        <p className="text-sm font-semibold text-slate-200">
                                                            Every {leak.avg_frequency_days ? Math.round(leak.avg_frequency_days) : '?'} days
                                                        </p>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Transaction Stats Section */}
                                            {leak.total_spent && (
                                                <div className="px-4 py-3 border-t border-slate-700/50 bg-slate-900/20">
                                                    <p className="text-xs text-slate-500 font-medium mb-3">Transaction Details</p>
                                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                                                        <div className="bg-slate-800/50 p-2.5 rounded-lg">
                                                            <p className="text-xs text-slate-500 mb-1">Total Spent</p>
                                                            <p className="font-bold text-slate-200">₹{(leak.total_spent || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                                                        </div>
                                                        <div className="bg-slate-800/50 p-2.5 rounded-lg">
                                                            <p className="text-xs text-slate-500 mb-1">Avg/Month</p>
                                                            <p className="font-bold text-slate-200">
                                                                ₹{(leak.active_duration_days ? (leak.total_spent / (leak.active_duration_days / 30)) : 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                                                            </p>
                                                        </div>
                                                        <div className="bg-slate-800/50 p-2.5 rounded-lg">
                                                            <p className="text-xs text-slate-500 mb-1">Avg/Transaction</p>
                                                            <p className="font-bold text-slate-200">₹{(leak.avg_per_transaction || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</p>
                                                        </div>
                                                        <div className="bg-slate-800/50 p-2.5 rounded-lg">
                                                            <p className="text-xs text-slate-500 mb-1">Count</p>
                                                            <p className="font-bold text-slate-200">{leak.transaction_count || 0}</p>
                                                        </div>
                                                    </div>
                                                    <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                                                        <div className="bg-slate-800/50 p-2.5 rounded-lg">
                                                            <p className="text-xs text-slate-500 mb-1">Duration</p>
                                                            <p className="font-bold text-slate-200">
                                                                {leak.active_duration_days ? Math.round(leak.active_duration_days / 30) : '?'} months
                                                            </p>
                                                        </div>
                                                        <div className="bg-slate-800/50 p-2.5 rounded-lg">
                                                            <p className="text-xs text-slate-500 mb-1">Last Transaction</p>
                                                            <p className="font-bold text-slate-200">{leak.last_transaction_days_ago || 0} days ago</p>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Reasoning Section */}
                                            <div className="px-4 py-3 border-t border-slate-700/50 bg-slate-900/10">
                                                <p className="text-xs text-slate-500 font-medium mb-2">Why We Flagged This</p>
                                                <p className="text-sm text-slate-300 leading-relaxed">{leak.reasoning || 'No reasoning provided'}</p>
                                            </div>

                                            {/* Actionable Step Section */}
                                            <div className="px-4 py-3 border-t border-slate-700/50 bg-slate-900/20">
                                                <div className="flex items-start gap-3">
                                                    <div className="text-lg mt-0.5">💡</div>
                                                    <div className="flex-1">
                                                        <p className="text-xs text-slate-500 font-medium mb-1">What You Can Do</p>
                                                        <p className="text-sm text-slate-300">{leak.actionable_step || 'No action suggested'}</p>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* Action Buttons - Footer */}
                                            <div className="px-4 py-3 flex gap-2 bg-slate-900/40 border-t border-slate-700/50">
                                                <button 
                                                    onClick={() => openDetailsModal(i, leak.merchant_hint || 'Unknown')}
                                                    className="w-full px-3 py-2 text-sm font-medium bg-slate-700/30 text-slate-300 rounded-lg hover:bg-slate-700/50 transition-colors border border-slate-600/30">
                                                    More Details
                                                </button>
                                            </div>
                                        </>
                                    )}
                                </div>
                            );
                        })
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Col: Leaks List - REMOVED, now full width above */}
                <div className="lg:col-span-2 space-y-6">
                </div>

                {/* Right Col: AI Insights - DISABLED */}
                {/* <div className="lg:col-span-1">
                    <div className="sticky top-8 bg-gradient-to-b from-surface/80 to-surface/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl shadow-primary/5">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="p-2 bg-gradient-to-br from-primary to-accent rounded-lg">
                                <ShieldAlert className="w-5 h-5 text-white" />
                            </div>
                            <h3 className="text-xl font-bold text-white">Gemini Insights</h3>
                        </div>

                        <div className="prose prose-invert prose-sm max-w-none text-slate-300">
                            <ReactMarkdown>{ai_insights || "No insights available."}</ReactMarkdown>
                        </div>
                    </div>
                </div> */}
            </div>

            {/* Transaction Details Modal */}
            {detailsModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[80vh] overflow-hidden flex flex-col">
                        {/* Modal Header */}
                        <div className="p-6 border-b border-slate-700 flex items-center justify-between bg-slate-800/50">
                            <div>
                                <h2 className="text-2xl font-bold text-slate-100">Transaction History</h2>
                                <p className="text-slate-400 text-sm mt-1">{detailsModal.merchant}</p>
                            </div>
                            <button
                                onClick={closeDetailsModal}
                                className="p-2 hover:bg-slate-700/50 rounded-lg transition-colors"
                            >
                                <X className="w-6 h-6 text-slate-400" />
                            </button>
                        </div>

                        {/* Modal Content */}
                        <div className="flex-1 overflow-y-auto">
                            {loadingDetails ? (
                                <div className="p-8 text-center text-slate-400">
                                    Loading transactions...
                                </div>
                            ) : detailsTransactions.length === 0 ? (
                                <div className="p-8 text-center">
                                    <p className="text-slate-400">No transactions found for this merchant.</p>
                                    <p className="text-xs text-slate-500 mt-2">Check browser console for debugging info.</p>
                                </div>
                            ) : (
                                <div className="p-6">
                                    {/* Table View */}
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm">
                                            <thead>
                                                <tr className="border-b border-slate-700">
                                                    <th className="text-left py-3 px-4 font-semibold text-slate-300">Date</th>
                                                    <th className="text-left py-3 px-4 font-semibold text-slate-300">Narration</th>
                                                    <th className="text-right py-3 px-4 font-semibold text-slate-300">Amount</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {detailsTransactions.map((txn: any, idx: number) => (
                                                    <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-800/50 transition-colors">
                                                        <td className="py-3 px-4 text-slate-400 whitespace-nowrap">
                                                            {new Date(txn.txn_date).toLocaleDateString('en-IN')}
                                                        </td>
                                                        <td className="py-3 px-4 text-slate-300">
                                                            {txn.narration || txn.description || txn.notes || txn.merchant || '-'}
                                                        </td>
                                                        <td className="py-3 px-4 text-right text-slate-200 font-semibold whitespace-nowrap">
                                                            ₹{(txn.withdrawal_amount || txn.deposit_amount || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                    
                                    {/* Summary Footer */}
                                    <div className="mt-6 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-xs text-slate-500 mb-1">Total Transactions</p>
                                                <p className="text-lg font-bold text-slate-200">{detailsTransactions.length}</p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-slate-500 mb-1">Total Amount</p>
                                                <p className="text-lg font-bold text-slate-200">
                                                    ₹{detailsTransactions.reduce((sum: number, t: any) => sum + (t.withdrawal_amount || t.deposit_amount || 0), 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Modal Footer */}
                        <div className="p-4 border-t border-slate-700 bg-slate-800/50 flex justify-end">
                            <button
                                onClick={closeDetailsModal}
                                className="px-6 py-2 bg-slate-700/50 text-slate-300 rounded-lg hover:bg-slate-700 transition-colors font-medium"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

function StatsCard({ title, value, icon, trend, color }: any) {
    const colorMap: any = {
        primary: 'text-primary bg-primary/10 border-primary/20',
        accent: 'text-accent bg-accent/10 border-accent/20',
        danger: 'text-danger bg-danger/10 border-danger/20',
        success: 'text-green-400 bg-green-400/10 border-green-400/20',
    };

    return (
        <div className="bg-surface/50 backdrop-blur-sm border border-slate-700/50 hover:border-slate-600 p-6 rounded-2xl transition-all duration-300 hover:shadow-lg hover:shadow-primary/5">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <p className="text-slate-400 text-sm font-medium mb-1">{title}</p>
                    <h3 className="text-3xl font-bold text-white">{value}</h3>
                </div>
                <div className={cn("p-3 rounded-xl", colorMap[color])}>
                    {icon}
                </div>
            </div>
            <p className="text-xs text-slate-500 font-medium bg-slate-800/50 inline-block px-2 py-1 rounded-lg">
                {trend}
            </p>
        </div>
    );
}

interface LeakCategoryChartProps {
    leaks: any[];
    onCategoryClick?: (category: string) => void;
    selectedCategory?: string | null;
}

function LeakCategoryChart({ leaks, onCategoryClick, selectedCategory }: LeakCategoryChartProps) {
    // Group leaks by category
    const categoryMap = leaks.reduce((acc: any, leak: any) => {
        const category = leak.leak_category || 'Other';
        acc[category] = (acc[category] || 0) + 1;
        return acc;
    }, {});

    // Convert to chart data
    const chartData = Object.entries(categoryMap)
        .map(([name, value]) => {
            // Format category name
            const formatted = name
                .replace(/_/g, ' ')
                .split(' ')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ');

            return {
                name: formatted,
                originalName: name,
                value: value as number,
                percentage: ((value as number / leaks.length) * 100).toFixed(1),
            };
        })
        .sort((a, b) => b.value - a.value); // Sort by count descending

    // Calculate display stats for center of donut
    const selectedData = selectedCategory ? chartData.find(d => d.originalName === selectedCategory) : null;
    const centerCount = selectedData ? selectedData.value : leaks.length;
    const centerLabel = selectedData ? selectedData.name : "Total Leaks";

    // Extended Color palette
    const COLORS = [
        '#ef4444', '#f97316', '#eab308', '#22c55e', '#3b82f6', '#8b5cf6', '#ec4899',
        '#06b6d4', '#14b8a6', '#f43f5e', '#6366f1', '#a855f7', '#d946ef'
    ];

    return (
        <div className="flex flex-col lg:flex-row gap-8 items-start justify-center">
            {/* Donut Chart - Fixed Width */}
            <div className="w-full lg:w-5/12 h-[320px] relative flex-shrink-0">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={80}
                            outerRadius={120}
                            paddingAngle={3}
                            dataKey="value"
                            onClick={(entry: any) => {
                                if (onCategoryClick && entry.payload.originalName) {
                                    onCategoryClick(entry.payload.originalName);
                                }
                            }}
                            style={{ cursor: 'pointer', outline: 'none' }}
                            stroke="none"
                        >
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={COLORS[index % COLORS.length]}
                                    className="transition-all duration-300"
                                    opacity={selectedCategory && selectedCategory !== entry.originalName ? 0.3 : 1}
                                />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(15, 23, 42, 0.95)',
                                color: '#f8fafc',
                                borderRadius: '12px',
                                border: '1px solid rgba(51, 65, 85, 0.5)',
                                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
                                padding: '12px'
                            }}
                            itemStyle={{ color: '#fff' }}
                            formatter={(value: any, name: any) => [`${value} leaks`, name]}
                        />
                    </PieChart>
                </ResponsiveContainer>

                {/* Center Stats */}
                <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none transition-all duration-300">
                    <span
                        key={centerCount} // Animate on change
                        className="text-4xl font-bold text-white animate-in zoom-in-50 duration-300"
                    >
                        {centerCount}
                    </span>
                    <span className="text-xs text-slate-400 uppercase tracking-widest mt-1 text-center max-w-[120px] truncate px-2">
                        {centerLabel}
                    </span>
                </div>
            </div>

            {/* Legend - Grid (No Scroll) */}
            <div className="w-full lg:w-7/12">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {chartData.map((item, index) => {
                        const color = COLORS[index % COLORS.length];
                        const isSelected = selectedCategory === item.originalName;
                        const isDimmed = selectedCategory && !isSelected;

                        return (
                            <button
                                key={index}
                                onClick={() => onCategoryClick && onCategoryClick(item.originalName)}
                                className={cn(
                                    "group flex flex-col p-3 rounded-xl border transition-all duration-300 text-left relative overflow-hidden",
                                    isSelected
                                        ? "bg-slate-800 border-primary shadow-lg shadow-primary/10 scale-[1.02]"
                                        : "bg-slate-800/30 border-slate-700/30 hover:bg-slate-800 hover:border-slate-600",
                                    isDimmed ? "opacity-50 hover:opacity-100" : "opacity-100"
                                )}
                            >
                                <div className="flex items-center justify-between w-full mb-2">
                                    <div className="flex items-center gap-2.5 truncate pr-2">
                                        <div
                                            className="w-2.5 h-2.5 rounded-full flex-shrink-0 shadow-[0_0_8px] transition-shadow duration-300"
                                            style={{
                                                backgroundColor: color,
                                                boxShadow: `0 0 8px ${color}`
                                            }}
                                        />
                                        <span className={cn(
                                            "font-medium text-sm truncate transition-colors",
                                            isSelected ? "text-white" : "text-slate-200 group-hover:text-white"
                                        )}>
                                            {item.name}
                                        </span>
                                    </div>
                                    <span className={cn(
                                        "text-xs font-mono px-1.5 py-0.5 rounded transition-colors",
                                        isSelected ? "bg-primary/20 text-primary-300" : "bg-slate-900/50 text-slate-400"
                                    )}>
                                        {item.percentage}%
                                    </span>
                                </div>

                                <div className="flex items-end justify-between w-full">
                                    <span className="text-xs text-slate-500 group-hover:text-slate-400 transition-colors">
                                        {item.value} {item.value === 1 ? 'leak' : 'leaks'}
                                    </span>
                                </div>

                                {/* Progress Bar Background */}
                                <div className="absolute bottom-0 left-0 w-full h-1 bg-slate-700/30">
                                    {/* Active Progress */}
                                    <div
                                        className="h-full transition-all duration-500 ease-out"
                                        style={{
                                            width: `${item.percentage}%`,
                                            backgroundColor: color,
                                            opacity: isSelected ? 1 : 0.7
                                        }}
                                    />
                                </div>
                            </button>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}