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

export const dealRecordApi = {
  list: (params = {}) => request.get(`${baseUrl}/deal-records`, { params }),
  create: (data) => request.post(`${baseUrl}/deal-records`, data),
  update: (id, data) => request.put(`${baseUrl}/deal-records/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/deal-records/${id}`)
}

export const opportunityApi = {
  list: (params = {}) => request.get(`${baseUrl}/opportunities`, { params }),
  getDetail: (id) => request.get(`${baseUrl}/opportunities/${id}`),
  create: (data) => request.post(`${baseUrl}/opportunities`, data),
  update: (id, data) => request.put(`${baseUrl}/opportunities/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/opportunities/${id}`)
} 