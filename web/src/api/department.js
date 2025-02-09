import { request } from '@/utils'

export const departmentApi = {
  // 获取部门列表
  list: () => request.get('/dept/list'),
  // 获取当前用户信息（包含部门信息）
  getCurrentUserInfo: () => request.get('/base/userinfo'),
  // 获取部门详情
  getDeptInfo: (id) => request.get('/dept/get', { params: { id } })
}
