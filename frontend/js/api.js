const API_BASE = 'https://course-platform-zyx4.onrender.com';

const TokenManager = {
  get: () => localStorage.getItem('access_token'),
  set: (token) => localStorage.setItem('access_token', token),
  remove: () => localStorage.removeItem('access_token'),
  getUser: () => { const d = localStorage.getItem('user_data'); return d ? JSON.parse(d) : null; },
  setUser: (data) => localStorage.setItem('user_data', JSON.stringify(data)),
  removeUser: () => localStorage.removeItem('user_data'),
  isLoggedIn: () => !!localStorage.getItem('access_token'),
  isAdmin: () => { const u = TokenManager.getUser(); return u && u.role === 'admin'; }
};

async function apiRequest(endpoint, options = {}) {
  const token = TokenManager.get();
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers
  };
  if (options.body instanceof FormData) delete headers['Content-Type'];
  const config = {
    ...options,
    headers,
    body: options.body instanceof FormData ? options.body : options.body ? JSON.stringify(options.body) : undefined
  };
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, config);
    if (response.status === 401) {
      TokenManager.remove();
      TokenManager.removeUser();
      if (!window.location.href.includes('login')) window.location.href = '/login.html';
      return null;
    }
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
    return data;
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch'))
      throw new Error('Cannot connect to server. Please try again.');
    throw error;
  }
}

const AuthAPI = {
  register: (data) => apiRequest('/api/auth/register', { method: 'POST', body: data }),
  login: (data) => apiRequest('/api/auth/login', { method: 'POST', body: data }),
  me: () => apiRequest('/api/auth/me'),
};

const CoursesAPI = {
  list: () => apiRequest('/api/courses/'),
  get: (id) => apiRequest(`/api/courses/${id}`),
  getDownload: (id) => apiRequest(`/api/courses/${id}/download`),
  create: (data) => apiRequest('/api/courses/admin/create', { method: 'POST', body: data }),
  update: (id, data) => apiRequest(`/api/courses/admin/${id}`, { method: 'PUT', body: data }),
  delete: (id) => apiRequest(`/api/courses/admin/${id}`, { method: 'DELETE' }),
  adminList: () => apiRequest('/api/courses/admin/all/list'),
};

const PaymentsAPI = {
  getQR: (courseId) => apiRequest(`/api/payments/qr/${courseId}`),
  submitPayment: (courseId, formData) => apiRequest(`/api/payments/submit/${courseId}`, { method: 'POST', body: formData, headers: {} }),
  myPayments: () => apiRequest('/api/payments/my-payments'),
};

const AdminAPI = {
  stats: () => apiRequest('/api/admin/stats'),
  payments: (status = null) => apiRequest(`/api/admin/payments${status ? `?status=${status}` : ''}`),
  verifyPayment: (id, data) => apiRequest(`/api/admin/payments/${id}/verify`, { method: 'POST', body: data }),
  screenshot: (id) => `${API_BASE}/api/admin/screenshot/${id}`,
  users: () => apiRequest('/api/admin/users'),
};
