import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/v1',
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
}

export const siteAPI = {
  list: () => api.get('/sites/'),
  get: (siteId) => api.get(`/sites/${siteId}`),
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
  rate: (pageId, score) => api.post(`/ratings/page/${pageId}?score=${score}`),
  delete: (pageId) => api.delete(`/ratings/page/${pageId}`),
}

export default api