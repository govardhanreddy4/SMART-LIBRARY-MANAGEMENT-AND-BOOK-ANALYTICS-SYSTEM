import assert from 'node:assert';

/**
 * URL resolution logic from frontend/src/api/client.js
 */
function resolveBaseURL(envValue) {
  const rawBaseURL = (envValue || '/api').trim();
  const cleanBaseURL = rawBaseURL.endsWith('/') ? rawBaseURL.slice(0, -1) : rawBaseURL;
  const baseURL = (cleanBaseURL.startsWith('http') && !cleanBaseURL.endsWith('/api'))
    ? `${cleanBaseURL}/api`
    : cleanBaseURL;
  return baseURL;
}

function getApiUrl(baseURL, path = '') {
  let cleanPath = path.startsWith('/') ? path : `/${path}`;
  if (baseURL.endsWith('/api') && cleanPath.startsWith('/api/')) {
    cleanPath = cleanPath.slice(4);
  }
  return `${baseURL}${cleanPath}`;
}

// 1. Verify local development fallback when VITE_API_URL is unset
assert.strictEqual(resolveBaseURL(undefined), '/api', 'Failed on undefined VITE_API_URL');
assert.strictEqual(resolveBaseURL(''), '/api', 'Failed on empty VITE_API_URL');

// 2. Verify production URL as configured in Vercel
const prodEnv = 'https://smart-library-management-and-book.onrender.com/api';
assert.strictEqual(resolveBaseURL(prodEnv), prodEnv, 'Failed on canonical Vercel VITE_API_URL');

// 3. Verify production URL with accidental trailing slash
const prodEnvTrailing = 'https://smart-library-management-and-book.onrender.com/api/';
assert.strictEqual(resolveBaseURL(prodEnvTrailing), prodEnv, 'Failed to strip trailing slash');

// 4. Verify production URL if user enters domain root without /api
const prodEnvNoSubpath = 'https://smart-library-management-and-book.onrender.com';
assert.strictEqual(resolveBaseURL(prodEnvNoSubpath), prodEnv, 'Failed to normalize missing /api');

// 5. Verify production login request destination URL
const prodBase = resolveBaseURL(prodEnv);
const loginFullUrl = `${prodBase}/auth/login`;
assert.strictEqual(
  loginFullUrl,
  'https://smart-library-management-and-book.onrender.com/api/auth/login',
  'Production login URL did not match expected Render destination'
);

// 6. Verify export URL construction for production and local dev
assert.strictEqual(
  getApiUrl(prodBase, '/books/export/csv'),
  'https://smart-library-management-and-book.onrender.com/api/books/export/csv',
  'Export URL failed in production'
);
assert.strictEqual(
  getApiUrl('/api', '/books/export/csv'),
  '/api/books/export/csv',
  'Export URL failed in local dev'
);

console.log('✅ ALL API CLIENT URL CONSTRUCTION AND RESOLUTION TESTS PASSED.');
