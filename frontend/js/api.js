// Always call the same host:port the page was served from
const API_BASE = window.location.origin;

// ─── Token helpers ─────────────────────────────────────────────
export function getToken() { return localStorage.getItem('token'); }
export function getUser() { const u = localStorage.getItem('user'); return u ? JSON.parse(u) : null; }
export function setAuth(token, user) {
  localStorage.setItem('token', token);
  localStorage.setItem('user', JSON.stringify(user));
}
export function clearAuth() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
}
export function isLoggedIn() { return !!getToken(); }
export function isAdmin() { const u = getUser(); return u && u.role === 'admin'; }

// ─── Core fetch wrapper ────────────────────────────────────────
async function request(path, { method = 'GET', body, auth = false } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const tok = getToken();
    if (tok) headers['Authorization'] = `Bearer ${tok}`;
  }
  const opts = { method, headers };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${path}`, opts);
  let data;
  try { data = await res.json(); } catch { data = {}; }

  if (!res.ok) {
    const detail = data?.detail;
    let msg = 'Request failed';
    if (typeof detail === 'string') msg = detail;
    else if (detail?.message) msg = detail.message;
    else if (Array.isArray(detail)) msg = detail.map(d => d.msg || d.message || JSON.stringify(d)).join('; ');
    else if (detail) msg = JSON.stringify(detail);
    const err = new Error(msg);
    err.status = res.status;
    err.code = detail?.code || 'API_ERROR';
    throw err;
  }
  return data;
}

// ─── Auth API ──────────────────────────────────────────────────
export const authAPI = {
  register: (body) => request('/auth/register', { method: 'POST', body }),
  login: (body) => request('/auth/login', { method: 'POST', body }),
  me: () => request('/auth/me', { auth: true }),
};

// ─── Events API ────────────────────────────────────────────────
export const eventsAPI = {
  list: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined && v !== '' && v !== false))
    ).toString();
    return request(`/events${qs ? '?' + qs : ''}`);
  },
  get: (id) => request(`/events/${id}`),
  create: (body) => request('/events', { method: 'POST', body, auth: true }),
  update: (id, body) => request(`/events/${id}`, { method: 'PATCH', body, auth: true }),
  delete: (id) => request(`/events/${id}`, { method: 'DELETE', auth: true }),
};

// ─── Clubs API ─────────────────────────────────────────────────
export const clubsAPI = {
  list: () => request('/clubs'),
  get: (id) => request(`/clubs/${id}`),
  create: (body) => request('/clubs', { method: 'POST', body, auth: true }),
  update: (id, body) => request(`/clubs/${id}`, { method: 'PATCH', body, auth: true }),
};

// ─── Registrations API ─────────────────────────────────────────
export const registrationsAPI = {
  myRegistrations: () => request('/registrations/me', { auth: true }),
  register: (event_id) => request('/registrations', { method: 'POST', body: { event_id }, auth: true }),
  cancel: (regId) => request(`/registrations/${regId}`, { method: 'DELETE', auth: true }),
  eventRegistrations: (eventId) => request(`/registrations/events/${eventId}`, { auth: true }),
};
