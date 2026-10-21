import React, { useState } from 'react';
import {
  Zap,
  Play,
  Cpu,
  Clock,
  Layers,
  CheckCircle,
  AlertCircle,
  Sparkles,
  BarChart2,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { concurrencyApi } from '../api/client';

export default function ConcurrencyPage() {
  const [simulations, setSimulations] = useState(100000);
  const [chunks, setChunks] = useState(8);
  const [running, setRunning] = useState(false);
  const [benchmarkResult, setBenchmarkResult] = useState(null);
  const [error, setError] = useState('');

  const handleRunBenchmark = async () => {
    setRunning(true);
    setError('');
    try {
      const res = await concurrencyApi.runBenchmark(simulations, chunks);
      setBenchmarkResult(res.data);
    } catch (err) {
      setError(err.message || 'Benchmark execution failed');
    } finally {
      setRunning(false);
    }
  };

  const chartData = benchmarkResult
    ? [
        {
          name: 'Sequential (1 Thread)',
          time: benchmarkResult.sequential_time_sec,
          fill: '#EF4444',
        },
        {
          name: 'ThreadPool (GIL Bound)',
          time: benchmarkResult.threading_time_sec,
          fill: '#F59E0B',
        },
        {
          name: 'ProcessPool (True Multi-Core)',
          time: benchmarkResult.multiprocessing_time_sec,
          fill: '#10B981',
        },
      ]
    : [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="pb-2 border-b border-slate-200">
        <h1 className="text-2xl font-black text-slate-800 tracking-tight flex items-center gap-2">
          <span>Module III: Concurrency & Performance Lab</span>
          <Zap className="w-5 h-5 text-amber-500 fill-amber-500" />
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Live parallel execution benchmark comparing Python <strong>Single Thread</strong> vs{' '}
          <strong>ThreadPoolExecutor</strong> vs <strong>Multiprocessing Pool</strong>
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Control Panel Card */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-1">
            <h3 className="font-bold text-slate-800 text-base">Benchmark Configuration</h3>
            <p className="text-xs text-slate-500">
              Executes CPU-bound stochastic circulation risk scoring calculations across parallel workers
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                Simulations Count
              </label>
              <select
                value={simulations}
                onChange={(e) => setSimulations(Number(e.target.value))}
                disabled={running}
                className="py-2 px-3 rounded-xl border border-slate-200 text-xs bg-slate-50 font-mono"
              >
                <option value={50000}>50,000 iterations (Fast ~1s)</option>
                <option value={100000}>100,000 iterations (Standard ~2s)</option>
                <option value={250000}>250,000 iterations (Deep ~5s)</option>
                <option value={500000}>500,000 iterations (Stress ~10s)</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                Batch Chunks
              </label>
              <select
                value={chunks}
                onChange={(e) => setChunks(Number(e.target.value))}
                disabled={running}
                className="py-2 px-3 rounded-xl border border-slate-200 text-xs bg-slate-50 font-mono"
              >
                <option value={4}>4 Chunks</option>
                <option value={8}>8 Chunks (Default)</option>
                <option value={16}>16 Chunks</option>
              </select>
            </div>

            <div className="self-end">
              <button
                onClick={handleRunBenchmark}
                disabled={running}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50"
              >
                <Play className={`w-4 h-4 fill-white ${running ? 'animate-spin' : ''}`} />
                <span>{running ? 'Running Parallel Benchmark...' : 'Run Live Benchmark'}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results Section */}
      {benchmarkResult && (
        <div className="space-y-6">
          {/* Metrics comparison cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {/* Sequential Card */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Sequential Execution
                </span>
                <span className="px-2 py-0.5 rounded-md bg-rose-50 text-rose-700 font-bold text-[10px]">
                  Baseline (1.0x)
                </span>
              </div>
              <p className="text-3xl font-black text-slate-800 font-mono">
                {benchmarkResult.sequential_time_sec}s
              </p>
              <p className="text-xs text-slate-400 mt-1">Single-threaded CPU execution loop</p>
            </div>

            {/* Multithreading Card */}
            <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  ThreadPoolExecutor
                </span>
                <span className="px-2 py-0.5 rounded-md bg-amber-50 text-amber-700 font-bold text-[10px]">
                  {benchmarkResult.threading_speedup}x Speedup
                </span>
              </div>
              <p className="text-3xl font-black text-amber-600 font-mono">
                {benchmarkResult.threading_time_sec}s
              </p>
              <p className="text-xs text-slate-400 mt-1">Limited by Python's Global Interpreter Lock (GIL)</p>
            </div>

            {/* Multiprocessing Card */}
            <div className="bg-white rounded-2xl p-5 border-2 border-emerald-500/50 shadow-md">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Multiprocessing Pool
                </span>
                <span className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                  {benchmarkResult.multiprocessing_speedup}x Parallel Speedup!
                </span>
              </div>
              <p className="text-3xl font-black text-emerald-600 font-mono">
                {benchmarkResult.multiprocessing_time_sec}s
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Bypasses GIL across {benchmarkResult.cpu_cores_available} CPU cores
              </p>
            </div>
          </div>

          {/* Timing Comparison Bar Chart */}
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
            <h3 className="font-bold text-slate-800 text-base mb-1">Execution Time Comparison</h3>
            <p className="text-xs text-slate-400 mb-6">Lower duration represents faster performance</p>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 60, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                  <XAxis type="number" unit="s" tick={{ fontSize: 11, fill: '#64748b' }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: '#334155', fontWeight: 600 }} />
                  <Tooltip
                    formatter={(val) => [`${val} seconds`, 'Elapsed Duration']}
                    contentStyle={{
                      backgroundColor: '#1e293b',
                      borderRadius: '8px',
                      color: '#fff',
                      border: 'none',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="time" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Conceptual Explanations Box */}
      <div className="bg-slate-900 rounded-2xl p-6 text-slate-300 border border-slate-800">
        <h4 className="text-white font-bold text-sm mb-3 flex items-center gap-2">
          <Cpu className="w-4 h-4 text-indigo-400" />
          <span>Advanced Python Course Syllabus Mapping — Module III</span>
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <h5 className="font-bold text-white mb-1">1. GIL Contention in Multithreading</h5>
            <p className="text-slate-400">
              For CPU-bound numerical tasks, Python's Global Interpreter Lock (GIL) serializes thread execution, explaining why ThreadPoolExecutor does not scale linearly.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <h5 className="font-bold text-white mb-1">2. Multiprocessing Pool Acceleration</h5>
            <p className="text-slate-400">
              <code>multiprocessing.Pool</code> spawns distinct OS processes with dedicated interpreter instances, achieving true parallelism across all available CPU cores.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-800/60 border border-slate-700/50">
            <h5 className="font-bold text-white mb-1">3. High-Precision Profiling</h5>
            <p className="text-slate-400">
              Execution duration is measured with sub-microsecond precision using <code>time.perf_counter()</code>, and module call frequency is validated via <code>cProfile</code>.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
