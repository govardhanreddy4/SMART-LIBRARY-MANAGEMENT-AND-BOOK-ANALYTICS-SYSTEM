import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Library, Lock, User, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Invalid username or password');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemo = async () => {
    setUsername('admin');
    setPassword('admin123');
    setLoading(true);
    setError('');
    try {
      await login('admin', 'admin123');
      navigate('/');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Background Glow */}
      <div className="absolute w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-3xl -top-32 -left-32 pointer-events-none" />
      <div className="absolute w-[500px] h-[500px] bg-sky-600/10 rounded-full blur-3xl -bottom-32 -right-32 pointer-events-none" />

      <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-8 relative z-10 border border-slate-100">
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-indigo-600 rounded-2xl mx-auto flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 mb-4">
            <Library className="w-7 h-7" />
          </div>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight">Smart Library Portal</h1>
          <p className="text-sm text-slate-500 mt-1">Book Analytics & Management System</p>
        </div>

        {error && (
          <div className="mb-6 p-4 rounded-xl bg-rose-50 border border-rose-200 flex items-start gap-3 text-rose-700 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Authentication Failed</p>
              <p className="text-xs text-rose-600 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
              Username
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <User className="w-4 h-4" />
              </div>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm bg-slate-50/50"
                placeholder="Enter username"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
              Password
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                <Lock className="w-4 h-4" />
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm bg-slate-50/50"
                placeholder="Enter password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm shadow-md shadow-indigo-600/20 flex items-center justify-center gap-2 transition-all duration-150 disabled:opacity-60"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Portal'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-slate-100">
          <div className="bg-slate-50 rounded-xl p-3.5 border border-slate-200/80 mb-3">
            <p className="text-xs text-slate-600 font-medium mb-1">Default Evaluator Credentials:</p>
            <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>user: <strong className="text-slate-800">admin</strong></span>
              <span>pass: <strong className="text-slate-800">admin123</strong></span>
            </div>
          </div>

          <button
            onClick={handleQuickDemo}
            type="button"
            className="w-full py-2 px-3 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-medium text-xs flex items-center justify-center gap-1.5 transition-colors border border-emerald-200"
          >
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>1-Click Quick Demo Sign In</span>
          </button>
        </div>
      </div>
    </div>
  );
}
