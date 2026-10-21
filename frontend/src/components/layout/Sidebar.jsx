import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  BookOpen,
  Users,
  Repeat,
  BarChart3,
  Compass,
  Zap,
  Library,
  LogOut,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const navItems = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Books Catalog', path: '/books', icon: BookOpen },
  { name: 'Members Directory', path: '/members', icon: Users },
  { name: 'Circulation & Loans', path: '/loans', icon: Repeat },
  { name: 'Analytics & Insights', path: '/analytics', icon: BarChart3 },
  { name: 'Google Books Discovery', path: '/discovery', icon: Compass },
  { name: 'Concurrency Lab', path: '/concurrency', icon: Zap },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 bg-slate-900 text-white flex flex-col shrink-0 h-screen sticky top-0 border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800">
        <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-500/20">
          <Library className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-wide text-white">SMART LIBRARY</h1>
          <p className="text-[11px] text-slate-400 font-medium tracking-wider uppercase">Analytics System</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
          Main Menu
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Footer Profile */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/60">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5 truncate">
            <div className="w-8 h-8 rounded-full bg-indigo-700 text-white flex items-center justify-center font-bold text-xs ring-2 ring-indigo-500/30">
              {user?.name ? user.name.charAt(0).toUpperCase() : 'U'}
            </div>
            <div className="truncate">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.name || 'Administrator'}</p>
              <div className="flex items-center gap-1 text-[11px] text-indigo-400">
                <ShieldCheck className="w-3 h-3" />
                <span>{user?.role || 'Librarian'}</span>
              </div>
            </div>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-slate-800 hover:bg-rose-950/40 text-slate-400 hover:text-rose-400 text-xs font-medium transition-colors border border-slate-700/60"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}
