import React from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Topbar from './Topbar';

const pageMeta = {
  '/': { title: 'Operational Dashboard', subtitle: 'Real-time library KPIs, inventory valuation, and circulation overview' },
  '/books': { title: 'Book Catalog & Inventory', subtitle: 'Manage books, search collections, safe delete, and bulk CSV/JSON import/export' },
  '/members': { title: 'Members Directory', subtitle: 'Student and faculty membership management with verified regex validations' },
  '/loans': { title: 'Circulation & Book Loans', subtitle: 'Issue books, process returns, track overdue loans and calculated fines' },
  '/analytics': { title: 'Advanced Analytics & Insights', subtitle: 'Pandas data frame groupings and NumPy statistical price/duration distributions' },
  '/discovery': { title: 'Google Books API Discovery', subtitle: 'Search the live Google Books REST API and import directly into SQLite' },
  '/concurrency': { title: 'Concurrency & Performance Lab', subtitle: 'Live comparison benchmarking: Sequential vs Multithreaded vs Multiprocessing' },
};

export default function AppLayout() {
  const location = useLocation();
  const currentMeta = pageMeta[location.pathname] || {
    title: 'Smart Library Management',
    subtitle: 'Advanced Python & React Integrated System',
  };

  return (
    <div className="flex min-h-screen bg-slate-50 font-sans">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar title={currentMeta.title} subtitle={currentMeta.subtitle} />
        <main className="flex-1 p-8 overflow-y-auto max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
