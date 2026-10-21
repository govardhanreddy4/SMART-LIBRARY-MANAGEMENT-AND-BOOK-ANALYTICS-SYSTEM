import React, { useState, useEffect } from 'react';
import {
  Users,
  Search,
  Plus,
  Edit2,
  Trash2,
  Download,
  AlertCircle,
  CheckCircle,
  X,
  Mail,
  Phone,
  Calendar,
  UserCheck,
} from 'lucide-react';
import { membersApi } from '../api/client';

export default function MembersPage() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Modals state
  const [modalMode, setModalMode] = useState(null); // 'add' | 'edit' | null
  const [selectedMember, setSelectedMember] = useState(null);
  const [formData, setFormData] = useState({
    member_id: '',
    name: '',
    email: '',
    phone: '',
  });
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      const res = await membersApi.list(search);
      setMembers(res);
    } catch (err) {
      setError(err.message || 'Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadData();
    }, 200);
    return () => clearTimeout(timer);
  }, [search]);

  const handleOpenAdd = () => {
    setFormData({
      member_id: `MEM-${Math.floor(100 + Math.random() * 900)}`,
      name: '',
      email: '',
      phone: '+91',
    });
    setModalMode('add');
  };

  const handleOpenEdit = (member) => {
    setSelectedMember(member);
    setFormData({
      member_id: member.member_id,
      name: member.name,
      email: member.email,
      phone: member.phone,
    });
    setModalMode('edit');
  };

  const handleDelete = async (memberId) => {
    if (!window.confirm(`Are you sure you want to delete member '${memberId}'?`)) return;
    try {
      setError('');
      await membersApi.delete(memberId);
      setSuccess(`Member ${memberId} removed successfully.`);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      if (modalMode === 'add') {
        await membersApi.create(formData);
        setSuccess(`Member "${formData.name}" registered successfully.`);
      } else {
        await membersApi.update(selectedMember.member_id, {
          name: formData.name,
          email: formData.email,
          phone: formData.phone,
        });
        setSuccess(`Member "${formData.name}" updated successfully.`);
      }
      setModalMode(null);
      loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleExport = (format) => {
    window.open(`/api/members/export/${format}`, '_blank');
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
            <CheckCircle className="w-4 h-4 shrink-0" />
            <span>{success}</span>
          </div>
          <button onClick={() => setSuccess('')}><X className="w-4 h-4" /></button>
        </div>
      )}

      {/* Header and Action Buttons */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800">Members Directory</h1>
          <p className="text-xs text-slate-500">Manage registered students, faculty members, and contact records</p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Export Buttons */}
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
            onClick={handleOpenAdd}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm shadow-indigo-600/30 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Register Member</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-xs">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by name, Member ID, email, or phone..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-slate-50/50"
          />
        </div>
      </div>

      {/* Members Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/75 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4">Member ID</th>
                <th className="py-3 px-4">Full Name</th>
                <th className="py-3 px-4">Email Address</th>
                <th className="py-3 px-4">Phone Number</th>
                <th className="py-3 px-4">Registered Date</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {members.length > 0 ? (
                members.map((m) => (
                  <tr key={m.member_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-indigo-600">{m.member_id}</td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-full bg-slate-100 text-slate-700 font-bold text-xs flex items-center justify-center shrink-0">
                          {m.name.charAt(0).toUpperCase()}
                        </div>
                        <span className="font-bold text-slate-800">{m.name}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      <div className="flex items-center gap-1.5">
                        <Mail className="w-3.5 h-3.5 text-slate-400" />
                        <span>{m.email}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-600 font-mono">
                      <div className="flex items-center gap-1.5">
                        <Phone className="w-3.5 h-3.5 text-slate-400" />
                        <span>{m.phone}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-500">
                      <div className="flex items-center gap-1.5">
                        <Calendar className="w-3.5 h-3.5 text-slate-400" />
                        <span>{m.created_at ? m.created_at.split('T')[0] : 'N/A'}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleOpenEdit(m)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                          title="Edit Member Contact"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(m.member_id)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete Member"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-400">
                    <Users className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                    <p className="text-sm font-semibold">No members found</p>
                    <p className="text-xs text-slate-400 mt-1">Try adjusting your search criteria</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Register / Edit Member Modal */}
      {(modalMode === 'add' || modalMode === 'edit') && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-base">
                {modalMode === 'add' ? 'Register New Member' : `Edit Member: ${formData.member_id}`}
              </h3>
              <button onClick={() => setModalMode(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Member ID
                </label>
                <input
                  type="text"
                  required
                  disabled={modalMode === 'edit'}
                  value={formData.member_id}
                  onChange={(e) => setFormData({ ...formData, member_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs disabled:bg-slate-100"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  placeholder="e.g. Aarav Sharma"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Email Address (Regex Validated)
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  placeholder="e.g. student@college.edu"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Phone Number (Regex Validated)
                </label>
                <input
                  type="text"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  placeholder="e.g. +919876543210"
                />
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setModalMode(null)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors disabled:opacity-50"
                >
                  {submitting ? 'Saving...' : modalMode === 'add' ? 'Register Member' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
