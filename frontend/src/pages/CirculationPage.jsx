import React, { useState, useEffect } from 'react';
import {
  Repeat,
  AlertTriangle,
  CheckCircle2,
  Plus,
  Download,
  AlertCircle,
  X,
  BookOpen,
  User,
  Calendar,
  RotateCcw,
} from 'lucide-react';
import { loansApi, booksApi, membersApi } from '../api/client';

export default function CirculationPage() {
  const [tab, setTab] = useState('active'); // 'active' | 'overdue' | 'all'
  const [loans, setLoans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Issue Modal State
  const [showIssueModal, setShowIssueModal] = useState(false);
  const [books, setBooks] = useState([]);
  const [members, setMembers] = useState([]);
  const [issueData, setIssueData] = useState({
    book_id: '',
    member_id: '',
    loan_days: 14,
  });
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      let res;
      if (tab === 'active') {
        res = await loansApi.listActive();
      } else if (tab === 'overdue') {
        res = await loansApi.listOverdue();
      } else {
        res = await loansApi.listAll();
      }
      setLoans(res);
    } catch (err) {
      setError(err.message || 'Failed to load loans');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [tab]);

  const handleOpenIssueModal = async () => {
    try {
      const [booksRes, membersRes] = await Promise.all([
        booksApi.list(),
        membersApi.list(),
      ]);
      setBooks(booksRes);
      setMembers(membersRes);
      setIssueData({
        book_id: booksRes[0]?.book_id || '',
        member_id: membersRes[0]?.member_id || '',
        loan_days: 14,
      });
      setShowIssueModal(true);
    } catch (err) {
      setError('Failed to fetch books or members for checkout');
    }
  };

  const handleIssueSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const res = await loansApi.issue({
        book_id: issueData.book_id,
        member_id: issueData.member_id,
        loan_days: parseInt(issueData.loan_days, 10),
      });
      setSuccess(res.message);
      setShowIssueModal(false);
      loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReturn = async (loanId, title) => {
    if (!window.confirm(`Confirm return for "${title}" (Loan #${loanId})?`)) return;
    try {
      setError('');
      const res = await loansApi.returnBook(loanId);
      setSuccess(res.message);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleExport = (format) => {
    window.open(`/api/loans/export/${format}`, '_blank');
  };

  return (
    <div className="space-y-6">
      {/* Notifications */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError('')}><X className="w-4 h-4" /></button>
        </div>
      )}

      {success && (
        <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-semibold flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{success}</span>
          </div>
          <button onClick={() => setSuccess('')}><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Header and Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Circulation & Book Loans</h1>
          <p className="text-xs text-slate-500">Track book checkouts, manage returns, and monitor overdue fines</p>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="flex items-center rounded-xl border border-slate-200 bg-white p-0.5 shadow-xs">
            <span className="px-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
              <Download className="w-3 h-3" />
              <span>Export:</span>
            </span>
            <button
              onClick={() => handleExport('csv')}
              className="px-2 py-1 text-xs font-semibold text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-50"
            >
              CSV
            </button>
            <button
              onClick={() => handleExport('json')}
              className="px-2 py-1 text-xs font-semibold text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-50"
            >
              JSON
            </button>
          </div>

          <button
            onClick={handleOpenIssueModal}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm shadow-indigo-600/30 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Issue / Checkout Book</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-200 pb-2">
        <button
          onClick={() => setTab('active')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            tab === 'active'
              ? 'bg-indigo-600 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          Active Loans
        </button>
        <button
          onClick={() => setTab('overdue')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            tab === 'overdue'
              ? 'bg-rose-600 text-white shadow-xs'
              : 'text-rose-600 hover:bg-rose-50'
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Overdue Loans</span>
        </button>
        <button
          onClick={() => setTab('all')}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            tab === 'all'
              ? 'bg-slate-800 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
          }`}
        >
          All Circulation Records
        </button>
      </div>

      {/* Loans Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/75 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4">Loan ID</th>
                <th className="py-3 px-4">Book Details</th>
                <th className="py-3 px-4">Borrower</th>
                <th className="py-3 px-4">Issue Date</th>
                <th className="py-3 px-4">Due Date</th>
                {tab === 'overdue' && <th className="py-3 px-4 text-rose-600">Days Overdue</th>}
                {tab === 'overdue' && <th className="py-3 px-4 text-rose-600 text-right">Fine Amount</th>}
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loans.length > 0 ? (
                loans.map((loan) => (
                  <tr key={loan.loan_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-indigo-600">#{loan.loan_id}</td>
                    <td className="py-3 px-4 max-w-xs">
                      <p className="font-bold text-slate-800 truncate">{loan.title}</p>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">{loan.book_id}</p>
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-bold text-slate-800">{loan.member_name}</p>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">{loan.member_id}</p>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-600">{loan.issue_date}</td>
                    <td className="py-3 px-4 font-mono font-semibold text-slate-700">{loan.due_date}</td>
                    {tab === 'overdue' && (
                      <td className="py-3 px-4 font-bold text-rose-600">
                        {loan.days_overdue || 0} days
                      </td>
                    )}
                    {tab === 'overdue' && (
                      <td className="py-3 px-4 text-right font-mono font-bold text-rose-600">
                        ₹{(loan.fine_amount || 0).toFixed(2)}
                      </td>
                    )}
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          loan.status === 'RETURNED'
                            ? 'bg-slate-100 text-slate-600'
                            : loan.status === 'OVERDUE'
                            ? 'bg-rose-100 text-rose-700'
                            : 'bg-emerald-100 text-emerald-700'
                        }`}
                      >
                        {loan.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      {loan.status !== 'RETURNED' ? (
                        <button
                          onClick={() => handleReturn(loan.loan_id, loan.title)}
                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 font-bold text-[11px] border border-emerald-200 transition-colors"
                        >
                          <RotateCcw className="w-3 h-3" />
                          <span>Return</span>
                        </button>
                      ) : (
                        <span className="text-[11px] text-slate-400 font-mono">
                          Returned {loan.return_date}
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={tab === 'overdue' ? 9 : 7} className="py-12 text-center text-slate-400">
                    <Repeat className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                    <p className="text-sm font-semibold">No loans found in this category</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Issue Book Modal */}
      {showIssueModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-base">Issue Book to Member</h3>
              <button onClick={() => setShowIssueModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleIssueSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Select Book (Available in stock)
                </label>
                <select
                  required
                  value={issueData.book_id}
                  onChange={(e) => setIssueData({ ...issueData, book_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs bg-slate-50/50"
                >
                  {books.map((b) => (
                    <option key={b.book_id} value={b.book_id} disabled={b.available_copies <= 0}>
                      {b.title} [{b.book_id}] ({b.available_copies} available)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Select Member
                </label>
                <select
                  required
                  value={issueData.member_id}
                  onChange={(e) => setIssueData({ ...issueData, member_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs bg-slate-50/50"
                >
                  {members.map((m) => (
                    <option key={m.member_id} value={m.member_id}>
                      {m.name} ({m.member_id}) - {m.email}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Loan Duration (Days)
                </label>
                <input
                  type="number"
                  min="1"
                  max="90"
                  required
                  value={issueData.loan_days}
                  onChange={(e) => setIssueData({ ...issueData, loan_days: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                />
                <p className="text-[11px] text-slate-400 mt-1">Default policy: 14 days standard loan</p>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setShowIssueModal(false)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors disabled:opacity-50"
                >
                  {submitting ? 'Checking out...' : 'Confirm Loan Issue'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
