<template>
  <div class="page-container">
    <div class="page-header">
      <h2>🍃 主题方案管理</h2>
      <el-button type="primary" class="chinese-btn" @click="openCreateDialog">
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
      <el-table-column prop="theme_color" label="主题色" width="100">
        <template #default="{ row }">
          <span class="color-dot" :style="{ background: getColorHex(row.theme_color) }"></span>
          {{ row.theme_color }}
        </template>
      </el-table-column>
      <el-table-column prop="tea_category" label="茶类" width="100" />
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

    <el-dialog v-model="showCreateDialog" title="创建茶席方案" width="900px" :close-on-click-modal="false">
      <el-steps :active="createStep" align-center style="margin-bottom: 20px">
        <el-step title="基本信息" />
        <el-step title="预览推荐器物" />
        <el-step title="确认创建" />
      </el-steps>

      <div v-if="createStep === 0">
        <el-form :model="formData" label-width="100px" @submit.prevent>
          <el-form-item label="方案名称" required>
            <el-input v-model="formData.name" placeholder="请输入方案名称" />
          </el-form-item>
          <el-form-item label="选择主题" required>
            <el-select v-model="formData.theme_id" placeholder="请选择主题" style="width: 100%" @change="onThemeChange">
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
              <el-form-item label="主题色" required>
                <el-select v-model="formData.theme_color" placeholder="请选择主题色" style="width: 100%">
                  <el-option v-for="color in COLORS" :key="color" :label="color" :value="color">
                    <span class="color-dot" :style="{ background: getColorHex(color) }"></span>
                    <span style="margin-left: 8px">{{ color }}</span>
                  </el-option>
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="茶类" required>
                <el-select v-model="formData.tea_category" placeholder="请选择茶类" style="width: 100%">
                  <el-option v-for="tea in TEA_CATEGORIES" :key="tea" :label="tea" :value="tea" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
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
      </div>

      <div v-if="createStep === 1">
        <div v-if="previewLoading" style="text-align: center; padding: 60px">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <p style="margin-top: 15px; color: #8B4513">正在生成推荐器物组合...</p>
        </div>
        <div v-else-if="previewItems.length > 0">
          <el-alert type="info" :closable="false" style="margin-bottom: 15px">
            <template #title>
              系统已根据 <b>{{ formData.theme_color }}</b> + <b>{{ formData.tea_category }}</b> + <b>{{ formData.people_count }}人</b> + <b>¥{{ formData.budget }}</b> + <b>{{ formData.photo_style }}</b> 组合策划，推荐以下器物。请勾选需要的器物后创建方案。
            </template>
          </el-alert>
          <el-table :data="previewItems" border style="width: 100%" @selection-change="handlePreviewSelectionChange" ref="previewTable">
            <el-table-column type="selection" width="50" />
            <el-table-column prop="utensil.category" label="器物分类" width="90" />
            <el-table-column prop="utensil.name" label="器物名称" width="160" />
            <el-table-column prop="utensil.color" label="颜色" width="90">
              <template #default="{ row }">
                <span class="color-dot" :style="{ background: getColorHex(row.utensil.color) }"></span>
                {{ row.utensil.color }}
              </template>
            </el-table-column>
            <el-table-column prop="utensil.material" label="材质" width="80" />
            <el-table-column label="数量" width="80" align="center">
              <template #default="{ row }">{{ row.quantity }}</template>
            </el-table-column>
            <el-table-column label="单价" width="90" align="right">
              <template #default="{ row }">¥{{ row.utensil.price }}</template>
            </el-table-column>
            <el-table-column label="小计" width="100" align="right">
              <template #default="{ row }">
                <span style="color: #8B4513; font-weight: bold">¥{{ row.utensil.price * row.quantity }}</span>
              </template>
            </el-table-column>
          </el-table>
          <div style="margin-top: 15px; text-align: right; font-size: 16px; color: #8B4513">
            已选器物总价: <b style="font-size: 20px">¥{{ previewTotalPrice }}</b>
          </div>
        </div>
        <div v-else style="text-align: center; padding: 60px; color: #999">
          未找到匹配的推荐器物，请调整条件后重试
        </div>
      </div>

      <div v-if="createStep === 2">
        <el-result icon="info" title="确认创建方案" sub-title="请确认以下信息无误后点击创建">
          <template #extra>
            <el-descriptions :column="2" border style="text-align: left; margin-bottom: 20px">
              <el-descriptions-item label="方案名称">{{ formData.name }}</el-descriptions-item>
              <el-descriptions-item label="主题">{{ selectedThemeName }}</el-descriptions-item>
              <el-descriptions-item label="主题色">
                <span class="color-dot" :style="{ background: getColorHex(formData.theme_color) }"></span>
                {{ formData.theme_color }}
              </el-descriptions-item>
              <el-descriptions-item label="茶类">{{ formData.tea_category }}</el-descriptions-item>
              <el-descriptions-item label="活动日期">{{ formData.date }}</el-descriptions-item>
              <el-descriptions-item label="参与人数">{{ formData.people_count }}人</el-descriptions-item>
              <el-descriptions-item label="预算">¥{{ formData.budget }}</el-descriptions-item>
              <el-descriptions-item label="拍照风格">{{ formData.photo_style }}</el-descriptions-item>
              <el-descriptions-item label="客户姓名">{{ formData.customer_name }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{ formData.customer_phone }}</el-descriptions-item>
            </el-descriptions>
            <h4 style="color: #8B4513; margin: 15px 0 10px; text-align: left">已选器物 ({{ selectedPreviewItems.length }}件)</h4>
            <el-table :data="selectedPreviewItems" border size="small" style="text-align: left">
              <el-table-column prop="utensil.category" label="分类" width="80" />
              <el-table-column prop="utensil.name" label="名称" width="150" />
              <el-table-column prop="utensil.color" label="颜色" width="80" />
              <el-table-column prop="utensil.material" label="材质" width="70" />
              <el-table-column label="数量" width="60" align="center">
                <template #default="{ row }">{{ row.quantity }}</template>
              </el-table-column>
              <el-table-column label="单价" width="80" align="right">
                <template #default="{ row }">¥{{ row.utensil.price }}</template>
              </el-table-column>
              <el-table-column label="小计" width="90" align="right">
                <template #default="{ row }">¥{{ row.utensil.price * row.quantity }}</template>
              </el-table-column>
            </el-table>
            <div style="margin-top: 10px; text-align: right; font-size: 16px; color: #8B4513">
              总价: <b style="font-size: 20px">¥{{ previewTotalPrice }}</b>
            </div>
          </template>
        </el-result>
      </div>

      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button v-if="createStep > 0" @click="createStep--">上一步</el-button>
        <el-button v-if="createStep === 0" type="primary" class="chinese-btn" @click="fetchPreview" :disabled="!canPreview">
          预览推荐器物
        </el-button>
        <el-button v-if="createStep === 1" type="primary" class="chinese-btn" @click="createStep = 2" :disabled="selectedPreviewItems.length === 0">
          确认选择
        </el-button>
        <el-button v-if="createStep === 2" type="primary" class="chinese-btn" @click="createPlan">
          创建方案
        </el-button>
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
          <el-descriptions-item label="主题色">
            <span class="color-dot" :style="{ background: getColorHex(currentPlan.theme_color) }"></span>
            {{ currentPlan.theme_color }}
          </el-descriptions-item>
          <el-descriptions-item label="茶类">{{ currentPlan.tea_category }}</el-descriptions-item>
          <el-descriptions-item label="活动日期">{{ currentPlan.date }}</el-descriptions-item>
          <el-descriptions-item label="参与人数">{{ currentPlan.people_count }}人</el-descriptions-item>
          <el-descriptions-item label="预算">¥{{ currentPlan.budget }}</el-descriptions-item>
          <el-descriptions-item label="拍照风格">{{ currentPlan.photo_style }}</el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentPlan.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="方案总价">¥{{ currentPlan.total_price }}</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin: 20px 0 10px">已选器物组合</h3>
        <el-table :data="currentPlan.recommended_items.filter(i => i.selected)" border size="small" class="card-shadow">
          <el-table-column prop="utensil.category" label="器物分类" width="90" />
          <el-table-column prop="utensil.name" label="器物名称" width="160" />
          <el-table-column prop="utensil.color" label="颜色" width="90">
            <template #default="{ row }">
              <span class="color-dot" :style="{ background: getColorHex(row.utensil.color) }"></span>
              {{ row.utensil.color }}
            </template>
          </el-table-column>
          <el-table-column prop="utensil.material" label="材质" width="80" />
          <el-table-column label="数量" width="70" align="center">
            <template #default="{ row }">{{ row.quantity }}</template>
          </el-table-column>
          <el-table-column label="单价" width="90" align="right">
            <template #default="{ row }">¥{{ row.utensil.price }}</template>
          </el-table-column>
          <el-table-column label="小计" width="100" align="right">
            <template #default="{ row }">
              <span style="color: #8B4513; font-weight: bold">¥{{ row.utensil.price * row.quantity }}</span>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 10px; text-align: right; font-size: 16px; color: #8B4513">
          总价: <b style="font-size: 20px">¥{{ currentPlan.total_price }}</b>
        </div>
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
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Refresh, Loading } from '@element-plus/icons-vue'
import { teaPlanApi, themeApi, borrowListApi, recommendApi } from '@/api'
import { PHOTO_STYLES, TEA_CATEGORIES, COLORS } from '@/types'
import type { TeaPlan, Theme, RecommendationItem } from '@/types'

const plans = ref<TeaPlan[]>([])
const themes = ref<Theme[]>([])
const filterStatus = ref<string>('')
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showBorrowDialog = ref(false)
const currentPlan = ref<TeaPlan | null>(null)
const selectedPlanId = ref<number>(0)
const createStep = ref(0)
const previewItems = ref<(RecommendationItem & { selected: boolean })[]>([])
const previewLoading = ref(false)
const previewTable = ref()
const selectedPreviewRows = ref<(RecommendationItem & { selected: boolean })[]>([])

const formData = ref({
  name: '',
  theme_id: 0,
  date: '',
  people_count: 4,
  budget: 1000,
  photo_style: '宋韵古风',
  theme_color: '',
  tea_category: '',
  customer_name: '',
  customer_phone: '',
  status: 'draft'
})

const borrowForm = ref({
  borrow_date: '',
  return_date: ''
})

const selectedThemeName = computed(() => {
  const t = themes.value.find(t => t.id === formData.value.theme_id)
  return t?.name || ''
})

const canPreview = computed(() => {
  return formData.value.theme_color && formData.value.tea_category && formData.value.people_count > 0 && formData.value.budget > 0 && formData.value.photo_style
})

const selectedPreviewItems = computed(() => selectedPreviewRows.value.length > 0 ? selectedPreviewRows.value : previewItems.value.filter(i => i.selected))

const previewTotalPrice = computed(() => {
  return selectedPreviewItems.value.reduce((sum, item) => sum + item.utensil.price * item.quantity, 0)
})

const handlePreviewSelectionChange = (rows: any[]) => {
  selectedPreviewRows.value = rows
  previewItems.value.forEach(item => {
    item.selected = rows.includes(item)
  })
}

const getColorHex = (color: string) => {
  const colorMap: Record<string, string> = {
    '朱红': '#CD5C5C', '赭石': '#A0522D', '胭脂': '#C71585', '琥珀': '#FFBF00',
    '金黄': '#DAA520', '橙黄': '#FF8C00', '青色': '#5F9EA0', '湖蓝': '#4F94CD',
    '黛绿': '#556B2F', '松石': '#40E0D0', '月白': '#B0C4DE', '藏青': '#2F4F4F',
    '米白': '#D2B48C', '象牙': '#FFFFF0', '玄黑': '#2C2C2C', '紫砂': '#8B6914',
    '灰墨': '#696969', '素白': '#F5F5F5'
  }
  return colorMap[color] || '#8B4513'
}

const getThemeColor = (theme: Theme | undefined) => {
  return getColorHex(theme?.color || '')
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

const onThemeChange = (themeId: number) => {
  const theme = themes.value.find(t => t.id === themeId)
  if (theme) {
    formData.value.theme_color = theme.color
    formData.value.tea_category = theme.tea_category
    formData.value.photo_style = theme.style
  }
}

const openCreateDialog = () => {
  createStep.value = 0
  previewItems.value = []
  selectedPreviewRows.value = []
  showCreateDialog.value = true
}

const fetchPreview = async () => {
  if (!canPreview.value) {
    ElMessage.warning('请先选择主题色、茶类等必要信息')
    return
  }
  previewLoading.value = true
  createStep.value = 1
  try {
    const res = await recommendApi.getRecommendation({
      theme_color: formData.value.theme_color,
      tea_category: formData.value.tea_category,
      people_count: formData.value.people_count,
      budget: formData.value.budget,
      photo_style: formData.value.photo_style
    })
    previewItems.value = (res.data.recommendations || []).map((item: RecommendationItem) => ({
      ...item,
      selected: true
    }))
    selectedPreviewRows.value = [...previewItems.value]
    setTimeout(() => {
      if (previewTable.value) {
        previewItems.value.forEach(row => {
          previewTable.value.toggleRowSelection(row, true)
        })
      }
    }, 100)
  } catch (e) {
    ElMessage.error('获取推荐失败')
  } finally {
    previewLoading.value = false
  }
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
  if (selectedPreviewItems.value.length === 0) {
    ElMessage.warning('请至少选择一件推荐器物')
    return
  }
  try {
    const selected_items = previewItems.value.map(item => ({
      utensil_id: item.utensil.id,
      quantity: item.quantity,
      selected: item.selected
    }))
    await teaPlanApi.create({
      ...formData.value,
      selected_items
    })
    ElMessage.success('方案创建成功')
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
    theme_color: '',
    tea_category: '',
    customer_name: '',
    customer_phone: '',
    status: 'draft'
  }
  previewItems.value = []
  selectedPreviewRows.value = []
  createStep.value = 0
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

.color-dot {
  display: inline-block;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  vertical-align: middle;
  border: 1px solid #d4c4a8;
  margin-right: 4px;
}
</style>
