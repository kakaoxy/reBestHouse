import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { departmentApi } from '@/api/department'
import { useUserStore } from '@/store/modules/user'

export const useDepartmentStore = defineStore('department', () => {
  const currentDepartment = ref() // 初始值为空
  const departments = ref([]) // 初始为空数组
  const userStore = useUserStore()

  // 获取部门选项
  const getDepartmentOptions = async () => {
    try {
      const res = await departmentApi.list()
      if (res.code === 200 && res.data && res.data.length > 0) {
        // 先找到后端返回的上海部门
        const shanghaiDept = res.data.find(dept => dept.name === '上海')
        // 如果后端有上海部门，使用它的配置，否则使用默认配置
        const shanghaiOption = shanghaiDept
          ? { label: shanghaiDept.name, value: shanghaiDept.desc || 'shanghai' }
          : { label: '上海', value: 'shanghai' }

        // 过滤掉所有的上海选项，转换其他部门数据
        const otherOptions = res.data
          .filter(dept => dept.name !== '上海')
          .map(dept => {
            // 确保每个部门都有desc（拼音）
            if (!dept.desc) {
              console.warn(`部门 ${dept.name} 缺少拼音描述，将使用名称小写作为值`)
            }
            return {
              label: dept.name,
              value: dept.desc || dept.name.toLowerCase()
            }
          })

        // 将上海选项放在最前面
        departments.value = [shanghaiOption, ...otherOptions]
      } else {
        // 如果没有数据，使用默认的上海选项
        departments.value = [{ label: '上海', value: 'shanghai' }]
      }
      return departments.value
    } catch (error) {
      console.error('获取部门列表失败:', error)
      // 如果获取失败，使用默认的上海选项
      departments.value = [{ label: '上海', value: 'shanghai' }]
      return departments.value
    }
  }

  // 初始化当前部门
  const initCurrentDepartment = async () => {
    try {
      // 确保部门列表已加载
      if (departments.value.length === 0) {
        await getDepartmentOptions()
      }

      // 获取当前用户信息
      const userInfo = await departmentApi.getCurrentUserInfo()
      if (userInfo.code === 200 && userInfo.data?.dept_id) {
        // 如果用户有部门，获取部门详情
        const deptInfo = await departmentApi.getDeptInfo(userInfo.data.dept_id)
        if (deptInfo.code === 200 && deptInfo.data) {
          // 使用部门的desc作为value，如果没有desc则使用名称小写
          currentDepartment.value = deptInfo.data.desc || deptInfo.data.name.toLowerCase()
          return
        }
      }
      
      // 如果用户没有部门或获取部门信息失败，使用默认值（上海）
      const shanghaiDept = departments.value.find(dept => dept.label === '上海')
      currentDepartment.value = shanghaiDept?.value || 'shanghai'
    } catch (error) {
      console.error('获取当前部门失败:', error)
      // 确保即使出错也使用默认值
      currentDepartment.value = 'shanghai'
    }
  }

  // 获取当前部门的显示名称
  const getCurrentDepartmentLabel = computed(() => {
    const dept = departments.value.find(d => d.value === currentDepartment.value)
    return dept?.label || '上海'
  })

  const setDepartment = (value) => {
    currentDepartment.value = value
  }

  return {
    currentDepartment,
    departments,
    getCurrentDepartmentLabel,
    getDepartmentOptions,
    initCurrentDepartment,
    setDepartment
  }
})
