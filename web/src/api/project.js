import { request } from '@/utils'

const baseUrl = '/house/projects'

export const projectApi = {
  list: (params = {}) => request.get(baseUrl, { params }),
  create: (data) => request.post(baseUrl, data),
  update: (id, data) => request.put(`${baseUrl}/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/${id}`),
  getDetail: (id) => request.get(`${baseUrl}/${id}`),
  getPhases: (projectId) => request.get(`${baseUrl}/${projectId}/phases`),
  getPhaseMaterials: (phaseId) => request.get(`${baseUrl}/phases/${phaseId}/materials`)
} 