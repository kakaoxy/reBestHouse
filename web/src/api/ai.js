import { request } from '@/utils'

const baseUrl = '/ai'

export const aiReportApi = {
  // 生成AI报告
  generate: (data) => {
    return request.post(`${baseUrl}/report/generate`, data)
  }
}