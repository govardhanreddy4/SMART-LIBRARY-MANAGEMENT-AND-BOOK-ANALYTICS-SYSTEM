import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  Search,
  Plus,
  Filter,
  Edit2,
  Trash2,
  Download,
  Upload,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  FileText,
  X,
  Code2,
  Layers,
} from 'lucide-react';
import { booksApi, getApiUrl } from '../api/client';

export default function BooksPage() {
  const [books, setBooks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [funcDemo, setFuncDemo] = useState(null);
  const [showDemoModal, setShowDemoModal] = useState(false);

  // Modals state
  const [modalMode, setModalMode] = useState(null); // 'add' | 'edit' | 'import' | null
  const [selectedBook, setSelectedBook] = useState(null);
  const [formData, setFormData] = useState({
    book_id: '',
    title: '',
    author: '',
    category: '',
    price: '',
    total_copies: 1,
    available_copies: 1,
  });
  const [submitting, setSubmitting] = useState(false);
  const [importFile, setImportFile] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      const [booksRes, catsRes] = await Promise.all([
        booksApi.list(search, categoryFilter),
        booksApi.getCategories(),
      ]);
      setBooks(booksRes);
      setCategories(catsRes);
    } catch (err) {
      setError(err.message || 'Failed to load books');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      loadData();
    }, 200);
    return () => clearTimeout(timer);
  }, [search, categoryFilter]);

  const loadFunctionalDemo = async () => {
    try {
      const res = await booksApi.getFunctionalDemo();
      setFuncDemo(res);
      setShowDemoModal(true);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleOpenAdd = () => {
    setFormData({
      book_id: `BK-${Math.floor(1000 + Math.random() * 9000)}`,
      title: '',
      author: '',
      category: categories[0] || 'Computer Science',
      price: '',
      total_copies: 5,
      available_copies: 5,
    });
    setModalMode('add');
  };

  const handleOpenEdit = (book) => {
    setSelectedBook(book);
    setFormData({
      book_id: book.book_id,
      title: book.title,
      author: book.author,
      category: book.category,
      price: book.price,
      total_copies: book.total_copies,
      available_copies: book.available_copies,
    });
    setModalMode('edit');
  };

  const handleDelete = async (bookId) => {
    if (!window.confirm(`Are you sure you want to delete book '${bookId}'?`)) return;
    try {
      setError('');
      await booksApi.delete(bookId);
      setSuccess(`Book ${bookId} removed successfully.`);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSubmitForm = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const payload = {
        ...formData,
        price: parseFloat(formData.price),
        total_copies: parseInt(formData.total_copies, 10),
        available_copies: parseInt(formData.available_copies, 10),
      };

      if (modalMode === 'add') {
        await booksApi.create(payload);
        setSuccess(`Book "${payload.title}" created successfully.`);
      } else {
        await booksApi.update(selectedBook.book_id, payload);
        setSuccess(`Book "${payload.title}" updated successfully.`);
      }
      setModalMode(null);
      loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleImportSubmit = async (e) => {
    e.preventDefault();
    if (!importFile) return;
    setSubmitting(true);
    setError('');
    try {
      const fd = new FormData();
      fd.append('file', importFile);
      const res = await booksApi.importFile(fd);
      setSuccess(res.message);
      setModalMode(null);
      setImportFile(null);
      loadData();
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleExport = (format) => {
    window.open(getApiUrl(`/books/export/${format}`), '_blank');
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
          <h1 className="text-xl font-bold text-slate-800">Book Catalog Management</h1>
          <p className="text-xs text-slate-500">Manage catalog records, inventory stock, and data interchange</p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* Functional Programming Demo Trigger */}
          <button
            onClick={loadFunctionalDemo}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold border border-indigo-200 transition-colors"
            title="Demonstrate Course Module II Functional Programming Concepts"
          >
            <Code2 className="w-3.5 h-3.5 text-indigo-600" />
            <span>Module II: Functional Demo</span>
          </button>

          {/* Import Button */}
          <button
            onClick={() => setModalMode('import')}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold border border-slate-200 shadow-xs transition-colors"
          >
            <Upload className="w-3.5 h-3.5 text-slate-500" />
            <span>Import CSV/JSON</span>
          </button>

          {/* Export Dropdown / Buttons */}
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
            <button
              onClick={() => handleExport('xml')}
              className="px-2 py-1 text-xs font-semibold text-slate-700 hover:text-indigo-600 rounded-md hover:bg-slate-50"
            >
              XML
            </button>
          </div>

          {/* Add Book */}
          <button
            onClick={handleOpenAdd}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-sm shadow-indigo-600/30 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add New Book</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by title, author, or Book ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-slate-50/50"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400 shrink-0" />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="w-full sm:w-48 py-2 px-3 rounded-xl border border-slate-200 text-xs text-slate-700 bg-slate-50/50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">All Categories ({books.length})</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Books Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-slate-50/75 border-b border-slate-200 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <th className="py-3 px-4">Book ID</th>
                <th className="py-3 px-4">Title & Author</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4 text-right">Price (₹)</th>
                <th className="py-3 px-4 text-center">Total Stock</th>
                <th className="py-3 px-4 text-center">Available</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {books.length > 0 ? (
                books.map((b) => (
                  <tr key={b.book_id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-indigo-600">{b.book_id}</td>
                    <td className="py-3 px-4 max-w-xs">
                      <p className="font-bold text-slate-800 truncate">{b.title}</p>
                      <p className="text-[11px] text-slate-400 mt-0.5">{b.author}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 font-medium">
                        {b.category}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right font-mono font-semibold text-slate-800">
                      ₹{parseFloat(b.price).toFixed(2)}
                    </td>
                    <td className="py-3 px-4 text-center font-bold text-slate-700">{b.total_copies}</td>
                    <td className="py-3 px-4 text-center font-bold">
                      <span className={b.available_copies > 0 ? 'text-emerald-600' : 'text-rose-600'}>
                        {b.available_copies}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                          b.available_copies > 0
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {b.available_copies > 0 ? 'In Stock' : 'Out of Stock'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleOpenEdit(b)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                          title="Edit Book Details"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(b.book_id)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete Book"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-400">
                    <BookOpen className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                    <p className="text-sm font-semibold">No books found</p>
                    <p className="text-xs text-slate-400 mt-1">Try adjusting your search or category filter</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add / Edit Book Modal */}
      {(modalMode === 'add' || modalMode === 'edit') && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-lg p-6 overflow-hidden">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-base">
                {modalMode === 'add' ? 'Add New Catalog Book' : `Edit Book: ${formData.book_id}`}
              </h3>
              <button
                onClick={() => setModalMode(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitForm} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Book ID
                  </label>
                  <input
                    type="text"
                    required
                    disabled={modalMode === 'edit'}
                    value={formData.book_id}
                    onChange={(e) => setFormData({ ...formData, book_id: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs disabled:bg-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Category
                  </label>
                  <input
                    type="text"
                    required
                    list="cat-suggestions"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                    placeholder="e.g. Computer Science"
                  />
                  <datalist id="cat-suggestions">
                    {categories.map((c) => (
                      <option key={c} value={c} />
                    ))}
                  </datalist>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Book Title
                </label>
                <input
                  type="text"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  placeholder="e.g. Clean Architecture"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Author(s)
                </label>
                <input
                  type="text"
                  required
                  value={formData.author}
                  onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  placeholder="e.g. Robert C. Martin"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Price (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={formData.price}
                    onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Total Copies
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formData.total_copies}
                    onChange={(e) => setFormData({ ...formData, total_copies: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Available Copies
                  </label>
                  <input
                    type="number"
                    min="0"
                    max={formData.total_copies}
                    required
                    value={formData.available_copies}
                    onChange={(e) => setFormData({ ...formData, available_copies: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  />
                </div>
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
                  {submitting ? 'Saving...' : modalMode === 'add' ? 'Add Book' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Import CSV / JSON Modal */}
      {modalMode === 'import' && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-base">Import Book Catalog</h3>
              <button onClick={() => setModalMode(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleImportSubmit} className="space-y-4">
              <p className="text-xs text-slate-500">
                Upload a CSV or JSON file containing columns: <code>book_id, title, author, category, price, total_copies</code>.
              </p>

              <div className="border-2 border-dashed border-slate-200 rounded-2xl p-6 text-center hover:border-indigo-400 transition-colors">
                <FileText className="w-8 h-8 text-indigo-500 mx-auto mb-2" />
                <input
                  type="file"
                  accept=".csv,.json"
                  onChange={(e) => setImportFile(e.target.files[0])}
                  className="text-xs text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setModalMode(null)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={!importFile || submitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors disabled:opacity-50"
                >
                  {submitting ? 'Importing...' : 'Upload & Process'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Module II: Functional Programming Modal */}
      {showDemoModal && funcDemo && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-xl p-6 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2">
                <Code2 className="w-5 h-5 text-indigo-600" />
                <h3 className="font-bold text-slate-800 text-base">Module II: Functional Python Results</h3>
              </div>
              <button onClick={() => setShowDemoModal(false)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-3.5 bg-indigo-50 rounded-xl border border-indigo-100">
                <span className="font-bold text-indigo-900">functools.reduce() Inventory Valuation:</span>
                <p className="text-lg font-black text-indigo-700 mt-1">₹{funcDemo.total_valuation_reduce?.toLocaleString()}</p>
                <p className="text-[11px] text-indigo-600 mt-0.5">Computed via: <code>reduce(lambda acc, b: acc + (b.price * b.total_copies), catalog, 0.0)</code></p>
              </div>

              <div className="p-3.5 bg-emerald-50 rounded-xl border border-emerald-100">
                <span className="font-bold text-emerald-900">filter() with Lambda (Available Copies &gt; 0):</span>
                <p className="text-lg font-black text-emerald-700 mt-1">{funcDemo.available_books_count_filter} Books Available</p>
                <p className="text-[11px] text-emerald-600 mt-0.5">Computed via: <code>filter(lambda b: b.is_available, catalog)</code></p>
              </div>

              <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200">
                <span className="font-bold text-slate-800">map() with Lambda Summary Strings (Sample):</span>
                <ul className="list-disc list-inside mt-2 space-y-1 font-mono text-[11px] text-slate-600">
                  {funcDemo.formatted_summaries_map?.map((s, idx) => (
                    <li key={idx} className="truncate">{s}</li>
                  ))}
                </ul>
              </div>

              <div className="p-3.5 bg-purple-50 rounded-xl border border-purple-100">
                <span className="font-bold text-purple-900">Set Comprehension (Unique Categories):</span>
                <p className="font-mono text-[11px] text-purple-700 mt-1">
                  {`{ b.category for b in catalog }`} &rarr; {funcDemo.categories_set_comp?.join(', ')}
                </p>
              </div>

              <div className="p-3.5 bg-amber-50 rounded-xl border border-amber-100">
                <span className="font-bold text-amber-900">List Comprehension (Low Stock &le; 2 copies):</span>
                <p className="font-mono text-[11px] text-amber-700 mt-1">
                  {`[b.title for b in catalog if b.available_copies <= 2]`} &rarr; {funcDemo.low_stock_titles_list_comp?.length ? funcDemo.low_stock_titles_list_comp.join(', ') : 'None'}
                </p>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 text-right">
              <button
                onClick={() => setShowDemoModal(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
