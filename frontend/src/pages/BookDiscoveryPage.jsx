import React, { useState } from 'react';
import {
  Compass,
  Search,
  BookPlus,
  ExternalLink,
  CheckCircle,
  AlertCircle,
  X,
  Sparkles,
  BookOpen,
} from 'lucide-react';
import { googleBooksApi } from '../api/client';

export default function BookDiscoveryPage() {
  const [query, setQuery] = useState('Python Algorithms');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Import Modal state
  const [selectedBook, setSelectedBook] = useState(null);
  const [importForm, setImportForm] = useState({
    book_id: '',
    title: '',
    author: '',
    category: '',
    price: 550,
    total_copies: 5,
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const books = await googleBooksApi.search(query);
      setResults(books);
    } catch (err) {
      setError(err.message || 'Failed to search Google Books API');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenImport = (item) => {
    setSelectedBook(item);
    setImportForm({
      book_id: item.suggested_book_id || `GB-${Math.floor(1000 + Math.random() * 9000)}`,
      title: item.title,
      author: item.author,
      category: item.category || 'Computer Science',
      price: 599.0,
      total_copies: 4,
    });
  };

  const handleConfirmImport = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      const res = await googleBooksApi.importToCatalog({
        book_id: importForm.book_id,
        title: importForm.title,
        author: importForm.author,
        category: importForm.category,
        price: parseFloat(importForm.price),
        total_copies: parseInt(importForm.total_copies, 10),
      });
      setSuccess(res.message);
      setSelectedBook(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
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

      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span>Google Books API Discovery</span>
          <Compass className="w-5 h-5 text-indigo-600" />
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Search the global Google Books REST API repository and import records into your local catalog
        </p>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-xs flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by title, topic, author, or ISBN in Google Books..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-slate-50/50"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold shadow-xs transition-colors disabled:opacity-50"
        >
          {loading ? 'Searching API...' : 'Search Online'}
        </button>
      </form>

      {/* Results Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {results.map((book, idx) => (
          <div
            key={idx}
            className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col justify-between hover:shadow-md transition-shadow"
          >
            <div>
              <div className="flex gap-4 mb-3">
                {book.thumbnail ? (
                  <img
                    src={book.thumbnail}
                    alt={book.title}
                    className="w-16 h-22 object-cover rounded-lg shadow-xs border border-slate-200 shrink-0"
                  />
                ) : (
                  <div className="w-16 h-22 bg-indigo-50 rounded-lg flex items-center justify-center text-indigo-400 shrink-0">
                    <BookOpen className="w-6 h-6" />
                  </div>
                )}
                <div className="min-w-0">
                  <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 text-[10px] font-bold uppercase tracking-wider">
                    {book.category}
                  </span>
                  <h3 className="text-xs font-bold text-slate-800 line-clamp-2 mt-1">{book.title}</h3>
                  <p className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">{book.author}</p>
                  <p className="text-[10px] text-slate-400 mt-1 font-mono">{book.isbn ? `ISBN: ${book.isbn}` : book.published_date}</p>
                </div>
              </div>

              <p className="text-xs text-slate-500 line-clamp-3 mb-4">{book.description}</p>
            </div>

            <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-400">{book.suggested_book_id}</span>
              <button
                onClick={() => handleOpenImport(book)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors"
              >
                <BookPlus className="w-3.5 h-3.5" />
                <span>Import to Catalog</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {results.length === 0 && !loading && (
        <div className="bg-white rounded-2xl p-12 text-center border border-slate-200/80">
          <Compass className="w-10 h-10 mx-auto text-slate-300 mb-2" />
          <p className="text-sm font-semibold text-slate-700">Search Google Books to Discover Titles</p>
          <p className="text-xs text-slate-400 mt-1">Enter a search keyword above to query millions of global books</p>
        </div>
      )}

      {/* Import to Catalog Modal */}
      {selectedBook && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
              <h3 className="font-bold text-slate-800 text-base">Import Book to Local Catalog</h3>
              <button onClick={() => setSelectedBook(null)} className="text-slate-400 hover:text-slate-600">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleConfirmImport} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Catalog Book ID
                </label>
                <input
                  type="text"
                  required
                  value={importForm.book_id}
                  onChange={(e) => setImportForm({ ...importForm, book_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs font-mono"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  required
                  value={importForm.title}
                  onChange={(e) => setImportForm({ ...importForm, title: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                  Author
                </label>
                <input
                  type="text"
                  required
                  value={importForm.author}
                  onChange={(e) => setImportForm({ ...importForm, author: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Category
                  </label>
                  <input
                    type="text"
                    required
                    value={importForm.category}
                    onChange={(e) => setImportForm({ ...importForm, category: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Price (₹)
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    required
                    value={importForm.price}
                    onChange={(e) => setImportForm({ ...importForm, price: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-600 mb-1">
                    Copies
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={importForm.total_copies}
                    onChange={(e) => setImportForm({ ...importForm, total_copies: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs"
                  />
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setSelectedBook(null)}
                  className="px-4 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-colors disabled:opacity-50"
                >
                  {submitting ? 'Adding...' : 'Save to Catalog'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
