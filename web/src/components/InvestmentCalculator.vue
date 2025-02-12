<template>
  <n-modal
    :show="show"
    @update:show="emit('update:show', $event)"
    :title="'投资计算器'"
    preset="card"
    class="max-w-900px w-900px investment-calculator-modal"
    :mask-closable="false"
    style="font-size: 16px;"
  >
    <n-form
      ref="formRef"
      :model="formValue"
      :rules="rules"
      label-placement="left"
      label-width="auto"
      require-mark-placement="right-hanging"
      size="large"
      class="calculator-form"
    >
      <div class="grid grid-cols-3 gap-8">
        <n-form-item label="房屋总价（万元）" path="totalPrice">
          <n-input-number
            v-model:value="formValue.totalPrice"
            :min="0"
            :step="1"
            placeholder="请输入房屋总价"
            class="w-full"
          />
        </n-form-item>
        <n-form-item label="建筑面积（平方米）" path="area">
          <n-input-number
            v-model:value="formValue.area"
            :min="0"
            :step="1"
            placeholder="请输入建筑面积"
            class="w-full"
          />
        </n-form-item>
        <n-form-item label="预期售价（万元）" path="expectedPrice">
          <n-input-number
            v-model:value="formValue.expectedPrice"
            :min="0"
            :step="1"
            placeholder="请输入预期售价"
            class="w-full"
          />
        </n-form-item>
        <n-form-item label="销售周期（月）" path="salesCycle">
          <n-input-number
            v-model:value="formValue.salesCycle"
            :min="0"
            :step="1"
            placeholder="请输入销售周期"
            class="w-full"
          />
        </n-form-item>
        <n-form-item label="商户投资占比（%）" path="merchantRatio">
          <n-input-number
            v-model:value="formValue.merchantRatio"
            :min="0"
            :max="100"
            :step="1"
            placeholder="请输入商户投资占比"
            class="w-full"
          />
        </n-form-item>
        <n-form-item label="资方是否跟投" path="hasInvestor">
          <n-switch v-model:value="formValue.hasInvestor" class="mt-2" />
        </n-form-item>
      </div>
    </n-form>

    <div class="flex justify-center mt-10">
      <n-button 
        type="primary" 
        size="large" 
        @click="calculate"
        class="calculate-button px-8"
      >
        计算投资回报
      </n-button>
    </div>

    <template v-if="showResults">
      <div class="mt-12 border-t border-gray-100 pt-10">
        <h3 class="mb-8 font-medium tracking-tight text-gray-900">基础费用</h3>
        <div class="grid grid-cols-2 gap-8 bg-gray-50 rounded-2xl p-8">
          <div v-for="(value, key) in basicCosts" :key="key" class="flex justify-between items-center px-72">
            <span class="text-gray-600 text-[16px]">{{ labels[key] }}</span>
            <span class="font-medium text-[16px] text-gray-900">{{ formatMoney(value) }}</span>
          </div>
          <div class="col-span-2 flex justify-between border-t border-gray-200 pt-6 mt-4 px-72">
            <span class="text-[18px] font-medium text-gray-900">总投资</span>
            <span class="text-[18px] font-semibold text-blue-600">{{ formatMoney(totalInvestment) }}</span>
          </div>
        </div>
      </div>

      <div class="mt-12 border-t border-gray-100 pt-10">
        <h3 class="mb-8 font-medium tracking-tight text-gray-900">收益分配</h3>
        <div :class="['grid gap-8', formValue.hasInvestor ? 'grid-cols-3' : 'grid-cols-2']">
          <n-card title="商户方" class="investment-card">
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">投资金额</span>
                <span class="text-[18px] font-medium text-blue-600">{{ formatMoney(merchantInvestment) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">回款金额</span>
                <span class="text-[18px] font-medium" :class="merchantProfit >= 0 ? 'text-red-600' : 'text-green-600'">{{ formatMoney(merchantReturn) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">利润</span>
                <span class="text-[18px] font-medium" :class="merchantProfit >= 0 ? 'text-red-600' : 'text-green-600'">
                  {{ formatMoney(merchantProfit) }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">投资回报率</span>
                <span class="text-[18px] font-medium text-blue-600">{{ merchantRate }}%</span>
              </div>
            </div>
          </n-card>

          <n-card title="美化方" class="investment-card">
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">投资金额</span>
                <span class="text-[18px] font-medium text-blue-600">{{ formatMoney(platformInvestment) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">回款金额</span>
                <span class="text-[18px] font-medium" :class="platformProfit >= 0 ? 'text-red-600' : 'text-green-600'">{{ formatMoney(platformReturn) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">利润</span>
                <span class="text-[18px] font-medium" :class="platformProfit >= 0 ? 'text-red-600' : 'text-green-600'">
                  {{ formatMoney(platformProfit) }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">投资回报率</span>
                <span class="text-[18px] font-medium text-blue-600">{{ platformRate }}%</span>
              </div>
            </div>
          </n-card>

          <n-card v-if="formValue.hasInvestor" title="资方" class="investment-card">
            <div class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">投资金额</span>
                <span class="text-[18px] font-medium text-blue-600">{{ formatMoney(investorInvestment) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">回款金额</span>
                <span class="text-[18px] font-medium" :class="investorProfit >= 0 ? 'text-red-600' : 'text-green-600'">{{ formatMoney(investorReturn) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">利润</span>
                <span class="text-[18px] font-medium" :class="investorProfit >= 0 ? 'text-red-600' : 'text-green-600'">
                  {{ formatMoney(investorProfit) }}
                </span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-[15px] text-gray-500">投资回报率</span>
                <span class="text-[18px] font-medium text-blue-600">{{ investorRate }}%</span>
              </div>
            </div>
          </n-card>
        </div>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMessage } from 'naive-ui'

const message = useMessage()
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show'])

const formRef = ref(null)
const showResults = ref(false)
const warnings = ref([])

// 表单数据
const formValue = ref({
  totalPrice: 200, // 房屋总价（万元）
  area: 55, // 建筑面积（平方米）
  expectedPrice: 230, // 预期售价（万元）
  salesCycle: 4, // 销售周期（月）
  merchantRatio: 50, // 商户投资占比（%）
  hasInvestor: true // 资方是否跟投
})

const rules = {
  totalPrice: { required: true, message: '请输入房屋总价' },
  area: { required: true, message: '请输入建筑面积' },
  expectedPrice: { required: true, message: '请输入预期售价' },
  salesCycle: { required: true, message: '请输入销售周期' },
  merchantRatio: { required: true, message: '请输入商户投资占比' }
}

// 验证输入
const validateInputs = () => {
  const newWarnings = []
  if (!formValue.value.totalPrice || formValue.value.totalPrice <= 0) {
    newWarnings.push('请输入有效的房屋总价')
  }
  if (!formValue.value.area || formValue.value.area <= 0) {
    newWarnings.push('请输入有效的建筑面积')
  }
  if (!formValue.value.expectedPrice || formValue.value.expectedPrice <= 0) {
    newWarnings.push('请输入有效的预期售价')
  }
  if (!formValue.value.salesCycle || formValue.value.salesCycle <= 0) {
    newWarnings.push('请输入有效的销售周期')
  }
  if (!formValue.value.merchantRatio || formValue.value.merchantRatio <= 0 || formValue.value.merchantRatio >= 100) {
    newWarnings.push('请输入有效的商户占比（1-99）')
  }
  warnings.value = newWarnings
  return newWarnings.length === 0
}

// 标签映射
const labels = {
  purchaseCommission: '收房佣金(上限4万)',
  saleCommission: '代理人佣金(0.5%)',
  renovationCost: '装修费用',
  operationalCost: '运营费用'
}

// 基础费用计算
const basicCosts = computed(() => {
  // 收房佣金：1%，但最高不超过4万
  const purchaseCommission = Math.min(formValue.value.totalPrice * 0.01 * 10000, 40000) / 10000

  // 装修费用：每平米2200元
  const renovationCost = (formValue.value.area * 2200) / 10000

  // 代理人佣金：0.5%
  const saleCommission = formValue.value.expectedPrice * 0.005

  // 计算溢价
  const premium = formValue.value.expectedPrice - formValue.value.totalPrice
  const totalBasicCost = purchaseCommission + renovationCost + saleCommission

  // 运营费用：如果有溢价，取溢价和预期售价1%的较小值
  const maxOperationalCost = formValue.value.expectedPrice * 0.01
  const remainingPremium = premium - totalBasicCost
  const operationalCost = remainingPremium > 0 ? Math.min(remainingPremium, maxOperationalCost) : 0

  return {
    purchaseCommission,
    renovationCost,
    saleCommission,
    operationalCost
  }
})

// 总投资
const totalInvestment = computed(() => {
  const costs = basicCosts.value
  return Object.values(costs).reduce((sum, cost) => sum + cost, 0)
})

// 溢价金额
const premium = computed(() => {
  return formValue.value.expectedPrice - formValue.value.totalPrice
})

// 计算各方投资和收益
const calculateInvestmentAndReturns = computed(() => {
  const totalInvestmentValue = totalInvestment.value
  const premiumValue = premium.value
  const meifangbaoRatio = (100 - formValue.value.merchantRatio) / 100

  // 投资金额计算
  let merchantInvestment = totalInvestmentValue * (formValue.value.merchantRatio / 100)
  let meifangbaoInvestment, investorInvestment

  if (formValue.value.hasInvestor) {
    // 有资方跟投
    meifangbaoInvestment = totalInvestmentValue * meifangbaoRatio * 0.3
    investorInvestment = totalInvestmentValue * meifangbaoRatio * 0.7
  } else {
    // 无资方跟投
    meifangbaoInvestment = totalInvestmentValue * meifangbaoRatio
    investorInvestment = 0
  }

  // 利润计算
  const totalProfit = premiumValue * 10000 - totalInvestmentValue * 10000
  let merchantProfit = 0
  let meifangbaoProfit = 0
  let investorProfit = 0

  if (formValue.value.hasInvestor) {
    if (premiumValue * 10000 < totalInvestmentValue * 10000) {
      // 亏损情况
      const totalLoss = premiumValue * 10000 - totalInvestmentValue * 10000
      merchantProfit = totalLoss / 2
      const meifangbaoSideLoss = totalLoss / 2

      if (Math.abs(meifangbaoSideLoss) <= meifangbaoInvestment * 10000) {
        meifangbaoProfit = meifangbaoSideLoss
        investorProfit = 0
      } else {
        meifangbaoProfit = -meifangbaoInvestment * 10000
        investorProfit = meifangbaoSideLoss + meifangbaoInvestment * 10000
      }
    } else if (totalProfit > 0) {
      // 盈利情况
      // 资方最低收益要求
      const investorMinReturn = investorInvestment * 10000 * 0.08 * (formValue.value.salesCycle / 12)
      const meifangbaoTotalProfit = totalProfit * (1 - formValue.value.merchantRatio / 100)

      if (meifangbaoTotalProfit >= investorMinReturn) {
        investorProfit = investorMinReturn
        const remainingProfit = meifangbaoTotalProfit - investorMinReturn
        investorProfit += remainingProfit * 0.3
        meifangbaoProfit = remainingProfit * 0.7
      } else {
        investorProfit = meifangbaoTotalProfit
        meifangbaoProfit = 0
        warnings.value.push('提示：总利润不足以支付资方最低收益要求')
      }
      merchantProfit = totalProfit * (formValue.value.merchantRatio / 100)
    }
  } else {
    // 无资方跟投时的利润分配
    merchantProfit = totalProfit * (formValue.value.merchantRatio / 100)
    meifangbaoProfit = totalProfit * (1 - formValue.value.merchantRatio / 100)
    investorProfit = 0
  }

  // 计算各方回款
  const merchantReturn = (merchantInvestment * 10000 + merchantProfit) / 10000
  const meifangbaoReturn = (meifangbaoInvestment * 10000 + meifangbaoProfit) / 10000
  const investorReturn = (investorInvestment * 10000 + investorProfit) / 10000

  // 计算投资回报率
  const merchantRate = calculateReturnRate(merchantReturn * 10000, merchantInvestment * 10000)
  const meifangbaoRate = calculateReturnRate(meifangbaoReturn * 10000, meifangbaoInvestment * 10000)
  const investorRate = calculateReturnRate(investorReturn * 10000, investorInvestment * 10000)

  return {
    merchantInvestment,
    meifangbaoInvestment,
    investorInvestment,
    merchantReturn,
    meifangbaoReturn,
    investorReturn,
    merchantProfit: merchantProfit / 10000,
    meifangbaoProfit: meifangbaoProfit / 10000,
    investorProfit: investorProfit / 10000,
    merchantRate,
    meifangbaoRate,
    investorRate
  }
})

// 计算收益率
const calculateReturnRate = (totalReturn, investment) => {
  if (!investment) return 0
  return Math.round((totalReturn / investment - 1) * 100)
}

// 商户投资和收益
const merchantInvestment = computed(() => calculateInvestmentAndReturns.value.merchantInvestment)
const merchantReturn = computed(() => calculateInvestmentAndReturns.value.merchantReturn)
const merchantProfit = computed(() => calculateInvestmentAndReturns.value.merchantProfit)
const merchantRate = computed(() => calculateInvestmentAndReturns.value.merchantRate)

// 平台投资和收益
const platformInvestment = computed(() => calculateInvestmentAndReturns.value.meifangbaoInvestment)
const platformReturn = computed(() => calculateInvestmentAndReturns.value.meifangbaoReturn)
const platformProfit = computed(() => calculateInvestmentAndReturns.value.meifangbaoProfit)
const platformRate = computed(() => calculateInvestmentAndReturns.value.meifangbaoRate)

// 资方投资和收益
const investorInvestment = computed(() => calculateInvestmentAndReturns.value.investorInvestment)
const investorReturn = computed(() => calculateInvestmentAndReturns.value.investorReturn)
const investorProfit = computed(() => calculateInvestmentAndReturns.value.investorProfit)
const investorRate = computed(() => calculateInvestmentAndReturns.value.investorRate)

// 格式化金额
const formatMoney = (value) => {
  return value.toFixed(2) + '万'
}

// 计算按钮点击事件
const calculate = () => {
  if (validateInputs()) {
    showResults.value = true
  }
}

const handleSave = () => {
  calculate()
  emit('update:show', false)
}

const handleCancel = () => {
  emit('update:show', false)
}
</script>

<style scoped>
.investment-calculator-modal {
  --n-border-radius: 16px;
  --n-padding: 32px;
}

.calculator-form :deep(.n-form-item .n-form-item-label) {
  font-size: 15px;
  color: #374151;
}

.calculate-button {
  border-radius: 10px;
  font-weight: 500;
  height: 44px;
}

.investment-card {
  --n-border-radius: 16px;
  --n-padding: 24px;
  --n-title-font-size: 18px;
  --n-title-font-weight: 600;
  --n-title-text-color: #1F2937;
  border: 1px solid #E5E7EB;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.investment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
