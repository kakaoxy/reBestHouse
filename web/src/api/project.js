import { request } from '@/utils'

const baseUrl = '/projects'

export const projectApi = {
  list: (params = {}) => request.get(baseUrl, { params }),
  create: (data) => request.post(baseUrl, data),
  update: (id, data) => request.put(`${baseUrl}/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/${id}`),
  getDetail: (id) => request.get(`${baseUrl}/${id}`)
} 