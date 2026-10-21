import React, { useState, useEffect } from 'react';
import {
  BarChart3,
  TrendingUp,
  Download,
  Calculator,
  Layers,
  Sparkles,
  RefreshCw,
  Table,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { analyticsApi, dashboardApi, getApiUrl } from '../api/client';

export default function AnalyticsPage() {
  const [catData, setCatData] = useState([]);
  const [priceStats, setPriceStats] = useState(null);
  const [durationStats, setDurationStats] = useState(null);
  const [popularBooks, setPopularBooks] = useState([]);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const [cats, prices, durations, popular, monthly] = await Promise.all([
        analyticsApi.getCategoryBreakdown(),
        analyticsApi.getPriceStats(),
        analyticsApi.getLoanDurationStats(),
        analyticsApi.getPopularBooks(8),
        analyticsApi.getMonthlyTrends(),
      ]);
      setCatData(cats);
      setPriceStats(prices);
      setDurationStats(durations);
      setPopularBooks(popular);
      setTrends(monthly);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, []);

  const handleExportReport = (format) => {
    window.open(getApiUrl(`/reports/download/${format}`), '_blank');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-3">
        <RefreshCw className="w-8 h-8 text-indigo-600 animate-spin" />
        <p className="text-sm font-medium text-slate-500">Computing Pandas & NumPy statistics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header and Download Report */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight flex items-center gap-2">
            <span>Module IV: Advanced Data Analytics</span>
            <Sparkles className="w-5 h-5 text-indigo-600" />
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Statistical computations driven by Python's <strong>Pandas</strong> and <strong>NumPy</strong> libraries
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center rounded-xl border border-slate-200 bg-white p-0.5 shadow-xs">
            <span className="px-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Download className="w-3 h-3" />
              <span>Full Report:</span>
            </span>
            <button
              onClick={() => handleExportReport('json')}
              className="px-2 py-1 text-xs font-semibold text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-50"
            >
              JSON
            </button>
            <button
              onClick={() => handleExportReport('csv')}
              className="px-2 py-1 text-xs font-semibold text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-50"
            >
              CSV
            </button>
            <button
              onClick={() => handleExportReport('xml')}
              className="px-2 py-1 text-xs font-semibold text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-50"
            >
              XML
            </button>
          </div>
        </div>
      </div>

      {/* NumPy Statistics Grid */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Calculator className="w-4 h-4 text-indigo-600" />
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-700">
            NumPy Statistical Measures
          </h2>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Mean Price</span>
            <p className="text-xl font-black text-slate-800 mt-1 font-mono">₹{priceStats?.mean ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">np.mean()</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Median Price</span>
            <p className="text-xl font-black text-indigo-600 mt-1 font-mono">₹{priceStats?.median ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">np.median()</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Std Deviation</span>
            <p className="text-xl font-black text-slate-800 mt-1 font-mono">₹{priceStats?.std ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">np.std()</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Min Price</span>
            <p className="text-xl font-black text-emerald-600 mt-1 font-mono">₹{priceStats?.min ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">np.min()</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Max Price</span>
            <p className="text-xl font-black text-purple-600 mt-1 font-mono">₹{priceStats?.max ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">np.max()</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">25th %ile (Q1)</span>
            <p className="text-xl font-black text-slate-700 mt-1 font-mono">₹{priceStats?.p25 ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">np.percentile(25)</p>
          </div>
          <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">75th %ile (Q3)</span>
            <p className="text-xl font-black text-slate-700 mt-1 font-mono">₹{priceStats?.p75 ?? 0}</p>
            <p className="text-[10px] text-slate-400 mt-0.5">np.percentile(75)</p>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Category Valuation Chart */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="mb-6">
            <h3 className="font-bold text-slate-800 text-base">Pandas Category Monetary Valuation</h3>
            <p className="text-xs text-slate-400 mt-0.5">Sum of (price × total_copies) aggregated by category</p>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={catData}
                margin={{ top: 10, right: 10, left: 10, bottom: 25 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                <XAxis
                  dataKey="category"
                  tick={{ fontSize: 11, fill: '#64748b' }}
                  angle={-25}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={(val) => `₹${val}`} />
                <Tooltip
                  formatter={(val) => [`₹${val.toLocaleString()}`, 'Valuation']}
                  contentStyle={{
                    backgroundColor: '#1e293b',
                    borderRadius: '8px',
                    color: '#fff',
                    border: 'none',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="valuation" name="Total Valuation (₹)" fill="#0EA5E9" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Borrowing Trends Chart */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="mb-6">
            <h3 className="font-bold text-slate-800 text-base">Pandas Time-Series Borrowing Trends</h3>
            <p className="text-xs text-slate-400 mt-0.5">Loans grouped by period (Year-Month)</p>
          </div>

          <div className="h-72 w-full">
            {trends.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={trends}
                  margin={{ top: 10, right: 10, left: -20, bottom: 25 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                  <XAxis dataKey="period" tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis tick={{ fontSize: 11, fill: '#64748b' }} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      borderRadius: '8px',
                      color: '#fff',
                      border: 'none',
                      fontSize: '12px',
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="loan_count"
                    name="Circulation Loans"
                    stroke="#4F46E5"
                    strokeWidth={3}
                    dot={{ fill: '#4F46E5', r: 5 }}
                    activeDot={{ r: 7 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-slate-400 text-xs">
                Not enough time-series loan records yet
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Category Aggregation Table (Pandas DataFrame Presentation) */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Table className="w-4 h-4 text-indigo-600" />
            <h3 className="font-bold text-slate-800 text-sm">Pandas GroupBy & Aggregation Table</h3>
          </div>
          <span className="text-[11px] font-mono text-slate-400">df.groupby('category').agg(...)</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/75 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4 text-center">Distinct Titles</th>
                <th className="py-3 px-4 text-center">Total Copies</th>
                <th className="py-3 px-4 text-center">Available Copies</th>
                <th className="py-3 px-4 text-center">Issued Copies</th>
                <th className="py-3 px-4 text-right">Avg Book Price</th>
                <th className="py-3 px-4 text-right">Total Valuation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {catData.map((row) => (
                <tr key={row.category} className="hover:bg-slate-50/80 transition-colors">
                  <td className="py-3 px-4 font-bold text-slate-800">{row.category}</td>
                  <td className="py-3 px-4 text-center">{row.title_count}</td>
                  <td className="py-3 px-4 text-center font-semibold text-slate-700">{row.total_copies}</td>
                  <td className="py-3 px-4 text-center text-emerald-600 font-bold">{row.available_copies}</td>
                  <td className="py-3 px-4 text-center text-indigo-600 font-bold">{row.issued_copies}</td>
                  <td className="py-3 px-4 text-right font-mono text-slate-700">
                    ₹{row.avg_price ? parseFloat(row.avg_price).toFixed(2) : '0.00'}
                  </td>
                  <td className="py-3 px-4 text-right font-mono font-bold text-slate-900">
                    ₹{row.valuation ? parseFloat(row.valuation).toLocaleString() : '0.00'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
