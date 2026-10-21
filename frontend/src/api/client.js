import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

// Interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Network request failed';
    return Promise.reject(new Error(message));
  }
);

export const authApi = {
  login: (username, password) => api.post('/auth/login', { username, password }),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  registerLibrarian: (data) => api.post('/auth/register-librarian', data),
};

export const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary'),
  getCharts: () => api.get('/dashboard/charts'),
};

export const booksApi = {
  list: (query = '', category = '') => api.get('/books', { params: { query, category } }),
  get: (bookId) => api.get(`/books/${bookId}`),
  create: (data) => api.post('/books', data),
  update: (bookId, data) => api.put(`/books/${bookId}`, data),
  delete: (bookId) => api.delete(`/books/${bookId}`),
  getCategories: () => api.get('/books/categories'),
  getFunctionalDemo: () => api.get('/books/functional-demo'),
  importFile: (formData) => api.post('/books/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

export const membersApi = {
  list: (query = '') => api.get('/members', { params: { query } }),
  get: (memberId) => api.get(`/members/${memberId}`),
  create: (data) => api.post('/members', data),
  update: (memberId, data) => api.put(`/members/${memberId}`, data),
  delete: (memberId) => api.delete(`/members/${memberId}`),
};

export const loansApi = {
  listAll: () => api.get('/loans'),
  listActive: () => api.get('/loans/active'),
  listOverdue: () => api.get('/loans/overdue'),
  issue: (data) => api.post('/loans/issue', data),
  returnBook: (loanId, returnDate = null) => api.post(`/loans/${loanId}/return`, { return_date: returnDate }),
};

export const analyticsApi = {
  getCategoryBreakdown: () => api.get('/analytics/category-breakdown'),
  getPriceStats: () => api.get('/analytics/price-stats'),
  getLoanDurationStats: () => api.get('/analytics/loan-duration-stats'),
  getPopularBooks: (topN = 10) => api.get('/analytics/popular-books', { params: { top_n: topN } }),
  getMonthlyTrends: () => api.get('/analytics/monthly-trends'),
};

export const googleBooksApi = {
  search: (query) => api.get('/google-books/search', { params: { q: query } }),
  importToCatalog: (data) => api.post('/google-books/import-catalog', data),
};

export const concurrencyApi = {
  runBenchmark: (simulations = 100000, chunks = 8) => 
    api.post('/concurrency/benchmark', { total_simulations: simulations, num_chunks: chunks }),
};

export default api;
