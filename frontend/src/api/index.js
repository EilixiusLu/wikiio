import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL,
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error.response?.data || error)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  verifyEmail: (token) => api.get(`/auth/verify-email/${token}`),
}

export const userAPI = {
  getMe: () => api.get('/users/me'),
  fandomBindStart: (fandomUsername) =>
    api.post(`/users/fandom/bind/start?fandom_username=${encodeURIComponent(fandomUsername)}`),
  fandomBindVerify: () => api.post('/users/fandom/bind/verify'),
  fandomUnbind: () => api.delete('/users/fandom/unbind'),
  mirahezeBindStart: (mhUsername) =>
    api.post(`/users/miraheze/bind/start?miraheze_username=${encodeURIComponent(mhUsername)}`),
  mirahezeBindVerify: () => api.post('/users/miraheze/bind/verify'),
  mirahezeUnbind: () => api.delete('/users/miraheze/unbind'),
}

export const siteAPI = {
  list: () => api.get('/sites/'),
  get: (siteId) => api.get(`/sites/${siteId}`),
  create: (data) => api.post('/sites/', data),
  delete: (siteId) => api.delete(`/sites/${siteId}`),
  triggerCrawl: (siteId, full = false) => api.post(`/sites/${siteId}/crawl?full=${full}`),
}

export const pageAPI = {
  list: (params) => api.get('/pages/', { params }),
  get: (id) => api.get(`/pages/${id}`),
  stats: (siteId) => api.get('/pages/stats', { params: { site_id: siteId } }),
  topAuthors: (siteId, limit = 10) => api.get('/pages/top-authors', { params: { site_id: siteId, limit } }),
  count: (siteId) => api.get('/pages/count', { params: { site_id: siteId } }),
  rankingByRating: (siteId, skip = 0, limit = 50) =>
    api.get('/pages/rankings/by-rating', { params: { site_id: siteId, skip, limit } }),
  rankingByAuthor: (siteId, orderBy = 'page_count', skip = 0, limit = 50) =>
    api.get('/pages/rankings/by-author', { params: { site_id: siteId, order_by: orderBy, skip, limit } }),
  rankingBySiteRating: (siteId, skip = 0, limit = 50) =>
    api.get('/pages/rankings/by-site-rating', { params: { site_id: siteId, skip, limit } }),
  authorPages: (author, siteId = null, skip = 0, limit = 20) =>
    api.get(`/pages/author/${encodeURIComponent(author)}`, {
      params: { site_id: siteId || undefined, skip, limit }
    }),
  authorStats: (author) =>
    api.get(`/pages/author/${encodeURIComponent(author)}/stats`),
  authorProfile: (author) =>
    api.get(`/pages/author/${encodeURIComponent(author)}/profile`),
  siteRating: (pageId) => api.get(`/pages/${pageId}/site-rating`),
}

export const ratingAPI = {
  get: (pageId) => api.get(`/ratings/page/${pageId}`),
  getMine: (pageId) => api.get(`/ratings/page/${pageId}/mine`),
  rate: (pageId, score) => api.post(`/ratings/page/${pageId}`, { score }),
  delete: (pageId) => api.delete(`/ratings/page/${pageId}`),
}

export const searchAPI = {
  search: (params) => api.get('/search/', { params }),
  categories: (siteId) => api.get('/search/categories', { params: { site_id: siteId } }),
}

export const adminAPI = {
  stats: () => api.get('/admin/stats'),
  logs: (logType, lines = 200) => api.get(`/admin/logs/${logType}?lines=${lines}`),
  sites: () => api.get('/admin/sites'),
  approveSite: (siteId) => api.post(`/admin/sites/${siteId}/approve`),
  rejectSite: (siteId) => api.post(`/admin/sites/${siteId}/reject`),
}

export default api