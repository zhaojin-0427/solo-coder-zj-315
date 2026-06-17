<template>
  <div class="page-container">
    <div class="page-header">
      <h2>📝 活动复盘管理</h2>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="24">
        <el-button type="primary" class="chinese-btn" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建复盘
        </el-button>
      </el-col>
    </el-row>

    <el-table :data="reviews" class="card-shadow" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="方案名称" width="180">
        <template #default="{ row }">{{ row.plan?.name || '-' }}</template>
      </el-table-column>
      <el-table-column label="主题" width="120">
        <template #default="{ row }">
          <span class="theme-tag" :style="{ background: getThemeColor(row.plan?.theme) }">
            {{ row.plan?.theme?.name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="客户" width="100">
        <template #default="{ row }">{{ row.plan?.customer_name }}</template>
      </el-table-column>
      <el-table-column prop="review_date" label="复盘日期" width="120" />
      <el-table-column prop="rating" label="评分" width="100">
        <template #default="{ row }">
          <el-rate v-model="row.rating" disabled :max="5" />
        </template>
      </el-table-column>
      <el-table-column label="复购客户" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_repeat_customer ? 'success' : 'info'" size="small">
            {{ row.is_repeat_customer ? '是' : '否' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="customer_feedback" label="客户反馈" min-width="200" show-overflow-tooltip />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="viewDetail(row)">查看</el-button>
          <el-button size="small" type="warning" link @click="editReview(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showCreateDialog" :title="isEditing ? '编辑复盘' : '新建复盘'" width="800px">
      <el-form :model="formData" label-width="120px" @submit.prevent>
        <el-form-item label="关联方案" required>
          <el-select v-model="formData.plan_id" placeholder="请选择已完成的方案" style="width: 100%" :disabled="isEditing">
            <el-option
              v-for="plan in completedPlans"
              :key="plan.id"
              :label="`${plan.name} - ${plan.customer_name}`"
              :value="plan.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="复盘日期" required>
              <el-date-picker v-model="formData.review_date" type="date" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="客户评分" required>
              <el-rate v-model="formData.rating" :max="5" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="是否复购客户">
          <el-switch v-model="formData.is_repeat_customer" />
        </el-form-item>
        <el-form-item label="客户反馈">
          <el-input v-model="formData.customer_feedback" type="textarea" :rows="3" placeholder="请输入客户反馈" />
        </el-form-item>

        <h3 style="margin: 20px 0 10px; color: #8B4513">器物检查</h3>
        <div v-if="formData.items.length > 0">
          <el-table :data="formData.items" border size="small">
            <el-table-column prop="utensil.name" label="器物名称" width="180" />
            <el-table-column prop="utensil.category" label="分类" width="100" />
            <el-table-column label="是否破损" width="120" align="center">
              <template #default="{ row }">
                <el-switch v-model="row.damaged" @change="onDamageChange(row)" />
              </template>
            </el-table-column>
            <el-table-column label="破损说明" min-width="200">
              <template #default="{ row }">
                <el-input
                  v-model="row.damage_description"
                  :disabled="!row.damaged"
                  placeholder="请描述破损情况"
                />
              </template>
            </el-table-column>
            <el-table-column label="是否清洗" width="120" align="center">
              <template #default="{ row }">
                <el-switch v-model="row.cleaned" />
              </template>
            </el-table-column>
          </el-table>
        </div>
        <div v-else style="text-align: center; padding: 40px; color: #999">
          请先选择关联方案
        </div>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" class="chinese-btn" @click="saveReview">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="复盘详情" width="800px">
      <div v-if="currentReview">
        <el-descriptions :column="2" border class="card-shadow">
          <el-descriptions-item label="方案名称">{{ currentReview.plan?.name }}</el-descriptions-item>
          <el-descriptions-item label="主题">
            <span class="theme-tag" :style="{ background: getThemeColor(currentReview.plan?.theme) }">
              {{ currentReview.plan?.theme?.name }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="客户">{{ currentReview.plan?.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="复盘日期">{{ currentReview.review_date }}</el-descriptions-item>
          <el-descriptions-item label="评分">
            <el-rate v-model="currentReview.rating" disabled :max="5" />
          </el-descriptions-item>
          <el-descriptions-item label="复购客户">
            <el-tag :type="currentReview.is_repeat_customer ? 'success' : 'info'" size="small">
              {{ currentReview.is_repeat_customer ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="客户反馈" :span="2">
            {{ currentReview.customer_feedback || '暂无' }}
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin: 20px 0 10px; color: #8B4513">器物检查记录</h3>
        <el-table :data="currentReview.items" border class="card-shadow">
          <el-table-column prop="utensil.name" label="器物名称" width="180" />
          <el-table-column prop="utensil.category" label="分类" width="100" />
          <el-table-column label="是否破损" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.damaged ? 'danger' : 'success'" size="small">
                {{ row.damaged ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="破损说明" min-width="200">
            <template #default="{ row }">{{ row.damage_description || '-' }}</template>
          </el-table-column>
          <el-table-column label="是否清洗" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.cleaned ? 'success' : 'warning'" size="small">
                {{ row.cleaned ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { reviewApi, teaPlanApi, borrowListApi } from '@/api'
import type { ActivityReview, TeaPlan, BorrowList, Theme } from '@/types'

const reviews = ref<ActivityReview[]>([])
const completedPlans = ref<TeaPlan[]>([])
const borrowLists = ref<BorrowList[]>([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const isEditing = ref(false)
const editingId = ref<number>(0)
const currentReview = ref<ActivityReview | null>(null)

const formData = ref({
  plan_id: 0,
  review_date: '',
  customer_feedback: '',
  rating: 5,
  is_repeat_customer: false,
  items: [] as any[]
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

watch(() => formData.value.plan_id, async (newVal) => {
  if (newVal && !isEditing.value) {
    const borrowList = borrowLists.value.find(b => b.plan_id === newVal)
    if (borrowList) {
      const res = await borrowListApi.getOne(borrowList.id)
      formData.value.items = res.data.items.map(item => ({
        utensil_id: item.utensil_id,
        utensil: item.utensil,
        quantity: item.quantity,
        damaged: false,
        damage_description: '',
        cleaned: false
      }))
    } else {
      const planRes = await teaPlanApi.getOne(newVal)
      formData.value.items = planRes.data.recommended_items
        .filter((item: any) => item.selected)
        .map((item: any) => ({
          utensil_id: item.utensil_id,
          utensil: item.utensil,
          quantity: item.quantity,
          damaged: false,
          damage_description: '',
          cleaned: false
        }))
    }
  }
})

const loadReviews = async () => {
  try {
    const res = await reviewApi.getAll()
    reviews.value = res.data
  } catch (e) {
    ElMessage.error('加载复盘失败')
  }
}

const loadPlans = async () => {
  try {
    const [plansRes, borrowRes] = await Promise.all([
      teaPlanApi.getAll(),
      borrowListApi.getAll()
    ])
    completedPlans.value = plansRes.data.filter(p => p.status === 'confirmed' || p.status === 'borrowing')
    borrowLists.value = borrowRes.data
  } catch (e) {
    ElMessage.error('加载数据失败')
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  isEditing.value = false
  resetForm()
}

const resetForm = () => {
  formData.value = {
    plan_id: 0,
    review_date: '',
    customer_feedback: '',
    rating: 5,
    is_repeat_customer: false,
    items: []
  }
}

const onDamageChange = (row: any) => {
  if (!row.damaged) {
    row.damage_description = ''
  }
}

const saveReview = async () => {
  if (!formData.value.plan_id || !formData.value.review_date) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    const items = formData.value.items.map(item => ({
      utensil_id: item.utensil_id,
      damaged: item.damaged,
      damage_description: item.damage_description,
      cleaned: item.cleaned
    }))
    
    if (isEditing.value) {
      await reviewApi.update(editingId.value, {
        customer_feedback: formData.value.customer_feedback,
        rating: formData.value.rating,
        is_repeat_customer: formData.value.is_repeat_customer
      })
      for (const item of formData.value.items) {
        if (item.id) {
          await reviewApi.updateItem(item.id, {
            damaged: item.damaged,
            damage_description: item.damage_description,
            cleaned: item.cleaned
          })
        }
      }
      ElMessage.success('更新成功')
    } else {
      await reviewApi.create({
        ...formData.value,
        items
      })
      ElMessage.success('复盘已记录')
    }
    closeDialog()
    loadReviews()
    loadPlans()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

const viewDetail = async (row: ActivityReview) => {
  try {
    const res = await reviewApi.getOne(row.id)
    currentReview.value = res.data
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

const editReview = async (row: ActivityReview) => {
  isEditing.value = true
  editingId.value = row.id
  const res = await reviewApi.getOne(row.id)
  formData.value = {
    plan_id: res.data.plan_id,
    review_date: res.data.review_date,
    customer_feedback: res.data.customer_feedback || '',
    rating: res.data.rating,
    is_repeat_customer: res.data.is_repeat_customer,
    items: res.data.items.map(item => ({
      ...item,
      utensil_id: item.utensil_id
    }))
  }
  showCreateDialog.value = true
}

onMounted(() => {
  loadReviews()
  loadPlans()
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
</style>
