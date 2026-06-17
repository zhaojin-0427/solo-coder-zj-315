<template>
  <div class="page-container">
    <div class="page-header">
      <h2>🍃 主题方案管理</h2>
      <el-button type="primary" class="chinese-btn" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建新方案
      </el-button>
    </div>

    <el-row :gutter="20" class="filter-bar">
      <el-col :span="6">
        <el-select v-model="filterStatus" placeholder="选择状态" clearable @change="loadPlans">
          <el-option label="草稿" value="draft" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="借用中" value="borrowing" />
          <el-option label="已完成" value="completed" />
        </el-select>
      </el-col>
    </el-row>

    <el-table :data="plans" class="card-shadow" style="width: 100%; margin-top: 20px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="方案名称" width="180" />
      <el-table-column label="主题" width="140">
        <template #default="{ row }">
          <span class="theme-tag" :style="{ background: getThemeColor(row.theme) }">
            {{ row.theme?.name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="date" label="活动日期" width="120" />
      <el-table-column prop="people_count" label="人数" width="80" />
      <el-table-column prop="budget" label="预算" width="100">
        <template #default="{ row }">¥{{ row.budget }}</template>
      </el-table-column>
      <el-table-column prop="total_price" label="方案总价" width="120">
        <template #default="{ row }">¥{{ row.total_price }}</template>
      </el-table-column>
      <el-table-column prop="customer_name" label="客户" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <span :class="['status-badge', `status-${row.status}`]">
            {{ getStatusText(row.status) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="viewPlan(row)">查看</el-button>
          <el-button size="small" type="success" link @click="confirmPlan(row)" v-if="row.status === 'draft'">确认</el-button>
          <el-button size="small" type="warning" link @click="generateBorrow(row)" v-if="row.status === 'confirmed'">生成借单</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreateDialog" title="创建茶席方案" width="700px">
      <el-form :model="formData" label-width="100px" @submit.prevent>
        <el-form-item label="方案名称" required>
          <el-input v-model="formData.name" placeholder="请输入方案名称" />
        </el-form-item>
        <el-form-item label="选择主题" required>
          <el-select v-model="formData.theme_id" placeholder="请选择主题" style="width: 100%">
            <el-option
              v-for="theme in themes"
              :key="theme.id"
              :label="theme.name"
              :value="theme.id"
            >
              <span class="theme-tag" :style="{ background: getThemeColor(theme) }">
                {{ theme.name }}
              </span>
              <span style="margin-left: 10px; color: #666; font-size: 12px">
                {{ theme.tea_category }} | {{ theme.style }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="活动日期" required>
              <el-date-picker v-model="formData.date" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参与人数" required>
              <el-input-number v-model="formData.people_count" :min="1" :max="20" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="预算" required>
          <el-input-number v-model="formData.budget" :min="100" :max="10000" :step="100" style="width: 100%" />
        </el-form-item>
        <el-form-item label="拍照风格" required>
          <el-select v-model="formData.photo_style" placeholder="请选择拍照风格" style="width: 100%">
            <el-option v-for="style in PHOTO_STYLES" :key="style" :label="style" :value="style" />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户姓名" required>
              <el-input v-model="formData.customer_name" placeholder="请输入客户姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" required>
              <el-input v-model="formData.customer_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" class="chinese-btn" @click="createPlan">创建方案</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="方案详情" width="800px">
      <div v-if="currentPlan">
        <el-descriptions :column="2" border class="card-shadow">
          <el-descriptions-item label="方案名称">{{ currentPlan.name }}</el-descriptions-item>
          <el-descriptions-item label="主题">
            <span class="theme-tag" :style="{ background: getThemeColor(currentPlan.theme) }">
              {{ currentPlan.theme?.name }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="活动日期">{{ currentPlan.date }}</el-descriptions-item>
          <el-descriptions-item label="参与人数">{{ currentPlan.people_count }}人</el-descriptions-item>
          <el-descriptions-item label="预算">¥{{ currentPlan.budget }}</el-descriptions-item>
          <el-descriptions-item label="拍照风格">{{ currentPlan.photo_style }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentPlan.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="方案总价">¥{{ currentPlan.total_price }}</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin: 20px 0 10px">推荐器物组合</h3>
        <el-row :gutter="20">
          <el-col v-for="item in currentPlan.recommended_items" :key="item.id" :span="12">
            <div class="utensil-card card-shadow" style="padding: 15px; margin-bottom: 15px">
              <div style="display: flex; align-items: center">
                <el-checkbox v-model="item.selected" />
                <div style="flex: 1; margin-left: 10px">
                  <div style="font-weight: bold; color: #8B4513">{{ item.utensil.name }}</div>
                  <div style="font-size: 12px; color: #666">
                    {{ item.utensil.category }} | {{ item.utensil.material }} | {{ item.utensil.color }}
                  </div>
                  <div style="color: #A0522D; margin-top: 5px">
                    ¥{{ item.utensil.price }} × {{ item.quantity }} = ¥{{ item.utensil.price * item.quantity }}
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" class="chinese-btn" @click="regenerateRecommend">
          <el-icon><Refresh /></el-icon>
          重新推荐
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showBorrowDialog" title="生成布席清单" width="600px">
      <el-form :model="borrowForm" label-width="100px" @submit.prevent>
        <el-form-item label="借用日期" required>
          <el-date-picker v-model="borrowForm.borrow_date" type="date" style="width: 100%" />
        </el-form-item>
        <el-form-item label="归还日期" required>
          <el-date-picker v-model="borrowForm.return_date" type="date" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showBorrowDialog = false">取消</el-button>
        <el-button type="primary" class="chinese-btn" @click="createBorrowList">生成清单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { teaPlanApi, themeApi, borrowListApi } from '@/api'
import { PHOTO_STYLES } from '@/types'
import type { TeaPlan, Theme } from '@/types'

const plans = ref<TeaPlan[]>([])
const themes = ref<Theme[]>([])
const filterStatus = ref<string>('')
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showBorrowDialog = ref(false)
const currentPlan = ref<TeaPlan | null>(null)
const selectedPlanId = ref<number>(0)

const formData = ref({
  name: '',
  theme_id: 0,
  date: '',
  people_count: 4,
  budget: 1000,
  photo_style: '宋韵古风',
  customer_name: '',
  customer_phone: '',
  status: 'draft'
})

const borrowForm = ref({
  borrow_date: '',
  return_date: ''
})

const getThemeColor = (theme: Theme | undefined) => {
  const colorMap: Record<string, string> = {
    '青色': '#5F9EA0',
    '米白': '#D2B48C',
    '朱红': '#CD5C5C',
    '黛绿': '#556B2F',
    '月白': '#B0C4DE'
  }
  return colorMap[theme?.color || ''] || '#8B4513'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    confirmed: '已确认',
    borrowing: '借用中',
    completed: '已完成'
  }
  return map[status] || status
}

const loadPlans = async () => {
  try {
    const res = await teaPlanApi.getAll(filterStatus.value || undefined)
    plans.value = res.data
  } catch (e) {
    ElMessage.error('加载方案失败')
  }
}

const loadThemes = async () => {
  try {
    const res = await themeApi.getAll()
    themes.value = res.data
  } catch (e) {
    ElMessage.error('加载主题失败')
  }
}

const createPlan = async () => {
  if (!formData.value.theme_id || !formData.value.name || !formData.value.date || !formData.value.customer_name || !formData.value.customer_phone) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await teaPlanApi.create(formData.value as any)
    ElMessage.success('方案创建成功，系统已自动推荐器物组合')
    showCreateDialog.value = false
    resetForm()
    loadPlans()
  } catch (e) {
    ElMessage.error('创建方案失败')
  }
}

const resetForm = () => {
  formData.value = {
    name: '',
    theme_id: 0,
    date: '',
    people_count: 4,
    budget: 1000,
    photo_style: '宋韵古风',
    customer_name: '',
    customer_phone: '',
    status: 'draft'
  }
}

const viewPlan = async (row: TeaPlan) => {
  try {
    const res = await teaPlanApi.getOne(row.id)
    currentPlan.value = res.data
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

const confirmPlan = async (row: TeaPlan) => {
  try {
    await teaPlanApi.update(row.id, { status: 'confirmed' })
    ElMessage.success('方案已确认')
    loadPlans()
  } catch (e) {
    ElMessage.error('确认失败')
  }
}

const generateBorrow = (row: TeaPlan) => {
  selectedPlanId.value = row.id
  showBorrowDialog.value = true
}

const createBorrowList = async () => {
  if (!borrowForm.value.borrow_date || !borrowForm.value.return_date) {
    ElMessage.warning('请选择日期')
    return
  }
  try {
    const plan = await teaPlanApi.getOne(selectedPlanId.value)
    const items = plan.data.recommended_items
      .filter(item => item.selected)
      .map(item => ({
        utensil_id: item.utensil_id,
        quantity: item.quantity,
        borrowed: false,
        returned: false
      }))
    
    await borrowListApi.create({
      plan_id: selectedPlanId.value,
      borrow_date: borrowForm.value.borrow_date,
      return_date: borrowForm.value.return_date,
      status: 'pending',
      items
    })
    ElMessage.success('布席清单已生成')
    showBorrowDialog.value = false
    loadPlans()
  } catch (e) {
    ElMessage.error('生成清单失败')
  }
}

const regenerateRecommend = async () => {
  if (!currentPlan.value) return
  try {
    const res = await teaPlanApi.regenerate(currentPlan.value.id)
    currentPlan.value = res.data
    ElMessage.success('已重新推荐')
  } catch (e) {
    ElMessage.error('重新推荐失败')
  }
}

onMounted(() => {
  loadPlans()
  loadThemes()
})
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  color: #8B4513;
  font-size: 24px;
}

.filter-bar {
  margin-bottom: 10px;
}
</style>
