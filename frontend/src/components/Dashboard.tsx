import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, PieChart as RechartsPieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import {
  ArrowDownIcon,
  ArrowUpIcon,
  AlertCircleIcon,
  CheckCircleIcon,
  Wallet,
  TrendingUp,
  PiggyBank,
  Percent,
  Mail,
  Loader2,
  UtensilsCrossed,
  ShoppingBag,
  Shield,
  Receipt,
  Car,
  Film,
  Briefcase,
  CreditCard,
  Heart,
  GraduationCap,
  Banknote,
  MoreHorizontal,
  DollarSign,
  PieChart,
  LogIn,
  LogOut,
  User
} from 'lucide-react';
import api, { authService } from '../services/api';
import { useNavigate } from 'react-router-dom';

// ==================== TYPES ====================
interface Transaction {
  id: number;
  date: string;
  merchant: string;
  category_name: string | null;
  amount: number;
  trans_type: 'credit' | 'debit';
  bank_name: string | null;
  description: string | null;
}

interface MonthlyStats {
  month_year: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  category_breakdown: CategoryBreakdown[];
}

interface CategoryBreakdown {
  category_id: number;
  category_name: string;
  category_icon: string;
  category_color: string;
  total_amount: number;
  transaction_count: number;
  percentage: number;
}

// ==================== ICON MAPPING ====================
const getCategoryIcon = (categoryName: string): React.ReactNode => {
  const iconMap: Record<string, React.ReactNode> = {
    'Food & Dining': <UtensilsCrossed className="w-5 h-5" />,
    'Shopping': <ShoppingBag className="w-5 h-5" />,
    'Insurance': <Shield className="w-5 h-5" />,
    'Bills & Utilities': <Receipt className="w-5 h-5" />,
    'Bills': <Receipt className="w-5 h-5" />,
    'Travel & Transport': <Car className="w-5 h-5" />,
    'Travel': <Car className="w-5 h-5" />,
    'Entertainment': <Film className="w-5 h-5" />,
    'Salary': <Briefcase className="w-5 h-5" />,
    'Income': <Briefcase className="w-5 h-5" />,
    'Investments': <TrendingUp className="w-5 h-5" />,
    'Loan & EMI': <CreditCard className="w-5 h-5" />,
    'Cash Withdrawal': <Banknote className="w-5 h-5" />,
    'Health & Medical': <Heart className="w-5 h-5" />,
    'Education': <GraduationCap className="w-5 h-5" />,
    'Others': <MoreHorizontal className="w-5 h-5" />,
  };
  return iconMap[categoryName] || <DollarSign className="w-5 h-5" />;
};

// ==================== COMPONENTS ====================

// Dashboard Header
interface HeaderProps {
  userName: string | null;
  userEmail: string | null;
  isAuthenticated: boolean;
  onSyncEmails: () => void;
  onLogin: () => void;
  onLogout: () => void;
  syncing: boolean;
}

const Header: React.FC<HeaderProps> = ({ userName, userEmail, isAuthenticated, onSyncEmails, onLogin, onLogout, syncing }) => {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8 rounded-lg mb-8 shadow-lg">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <Wallet className="w-10 h-10" />
            Money Manager
          </h1>
          {isAuthenticated ? (
            <p className="text-blue-100 mt-2 flex items-center gap-2">
              <User className="w-4 h-4" />
              {userEmail || userName || 'User'}
            </p>
          ) : (
            <p className="text-blue-100 mt-2">Sign in to sync your emails</p>
          )}
        </div>
        <div className="flex gap-3">
          {isAuthenticated ? (
            <>
              <button
                className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center gap-2 disabled:opacity-50"
                onClick={onSyncEmails}
                disabled={syncing}
              >
                {syncing ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Mail className="w-5 h-5" />
                )}
                {syncing ? 'Syncing...' : 'Sync Emails'}
              </button>
              <button
                className="bg-red-500 text-white px-4 py-2 rounded-lg font-semibold hover:bg-red-600 transition flex items-center gap-2"
                onClick={onLogout}
              >
                <LogOut className="w-5 h-5" />
                Logout
              </button>
            </>
          ) : (
            <button
              className="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-blue-50 transition flex items-center gap-2"
              onClick={onLogin}
            >
              <LogIn className="w-5 h-5" />
              Sign in with Google
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

// Stats Card
interface StatsCardProps {
  title: string;
  value: string;
  change: number;
  icon: React.ReactNode;
  color: string;
  loading?: boolean;
}

const StatsCard: React.FC<StatsCardProps> = ({ title, value, change, icon, color, loading }) => {
  const isPositive = change >= 0;
  return (
    <div className="bg-white p-6 rounded-lg shadow-md border-l-4" style={{ borderColor: color }}>
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-500 text-sm font-medium">{title}</p>
          {loading ? (
            <div className="h-8 w-24 bg-gray-200 animate-pulse rounded mt-2"></div>
          ) : (
            <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          )}
          <div className="flex items-center mt-2">
            {isPositive ? (
              <ArrowUpIcon className="w-4 h-4 text-green-500" />
            ) : (
              <ArrowDownIcon className="w-4 h-4 text-red-500" />
            )}
            <span className={`text-sm font-semibold ml-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {Math.abs(change)}% vs last month
            </span>
          </div>
        </div>
        <div className="text-3xl text-gray-600">{icon}</div>
      </div>
    </div>
  );
};

// Spending Health Badge
interface HealthBadgeProps {
  health: 'excellent' | 'good' | 'moderate' | 'poor';
  score: number;
}

const HealthBadge: React.FC<HealthBadgeProps> = ({ health, score }) => {
  const colors = {
    excellent: { bg: 'bg-green-100', text: 'text-green-800', icon: <CheckCircleIcon className="w-5 h-5" /> },
    good: { bg: 'bg-blue-100', text: 'text-blue-800', icon: <CheckCircleIcon className="w-5 h-5" /> },
    moderate: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: <AlertCircleIcon className="w-5 h-5" /> },
    poor: { bg: 'bg-red-100', text: 'text-red-800', icon: <AlertCircleIcon className="w-5 h-5" /> },
  };

  const color = colors[health];
  return (
    <div className={`${color.bg} ${color.text} px-4 py-2 rounded-full inline-flex items-center`}>
      <span className="mr-2">{color.icon}</span>
      <span className="font-semibold">Spending Health: {health.toUpperCase()}</span>
      <span className="ml-2 text-sm">({score}/100)</span>
    </div>
  );
};

// Transaction List Component
interface TransactionListProps {
  transactions: Transaction[];
  loading?: boolean;
}

const TransactionList: React.FC<TransactionListProps> = ({ transactions, loading }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <CreditCard className="w-5 h-5" />
          Recent Transactions
        </h2>
      </div>
      <div className="overflow-x-auto">
        {loading ? (
          <div className="p-6 space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-gray-200 animate-pulse rounded"></div>
            ))}
          </div>
        ) : transactions.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <Receipt className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No transactions found</p>
            <p className="text-sm">Sync your emails to see transactions</p>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Merchant</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((txn) => (
                <tr key={txn.id} className="border-b border-gray-200 hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {new Date(txn.date).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    <div className="flex items-center gap-2">
                      {getCategoryIcon(txn.category_name || 'Others')}
                      {txn.merchant}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{txn.category_name || 'Uncategorized'}</td>
                  <td className={`px-6 py-4 text-sm font-semibold ${txn.trans_type === 'credit' ? 'text-green-600' : 'text-red-600'}`}>
                    {txn.trans_type === 'credit' ? '+' : '-'}₹{txn.amount.toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

// Category Breakdown Chart
interface CategoryData {
  name: string;
  value: number;
  color: string;
}

const CategoryChart: React.FC<{ data: CategoryData[]; loading?: boolean }> = ({ data, loading }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <PieChart className="w-5 h-5" />
        Spending by Category
      </h3>
      {loading ? (
        <div className="h-[300px] bg-gray-200 animate-pulse rounded"></div>
      ) : data.length === 0 ? (
        <div className="h-[300px] flex items-center justify-center text-gray-500">
          <div className="text-center">
            <ShoppingBag className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No spending data available</p>
          </div>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <RechartsPieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, value }: { name: string; value: number }) => `${name}: ₹${value.toLocaleString()}`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip formatter={(value: number) => `₹${value.toLocaleString()}`} />
          </RechartsPieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

// Monthly Trend Chart
interface TrendData {
  month: string;
  income: number;
  expenses: number;
}

const TrendChart: React.FC<{ data: TrendData[]; loading?: boolean }> = ({ data, loading }) => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <TrendingUp className="w-5 h-5" />
        6-Month Trend
      </h3>
      {loading ? (
        <div className="h-[300px] bg-gray-200 animate-pulse rounded"></div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" />
            <YAxis />
            <Tooltip formatter={(value: number) => `₹${value.toLocaleString()}`} />
            <Legend />
            <Bar dataKey="income" fill="#10b981" name="Income" />
            <Bar dataKey="expenses" fill="#ef4444" name="Expenses" />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

// Insights Panel
interface Insight {
  type: 'positive' | 'warning' | 'info';
  message: string;
}

const InsightsPanel: React.FC<{ insights: Insight[]; loading?: boolean }> = ({ insights, loading }) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return <CheckCircleIcon className="w-5 h-5 text-green-600" />;
      case 'warning':
        return <AlertCircleIcon className="w-5 h-5 text-yellow-600" />;
      default:
        return <CheckCircleIcon className="w-5 h-5 text-blue-600" />;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <TrendingUp className="w-5 h-5" />
        Smart Insights
      </h3>
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-200 animate-pulse rounded"></div>
          ))}
        </div>
      ) : insights.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <TrendingUp className="w-12 h-12 mx-auto mb-2 text-gray-300" />
          <p>No insights available yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {insights.map((insight, idx) => {
            const bgColor = {
              positive: 'bg-green-50 border-green-200',
              warning: 'bg-yellow-50 border-yellow-200',
              info: 'bg-blue-50 border-blue-200',
            }[insight.type];

            return (
              <div key={idx} className={`${bgColor} border-l-4 p-4 rounded`}>
                <div className="flex items-start">
                  <div className="mr-3 flex-shrink-0">{getIcon(insight.type)}</div>
                  <p className="text-sm text-gray-700">{insight.message}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

// ==================== MAIN DASHBOARD ====================

const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  // State for API data
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [stats, setStats] = useState<MonthlyStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Check for auth token on mount and handle callback
  useEffect(() => {
    // Check for token in URL (OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');

    if (tokenFromUrl) {
      // Store token and clean URL
      api.setToken(tokenFromUrl);
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    // Check for existing token
    const token = localStorage.getItem('auth_token');
    if (token) {
      api.setToken(token);
      setIsAuthenticated(true);
      // Get user info
      authService.getCurrentUser()
        .then(user => setUserEmail(user.email))
        .catch(() => {
          // Token invalid, clear it
          api.setToken(null);
          setIsAuthenticated(false);
        });
    }
  }, []);

  // Fetch data from API
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [transactionsRes, statsRes] = await Promise.all([
        api.getTransactions({ page: 1, page_size: 10 }),
        api.getMonthlyStats()
      ]);
      setTransactions(transactionsRes.transactions as Transaction[]);
      setStats(statsRes);
    } catch (err) {
      console.error('Failed to fetch data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Sync emails handler
  const handleSyncEmails = async () => {
    if (!isAuthenticated) {
      alert('Please sign in with Google first to sync your emails.');
      return;
    }

    setSyncing(true);
    try {
      const result = await api.syncEmails(30, 100);
      alert(`Sync complete! ${result.message}`);
      // Refresh data after sync
      await fetchData();
    } catch (err) {
      console.error('Failed to sync emails:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      if (errorMessage.includes('401') || errorMessage.includes('authenticated')) {
        alert('Session expired. Please sign in again.');
        handleLogout();
      } else {
        alert(`Failed to sync emails: ${errorMessage}`);
      }
    } finally {
      setSyncing(false);
    }
  };

  // Login handler
  const handleLogin = async () => {
    try {
      const { authorization_url } = await authService.initiateGoogleLogin();
      // Redirect to Google OAuth
      window.location.href = authorization_url;
    } catch (err) {
      console.error('Failed to get login URL:', err);
      alert('Failed to initiate login. Make sure Google OAuth is configured on the server.');
    }
  };

  // Logout handler
  const handleLogout = () => {
    authService.logout();
    localStorage.removeItem('onboarding_complete'); // Clear onboarding flag on logout
    setIsAuthenticated(false);
    setUserEmail(null);
    navigate('/login');
  };

  // Load data on mount
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Transform category breakdown for chart
  const categoryChartData: CategoryData[] = stats?.category_breakdown?.map(cat => ({
    name: cat.category_name,
    value: cat.total_amount,
    color: cat.category_color || '#6b7280'
  })) || [];

  // Mock trend data (would come from API in production)
  const trendData: TrendData[] = [
    { month: 'Jul', income: 75000, expenses: 42000 },
    { month: 'Aug', income: 75000, expenses: 45000 },
    { month: 'Sep', income: 80000, expenses: 48000 },
    { month: 'Oct', income: 75000, expenses: 41000 },
    { month: 'Nov', income: 78000, expenses: 46000 },
    { month: 'Dec', income: stats?.total_income || 82000, expenses: stats?.total_expenses || 50500 },
  ];

  // Generate insights based on stats
  const generateInsights = (): Insight[] => {
    const insights: Insight[] = [];

    if (stats) {
      // Savings rate insight
      if (stats.savings_rate >= 30) {
        insights.push({
          type: 'positive',
          message: `Your savings rate is ${stats.savings_rate.toFixed(1)}% this month - excellent! Keep up the disciplined spending.`
        });
      } else if (stats.savings_rate >= 15) {
        insights.push({
          type: 'info',
          message: `Your savings rate is ${stats.savings_rate.toFixed(1)}% this month. Consider increasing savings to 20%+.`
        });
      } else {
        insights.push({
          type: 'warning',
          message: `Your savings rate is only ${stats.savings_rate.toFixed(1)}%. Try to reduce expenses to improve savings.`
        });
      }

      // Top spending category insight
      if (stats.category_breakdown && stats.category_breakdown.length > 0) {
        const topCategory = stats.category_breakdown[0];
        insights.push({
          type: 'info',
          message: `Your top spending category is ${topCategory.category_name} at ₹${topCategory.total_amount.toLocaleString()} (${topCategory.percentage.toFixed(1)}% of expenses).`
        });
      }

      // Net savings insight
      if (stats.net_savings > 0) {
        insights.push({
          type: 'positive',
          message: `Great job! You saved ₹${stats.net_savings.toLocaleString()} this month.`
        });
      }
    }

    return insights;
  };

  // Calculate health score
  const getHealthScore = (): { health: 'excellent' | 'good' | 'moderate' | 'poor'; score: number } => {
    if (!stats) return { health: 'moderate', score: 50 };

    const savingsRate = stats.savings_rate;
    if (savingsRate >= 40) return { health: 'excellent', score: 90 };
    if (savingsRate >= 25) return { health: 'good', score: 75 };
    if (savingsRate >= 10) return { health: 'moderate', score: 55 };
    return { health: 'poor', score: 30 };
  };

  const healthInfo = getHealthScore();
  const insights = generateInsights();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <Header
        userName={userEmail?.split('@')[0] || null}
        userEmail={userEmail}
        isAuthenticated={isAuthenticated}
        onSyncEmails={handleSyncEmails}
        onLogin={handleLogin}
        onLogout={handleLogout}
        syncing={syncing}
      />

      <div className="max-w-7xl mx-auto px-4 pb-12">
        {/* Auth Prompt for non-authenticated users */}
        {!isAuthenticated && (
          <div className="mb-6 bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <div className="flex items-center">
              <LogIn className="w-5 h-5 text-blue-500 mr-2" />
              <p className="text-blue-700">
                <strong>Sign in with Google</strong> to sync your bank transaction emails and see real spending data.
              </p>
            </div>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
            <div className="flex items-center">
              <AlertCircleIcon className="w-5 h-5 text-red-500 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Health Badge */}
        <div className="mb-6">
          <HealthBadge health={healthInfo.health} score={healthInfo.score} />
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Income"
            value={`₹${(stats?.total_income || 0).toLocaleString()}`}
            change={8}
            icon={<Wallet className="w-8 h-8" />}
            color="#10b981"
            loading={loading}
          />
          <StatsCard
            title="Total Expenses"
            value={`₹${(stats?.total_expenses || 0).toLocaleString()}`}
            change={12}
            icon={<CreditCard className="w-8 h-8" />}
            color="#ef4444"
            loading={loading}
          />
          <StatsCard
            title="Total Savings"
            value={`₹${(stats?.net_savings || 0).toLocaleString()}`}
            change={5}
            icon={<PiggyBank className="w-8 h-8" />}
            color="#3b82f6"
            loading={loading}
          />
          <StatsCard
            title="Savings Rate"
            value={`${(stats?.savings_rate || 0).toFixed(1)}%`}
            change={2}
            icon={<Percent className="w-8 h-8" />}
            color="#8b5cf6"
            loading={loading}
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <CategoryChart data={categoryChartData} loading={loading} />
          <TrendChart data={trendData} loading={loading} />
        </div>

        {/* Transactions and Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <TransactionList transactions={transactions} loading={loading} />
          </div>
          <InsightsPanel insights={insights} loading={loading} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
