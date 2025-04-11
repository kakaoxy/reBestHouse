import { request } from '@/utils'

const baseUrl = '/api/ai'

export const aiReportApi = {
  // 生成AI报告
  generate: (data) => {
    return fetch(`${baseUrl}/report/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify(data)
    })
  }
}
