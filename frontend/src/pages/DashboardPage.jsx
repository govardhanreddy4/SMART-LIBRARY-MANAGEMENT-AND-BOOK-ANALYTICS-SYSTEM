import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Layers,
  CheckCircle2,
  Clock,
  Users,
  AlertTriangle,
  RefreshCw,
  TrendingUp,
  ArrowUpRight,
  Sparkles,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { dashboardApi } from '../api/client';
import { Link } from 'react-router-dom';

const DONUT_COLORS = ['#10B981', '#4F46E5', '#EF4444'];

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      setError('');
      const res = await dashboardApi.getCharts();
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard metrics');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <RefreshCw className="w-8 h-8 text-indigo-600 animate-spin" />
        <p className="text-sm font-medium text-slate-500">Loading library metrics from SQLite...</p>
      </div>
    );
  }

  const summary = data?.summary || {
    total_titles: 0,
    total_copies: 0,
    available_copies: 0,
    issued_copies: 0,
    active_members: 0,
    overdue_loans: 0,
  };

  const statCards = [
    {
      title: 'Catalog Titles',
      value: summary.total_titles,
      subtext: 'Unique titles catalogued',
      icon: BookOpen,
      color: 'from-blue-600 to-indigo-600',
      iconColor: 'text-indigo-600',
      bgColor: 'bg-indigo-50',
    },
    {
      title: 'Total Physical Copies',
      value: summary.total_copies,
      subtext: 'Inventory stock count',
      icon: Layers,
      color: 'from-indigo-600 to-purple-600',
      iconColor: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Available on Shelves',
      value: summary.available_copies,
      subtext: `${summary.total_copies ? Math.round((summary.available_copies / summary.total_copies) * 100) : 0}% ready for borrowing`,
      icon: CheckCircle2,
      color: 'from-emerald-600 to-teal-600',
      iconColor: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
    {
      title: 'Currently In Circulation',
      value: summary.issued_copies,
      subtext: 'Active reader loans',
      icon: Clock,
      color: 'from-amber-500 to-orange-600',
      iconColor: 'text-amber-600',
      bgColor: 'bg-amber-50',
    },
    {
      title: 'Registered Members',
      value: summary.active_members,
      subtext: 'Students & Faculty accounts',
      icon: Users,
      color: 'from-sky-500 to-blue-600',
      iconColor: 'text-sky-600',
      bgColor: 'bg-sky-50',
    },
    {
      title: 'Overdue Loans',
      value: summary.overdue_loans,
      subtext: 'Fines accruing at ₹2.00/day',
      icon: AlertTriangle,
      color: 'from-rose-500 to-red-600',
      iconColor: 'text-rose-600',
      bgColor: 'bg-rose-50',
      highlight: summary.overdue_loans > 0,
    },
  ];

  return (
    <div className="space-y-8">
      {/* Top Controls Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight flex items-center gap-2">
            <span>Operational Overview</span>
            <Sparkles className="w-5 h-5 text-indigo-500" />
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time analytics computed directly from the SQLite database
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="inline-flex items-center gap-2 px-3.5 py-2 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg border border-slate-200 shadow-xs transition-colors self-start sm:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${refreshing ? 'animate-spin' : ''}`} />
          <span>{refreshing ? 'Refreshing...' : 'Refresh Live Data'}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-medium">
          {error}
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <div
              key={i}
              className={`bg-white rounded-2xl p-5 border transition-all duration-200 hover:shadow-md ${
                card.highlight ? 'border-rose-300 ring-1 ring-rose-300/50' : 'border-slate-200/80 shadow-xs'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  {card.title}
                </span>
                <div className={`w-9 h-9 rounded-xl ${card.bgColor} ${card.iconColor} flex items-center justify-center`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-black text-slate-800 tracking-tight">{card.value}</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">{card.subtext}</p>
            </div>
          );
        })}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown Bar Chart */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-slate-800 text-base">Book Inventory by Category</h3>
              <p className="text-xs text-slate-400 mt-0.5">Total stock vs Available copies on shelves</p>
            </div>
            <Link
              to="/analytics"
              className="inline-flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-800"
            >
              <span>Full Analytics</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={data?.category_data || []}
                margin={{ top: 10, right: 10, left: -20, bottom: 25 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis
                  dataKey="category"
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  angle={-25}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px',
                  }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend wrapperStyle={{ paddingTop: 10, fontSize: '12px' }} />
                <Bar dataKey="total_copies" name="Total Copies" fill="#4F46E5" radius={[4, 4, 0, 0]} />
                <Bar dataKey="available_copies" name="Available Copies" fill="#10B981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Circulation Status Donut Chart */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col">
          <div className="mb-4">
            <h3 className="font-bold text-slate-800 text-base">Circulation Breakdown</h3>
            <p className="text-xs text-slate-400 mt-0.5">Physical copies status split</p>
          </div>

          <div className="h-60 w-full flex-1 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.circulation_status || []}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                >
                  {(data?.circulation_status || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={DONUT_COLORS[index % DONUT_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Donut Legend */}
          <div className="space-y-2 pt-2 border-t border-slate-100">
            {(data?.circulation_status || []).map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span
                    className="w-3 h-3 rounded-full shrink-0"
                    style={{ backgroundColor: DONUT_COLORS[idx % DONUT_COLORS.length] }}
                  />
                  <span className="text-slate-600 font-medium">{item.name}</span>
                </div>
                <span className="font-bold text-slate-800">{item.value} copies</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Grid: Recent Activity & Popular Books */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Circulation Activity */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-800 text-base">Recent Loan Activities</h3>
              <p className="text-xs text-slate-400 mt-0.5">Latest circulation events in SQLite</p>
            </div>
            <Link
              to="/loans"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
            >
              View All Loans
            </Link>
          </div>

          <div className="divide-y divide-slate-100">
            {data?.recent_loans?.length ? (
              data.recent_loans.map((loan) => (
                <div key={loan.loan_id} className="py-3 flex items-center justify-between">
                  <div className="min-w-0 pr-4">
                    <p className="text-xs font-bold text-slate-800 truncate">{loan.title}</p>
                    <p className="text-[11px] text-slate-400 mt-0.5">
                      Borrower: <span className="font-medium text-slate-600">{loan.member_name}</span> ({loan.member_id})
                    </p>
                  </div>
                  <div className="flex flex-col items-end shrink-0">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase ${
                        loan.status === 'RETURNED'
                          ? 'bg-slate-100 text-slate-600'
                          : loan.status === 'OVERDUE'
                          ? 'bg-rose-100 text-rose-700'
                          : 'bg-emerald-100 text-emerald-700'
                      }`}
                    >
                      {loan.status}
                    </span>
                    <span className="text-[10px] text-slate-400 mt-1">Due: {loan.due_date}</span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 py-4 text-center">No recent loans found.</p>
            )}
          </div>
        </div>

        {/* Most Popular Titles */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-bold text-slate-800 text-base">Most Borrowed Titles</h3>
              <p className="text-xs text-slate-400 mt-0.5">Calculated by borrowing frequency</p>
            </div>
            <Link
              to="/books"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800"
            >
              Browse Catalog
            </Link>
          </div>

          <div className="space-y-3">
            {data?.popular_books?.length ? (
              data.popular_books.map((b, idx) => (
                <div
                  key={b.book_id}
                  className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-100"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="w-6 h-6 rounded-lg bg-indigo-100 text-indigo-700 text-xs font-bold flex items-center justify-center shrink-0">
                      #{idx + 1}
                    </span>
                    <div className="min-w-0">
                      <p className="text-xs font-bold text-slate-800 truncate">{b.title}</p>
                      <p className="text-[11px] text-slate-400 truncate">{b.author} • {b.category}</p>
                    </div>
                  </div>
                  <span className="px-2.5 py-1 rounded-lg bg-white border border-slate-200 text-xs font-bold text-indigo-600 shrink-0">
                    {b.borrow_count} loans
                  </span>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400 py-4 text-center">No borrowing data recorded yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
