<template>
    <AppPage :show-footer="false">
      <div class="flex-1 px-6 py-4">
        <!-- 顶部欢迎卡片 -->
        <n-card class="welcome-card" :bordered="false">
          <div flex items-center justify-between>
            <div flex items-center>
              <img class="avatar" :src="userStore.avatar" />
              <div class="welcome-text">
                <p class="name">
                  {{ $t('views.workbench.text_hello', { username: userStore.name }) }}
                </p>
                <p class="subtitle">{{ $t('views.workbench.text_welcome') }}</p>
              </div>
            </div>
            <n-button
              type="primary"
              @click="showCalculator = true"
              class="calculator-btn"
            >
              投资计算器
            </n-button>
          </div>
        </n-card>
  
        <!-- 主要内容区域 -->
        <n-card
          :bordered="false"
          class="content-card"
        >
          <!-- <template #header-extra>
            <n-button text type="primary" class="more-btn">
              {{ $t('views.workbench.label_more') }}
            </n-button>
          </template> -->
          
          <div class="main-content">
            <!-- 左侧待评估列表 -->
            <div class="opportunity-list">
              <h3 class="section-title">待评估</h3>
              <n-spin :show="loading">
                <div class="cards-container">
                  <n-card
                    v-for="item in pendingOpportunities"
                    :key="item.id"
                    class="opportunity-card"
                    :class="{ 'opportunity-card--selected': selectedOpportunity?.id === item.id }"
                    :bordered="false"
                    @click="handleOpportunityClick(item)"
                  >
                    <div class="card-content">
                      <div class="header">
                        <span class="community-name">{{ item.community_name || '未知小区' }}</span>
                        <span class="price">{{ item.total_price ? `¥${item.total_price}万` : '待定' }}</span>
                      </div>
                      
                      <div class="details">
                         {{ item.layout || '--' }} · {{ item.floor || '--' }} · {{ item.area ? `${item.area}m²` : '--' }}
                      </div>
                      
                      <div class="stats">
                        <n-tag class="stat-tag" type="success">在售 {{ item.listing_count || 0 }}套</n-tag>
                        <n-tag class="stat-tag" type="info">成交 {{ item.deal_count || 0 }}套</n-tag>
                      </div>
                    </div>
                  </n-card>
                  
                  <n-empty
                    v-if="!loading && pendingOpportunities.length === 0"
                    description="暂无待评估商机"
                  />
                </div>
              </n-spin>
            </div>
  
            <!-- 更新报告区域 -->
            <div class="report-section">
              <h3 class="section-title">AI报告（基于DeepSeek R1模型）</h3>
              <n-card class="report-card" :bordered="false">
                <div v-if="selectedOpportunity" class="report-content">
                  <div class="selected-info">
                    <div class="flex items-center justify-between">
                      <div>
                        <span class="label">已选择商机：</span>
                        <span class="value">{{ selectedOpportunity.community_name }}</span>
                      </div>
                      <n-button
                        type="primary"
                        :loading="reportLoading"
                        @click="generateReport"
                        class="generate-btn"
                      >
                        {{ reportLoading ? '生成中...' : '生成AI报告' }}
                      </n-button>
                    </div>
                  </div>
                  <div class="report-body">
                    <n-spin :show="reportLoading">
                      <div v-if="reportContent" class="report-content-text">
                        <div class="report-text markdown-content" v-html="reportContent"></div>
                      </div>
                      <div v-else class="report-placeholder">
                        <p>
                          <span class="placeholder-text">点击上方按钮生成AI分析报告</span>
                        </p>
                      </div>
                    </n-spin>
                  </div>
                </div>
                <div v-else class="report-placeholder">
                  <p>
                    <span class="placeholder-text">请选择左侧商机查看详情</span>
                  </p>
                </div>
              </n-card>
            </div>
          </div>
        </n-card>
  
        <InvestmentCalculator :show="showCalculator" @update:show="showCalculator = $event" />
      </div>
    </AppPage>
  </template>
  
  <script setup>
  import { useUserStore } from '@/store'
  import { useI18n } from 'vue-i18n'
  import { ref, onMounted, computed } from 'vue'
  import InvestmentCalculator from '@/components/InvestmentCalculator.vue'
  import { opportunityApi } from '@/api/house'
  import { ershoufangApi, dealRecordApi } from '@/api/house'
  import { aiReportApi } from '@/api/ai'
  import { useMessage } from 'naive-ui'
  import { request } from '@/utils'  // 确保导入 request
  
  const dummyText = '售前美化房源信息后台管理系统'
  const { t } = useI18n({ useScope: 'global' })
  
  const userStore = useUserStore()
  const showCalculator = ref(false)
  
  // 待评估商机列表数据
  const pendingOpportunities = ref([])
  const loading = ref(false)
  
  // 获取同小区在售房源数量
  const getListingCount = async (communityId) => {
    try {
      const params = {
        community_id: communityId,
        page: 1,
        page_size: 1
      }
      const res = await ershoufangApi.list(params)
      return res.code === 200 ? res.data.total : 0
    } catch (error) {
      console.error('获取在售房源数量失败:', error)
      return 0
    }
  }
  
  // 获取同小区成交记录数量
  const getDealCount = async (communityId) => {
    try {
      const params = {
        community_id: communityId,
        page: 1,
        page_size: 1
      }
      const res = await dealRecordApi.list(params)
      return res.code === 200 ? res.data.total : 0
    } catch (error) {
      console.error('获取成交记录数量失败:', error)
      return 0
    }
  }
  
  // 获取待评估商机列表
  const fetchPendingOpportunities = async () => {
    loading.value = true
    try {
      const res = await opportunityApi.list({
        status: '待评估',
        page_size: 10,
        city: userStore.currentDepartment
      })
      console.log('待评估商机响应数据:', res)
      if (res.code === 200) {
        const items = res.data.items || []
        // 为每个商机获取在售和成交数量
        const itemsWithCounts = await Promise.all(
          items.map(async (item) => {
            const [listingCount, dealCount] = await Promise.all([
              getListingCount(item.community_id),
              getDealCount(item.community_id)
            ])
            return {
              ...item,
              listing_count: listingCount,
              deal_count: dealCount
            }
          })
        )
        pendingOpportunities.value = itemsWithCounts
      }
    } catch (error) {
      console.error('获取待评估商机列表失败:', error)
    } finally {
      loading.value = false
    }
  }
  const selectedOpportunity = ref(null)
  // 处理商机卡片点击
  const handleOpportunityClick = (item) => {
    selectedOpportunity.value = item
  }

  const reportLoading = ref(false)
  const reportContent = ref('')
  const message = useMessage()

  // 生成AI报告
  // ... existing code ...

  const generateReport = async () => {
    if (!selectedOpportunity.value) {
      message.warning('请先选择一个商机');
      return;
    }

    reportLoading.value = true;
    reportContent.value = '';

    try {
      const response = await request({
        url: 'ai/report/generate',
        method: 'POST',
        data: {
          opportunity_id: selectedOpportunity.value.id,
        },
        headers: {
          'Accept': 'text/event-stream',
        },
        responseType: 'text', // 修改为 text
        timeout: 180000,
        onDownloadProgress: (progressEvent) => {
          const rawText = progressEvent.event.target.responseText;
          const lines = rawText.split('\n');
          
          let newContent = '';
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6)); // 修改为 slice(6)
                if (data.content) {
                  newContent += data.content;
                  reportContent.value = newContent;
                }
                if (data.done) {
                  reportLoading.value = false;
                  message.success('报告生成成功');
                }
                if (data.error) {
                  throw new Error(data.error);
                }
              } catch (e) {
                // 忽略解析错误，继续处理下一行
                console.debug('解析行数据时出现非关键错误:', e);
              }
            }
          }
        }
      });
    } catch (err) {
      console.error('生成报告失败:', err);
      message.error(err.message === 'timeout of 180000ms exceeded' ? '生成报告超时，请稍后重试' : (err.message || '请求失败'));
      reportLoading.value = false;
    }
  };


  
  
  onMounted(() => {
    fetchPendingOpportunities()
  })
  </script>
  <style scoped>
  .welcome-card {
    /* background: linear-gradient(to right, #f7f7f7, #ffffff); */
    border-radius: 16px;
    margin-bottom: 24px;
  }
  
  .avatar {
    width: 60px;
    height: 60px;
    border-radius: 30px;
    object-fit: cover;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .welcome-text {
    margin-left: 20px;
  }
  
  .name {
    font-size: 24px;
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 4px;
  }
  
  .subtitle {
    font-size: 15px;
    color: #86868b;
  }
  
  .calculator-btn {
    height: 44px;
    padding: 0 24px;
    font-size: 15px;
    border-radius: 22px;
    /* background: #0071e3; */
    transition: all 0.2s ease;
  }
  
  .calculator-btn:hover {
    /* background: #0077ED; */
    transform: scale(1.02);
  }
  
  .content-card {
    border-radius: 16px;
    background: #ffffff;
    height: calc(100vh - 200px); /* 减去顶部卡片和padding的高度 */
    overflow: auto; /* 内容超出时显示滚动条 */
  }
  
  .main-content {
    display: flex;
    gap: 32px;
  }
  
  .opportunity-list {
    width: 35%;
    padding-right: 32px;
    border-right: 1px solid #f2f2f2;
  }
  
  .section-title {
    font-size: 20px;
    font-weight: 600;
    color: #1d1d1f;
    margin-bottom: 20px;
  }
  
  .cards-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .opportunity-card {
    border-radius: 12px;
    background: #ffffff;
    transition: all 0.3s ease;
  }
  
  .opportunity-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }
  
  .card-content {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .community-name {
    font-size: 17px;
    font-weight: 600;
    color: #1d1d1f;
  }
  
  .price {
    font-size: 17px;
    font-weight: 600;
    color: #0071e3;
  }
  
  .details {
    font-size: 15px;
    color: #86868b;
  }
  
  .stats {
    display: flex;
    gap: 8px;
  }
  
  .stat-tag {
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 13px;
  }
  
  .report-section {
    flex: 1;
  }
  
  .report-card {
    border-radius: 12px;
    background: #ffffff;
  }
  
  .report-placeholder {
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
  
  .placeholder-text {
    font-size: 17px;
    color: #86868b;
    margin-bottom: 8px;
    display: block;
  }
  
  .placeholder-hint {
    font-size: 13px;
    color: #98989d;
  }
  
  :deep(.n-card) {
    transition: all 0.3s ease;
  }
  
  :deep(.n-button) {
    font-weight: 500;
  }
  
  :deep(.n-tag) {
    border: none;
  }

  .opportunity-card--selected {
  border: 2px solid #0071e3;
  background-color: rgba(0, 113, 227, 0.05);
}

.opportunity-card--selected:hover {
  transform: none;
}

.selected-info {
  padding: 16px;
  border-radius: 8px;
  background-color: #f5f5f7;
  margin-bottom: 16px;
}

.selected-info .label {
  color: #86868b;
  font-size: 15px;
}

.selected-info .value {
  color: #1d1d1f;
  font-size: 17px;
  font-weight: 600;
  margin-left: 8px;
}
.report-content-text {
  padding: 20px;
  line-height: 1.6;
}

.markdown-content {
  color: #1d1d1f;
  font-size: 15px;
}

.markdown-content :deep(strong),
.markdown-content :deep(b) {
  color: #000000;
  font-weight: 600;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  color: #1d1d1f;
  font-weight: 600;
  margin: 16px 0 8px;
}

.report-body {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
  padding: 16px;
}
</style>