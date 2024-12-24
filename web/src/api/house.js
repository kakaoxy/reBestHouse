import { request } from '@/utils'

const baseUrl = '/house'

export const ershoufangApi = {
  list: (params = {}) => request.get(`${baseUrl}/ershoufangs`, { params }),
  create: (data) => request.post(`${baseUrl}/ershoufangs`, data),
  update: (id, data) => request.put(`${baseUrl}/ershoufangs/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/ershoufangs/${id}`)
}

export const communityApi = {
  list: (params = {}) => request.get(`${baseUrl}/communities`, { params }),
  create: (data) => request.post(`${baseUrl}/communities`, data),
  update: (id, data) => request.put(`${baseUrl}/communities/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/communities/${id}`)
} 