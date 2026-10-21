import React, { useState, useEffect } from 'react';
import { Activity, ShieldCheck, Database, Server } from 'lucide-react';
import { systemApi } from '../../api/client';

export default function Topbar({ title, subtitle }) {
  const [serverStatus, setServerStatus] = useState('checking');

  useEffect(() => {
    systemApi.checkHealth()
      .then(() => setServerStatus('connected'))
      .catch(() => setServerStatus('disconnected'));
  }, []);

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-10 shadow-xs">
      <div>
        <h2 className="text-lg font-bold text-slate-800">{title}</h2>
        {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {/* Backend Server Status Indicator */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200 text-xs text-slate-600 font-medium">
          <Server className="w-3.5 h-3.5 text-indigo-600" />
          <span>FastAPI REST:</span>
          <span className="flex items-center gap-1.5">
            <span
              className={`w-2 h-2 rounded-full ${
                serverStatus === 'connected'
                  ? 'bg-emerald-500 animate-pulse'
                  : serverStatus === 'checking'
                  ? 'bg-amber-400'
                  : 'bg-rose-500'
              }`}
            />
            <span className={serverStatus === 'connected' ? 'text-emerald-700 font-semibold' : 'text-slate-500'}>
              {serverStatus === 'connected' ? 'Live (:8000)' : serverStatus}
            </span>
          </span>
        </div>

        {/* Database indicator */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-indigo-50 border border-indigo-100 text-xs text-indigo-700 font-medium">
          <Database className="w-3.5 h-3.5 text-indigo-600" />
          <span>SQLite 3 (ACID)</span>
        </div>
      </div>
    </header>
  );
}
