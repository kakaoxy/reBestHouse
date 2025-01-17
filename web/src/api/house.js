import { request } from '@/utils'

const baseUrl = '/house'

export const ershoufangApi = {
  list: (params = {}) => {
    console.log('Calling ershoufang API with params:', params)
    return request.get(`${baseUrl}/ershoufangs`, { 
      params: {
        ...params,
        community_id: Number(params.community_id)
      }
    })
  },
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
  list: (params = {}) => {
    console.log('Calling deal records API with params:', params)
    return request.get(`${baseUrl}/deal-records`, { 
      params: {
        ...params,
        community_id: Number(params.community_id)
      }
    })
  },
  create: (data) => request.post(`${baseUrl}/deal-records`, data),
  update: (id, data) => request.put(`${baseUrl}/deal-records/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/deal-records/${id}`)
}

export const opportunityApi = {
  list: (params = {}) => request.get(`${baseUrl}/opportunities`, { params }),
  getDetail: (id) => request.get(`${baseUrl}/opportunities/${id}`),
  create: (data) => request.post(`${baseUrl}/opportunities`, data),
  update: (id, data) => request.put(`${baseUrl}/opportunities/${id}`, data),
  delete: (id) => request.delete(`${baseUrl}/opportunities/${id}`),
  createFollowUp(data) {
    return request.post('/house/opportunity/follow_up/create', data)
  },
  getFollowUps(opportunityId) {
    return request.get(`/house/opportunity/${opportunityId}/follow_ups`)
  },
  uploadImage(formData) {
    return request.post('/house/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
} 