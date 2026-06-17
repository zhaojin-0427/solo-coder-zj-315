<template>
  <div class="page-container">
    <div class="page-header">
      <h2>👤 客户偏好档案</h2>
      <el-button @click="loadProfiles">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-row :gutter="20" class="filter-bar">
      <el-col :span="5">
        <el-input v-model="filterName" placeholder="客户姓名" clearable @clear="loadProfiles" @keyup.enter="loadProfiles" />
      </el-col>
      <el-col :span="5">
        <el-input v-model="filterPhone" placeholder="手机号" clearable @clear="loadProfiles" @keyup.enter="loadProfiles" />
      </el-col>
      <el-col :span="4">
        <el-select v-model="filterTea" placeholder="偏好茶类" clearable style="width: 100%" @change="loadProfiles">
          <el-option v-for="tea in TEA_CATEGORIES" :key="tea" :label="tea" :value="tea" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-checkbox v-model="filterRepurchase" @change="loadProfiles">仅复购客户</el-checkbox>
      </el-col>
      <el-col :span="6" style="text-align: right">
        <el-button type="primary" @click="loadProfiles">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </el-col>
    </el-row>

    <el-table :data="profiles" class="card-shadow" style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="customer_name" label="客户姓名" width="120" />
      <el-table-column prop="customer_phone" label="手机号" width="140" />
      <el-table-column prop="reservation_count" label="预约次数" width="100">
        <template #default="{ row }">
          <el-tag type="info" size="small">{{ row.reservation_count }} 次</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="preferred_tea" label="偏好茶类" width="100">
        <template #default="{ row }">{{ row.preferred_tea || '-' }}</template>
      </el-table-column>
      <el-table-column label="偏好主题色" width="120">
        <template #default="{ row }">
          <span v-if="row.preferred_color" class="color-dot" :style="{ background: getColorHex(row.preferred_color) }"></span>
          {{ row.preferred_color || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="preferred_photo_style" label="拍照风格" width="120">
        <template #default="{ row }">{{ row.preferred_photo_style || '-' }}</template>
      </el-table-column>
      <el-table-column prop="average_budget" label="平均预算" width="110">
        <template #default="{ row }">¥{{ row.average_budget }}</template>
      </el-table-column>
      <el-table-column prop="repurchase_count" label="复购次数" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.repurchase_count > 0" type="success" size="small">{{ row.repurchase_count }} 次</el-tag>
          <span v-else style="color: #999">0 次</span>
        </template>
      </el-table-column>
      <el-table-column prop="last_activity_date" label="最近活动" width="120">
        <template #default="{ row }">{{ row.last_activity_date || '-' }}</template>
      </el-table-column>
      <el-table-column prop="tags" label="备注标签" min-width="120">
        <template #default="{ row }">
          <template v-if="row.tags">
            <el-tag v-for="tag in parseTags(row.tags)" :key="tag" size="small" style="margin: 2px">{{ tag }}</el-tag>
          </template>
          <span v-else style="color: #999">-</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="viewProfile(row)">查看详情</el-button>
          <el-button size="small" type="warning" link @click="editProfile(row)">编辑标签</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDetailDialog" title="客户偏好档案详情" width="900px">
      <div v-if="currentProfile">
        <el-descriptions :column="3" border class="card-shadow">
          <el-descriptions-item label="客户姓名">{{ currentProfile.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="手机号">{{ currentProfile.customer_phone }}</el-descriptions-item>
          <el-descriptions-item label="预约次数">{{ currentProfile.reservation_count }} 次</el-descriptions-item>
          <el-descriptions-item label="偏好茶类">{{ currentProfile.preferred_tea || '-' }}</el-descriptions-item>
          <el-descriptions-item label="偏好主题色">
            <span v-if="currentProfile.preferred_color" class="color-dot" :style="{ background: getColorHex(currentProfile.preferred_color) }"></span>
            {{ currentProfile.preferred_color || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="拍照风格">{{ currentProfile.preferred_photo_style || '-' }}</el-descriptions-item>
          <el-descriptions-item label="平均预算">¥{{ currentProfile.average_budget }}</el-descriptions-item>
          <el-descriptions-item label="复购次数">{{ currentProfile.repurchase_count }} 次</el-descriptions-item>
          <el-descriptions-item label="最近活动日期">{{ currentProfile.last_activity_date || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注标签" :span="3">
            <template v-if="currentProfile.tags">
              <el-tag v-for="tag in parseTags(currentProfile.tags)" :key="tag" size="small" style="margin: 2px">{{ tag }}</el-tag>
            </template>
            <span v-else>-</span>
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs v-model="activeTab" style="margin-top: 20px">
          <el-tab-pane label="历史预约" name="reservations">
            <el-table :data="customerReservations" border size="small" v-loading="loadingReservations">
              <el-table-column prop="expected_date" label="日期" width="120" />
              <el-table-column prop="time_slot" label="时段" width="100" />
              <el-table-column prop="people_count" label="人数" width="80" />
              <el-table-column prop="budget" label="预算" width="100">
                <template #default="{ row }">¥{{ row.budget }}</template>
              </el-table-column>
              <el-table-column prop="preferred_tea" label="茶类" width="100" />
              <el-table-column prop="preferred_color" label="主题色" width="100" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getReservationStatusType(row.status)" size="small">{{ getReservationStatusText(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="120">
                <template #default="{ row }">{{ row.remark || '-' }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="关联茶席方案" name="plans">
            <el-table :data="customerPlans" border size="small" v-loading="loadingPlans">
              <el-table-column prop="name" label="方案名称" min-width="150" />
              <el-table-column prop="date" label="日期" width="120" />
              <el-table-column prop="time_slot" label="时段" width="100" />
              <el-table-column prop="tea_category" label="茶类" width="100" />
              <el-table-column prop="theme_color" label="主题色" width="100" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getPlanStatusType(row.status)" size="small">{{ getPlanStatusText(row.status) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="total_price" label="总价" width="100">
                <template #default="{ row }">¥{{ row.total_price }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showEditDialog" title="编辑客户标签" width="500px">
      <el-form :model="editFormData" label-width="100px" @submit.prevent>
        <el-form-item label="客户姓名">
          <el-input v-model="editFormData.customer_name" />
        </el-form-item>
        <el-form-item label="偏好茶类">
          <el-select v-model="editFormData.preferred_tea" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="tea in TEA_CATEGORIES" :key="tea" :label="tea" :value="tea" />
          </el-select>
        </el-form-item>
        <el-form-item label="偏好主题色">
          <el-select v-model="editFormData.preferred_color" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="color in COLORS" :key="color" :label="color" :value="color">
              <span class="color-dot" :style="{ background: getColorHex(color) }"></span>
              <span style="margin-left: 8px">{{ color }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="拍照风格">
          <el-select v-model="editFormData.preferred_photo_style" placeholder="请选择" clearable style="width: 100%">
            <el-option v-for="style in PHOTO_STYLES" :key="style" :label="style" :value="style" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注标签">
          <el-input v-model="editFormData.tags" type="textarea" :rows="3" placeholder="多个标签用逗号分隔，如：VIP,喜欢安静,高预算" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" class="chinese-btn" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Search } from '@element-plus/icons-vue'
import { customerProfileApi } from '@/api'
import { TEA_CATEGORIES, COLORS, PHOTO_STYLES } from '@/types'
import type { CustomerProfile, Reservation, TeaPlan } from '@/types'

const profiles = ref<CustomerProfile[]>([])
const filterName = ref('')
const filterPhone = ref('')
const filterTea = ref('')
const filterRepurchase = ref(false)

const showDetailDialog = ref(false)
const showEditDialog = ref(false)
const currentProfile = ref<CustomerProfile | null>(null)
const activeTab = ref('reservations')
const customerReservations = ref<Reservation[]>([])
const customerPlans = ref<TeaPlan[]>([])
const loadingReservations = ref(false)
const loadingPlans = ref(false)

const editFormData = ref({
  customer_name: '',
  preferred_tea: '',
  preferred_color: '',
  preferred_photo_style: '',
  tags: ''
})

const getColorHex = (color: string): string => {
  const colorMap: Record<string, string> = {
    '朱红': '#CD5C5C', '赭石': '#A0522D', '胭脂': '#C71585', '琥珀': '#FFBF00',
    '金黄': '#DAA520', '橙黄': '#FF8C00', '青色': '#5F9EA0', '湖蓝': '#4F94CD',
    '黛绿': '#556B2F', '松石': '#40E0D0', '月白': '#B0C4DE', '藏青': '#2F4F4F',
    '米白': '#D2B48C', '象牙': '#FFFFF0', '玄黑': '#2C2C2C', '紫砂': '#8B6914',
    '灰墨': '#696969', '素白': '#F5F5F5'
  }
  return colorMap[color] || '#8B4513'
}

const parseTags = (tags: string): string[] => {
  if (!tags) return []
  return tags.split(/[,，、]/).map(t => t.trim()).filter(t => t.length > 0)
}

const getReservationStatusType = (status: string): string => {
  const map: Record<string, string> = {
    pending: 'warning', confirmed: 'success', cancelled: 'danger', converted: 'info'
  }
  return map[status] || ''
}

const getReservationStatusText = (status: string): string => {
  const map: Record<string, string> = {
    pending: '待确认', confirmed: '已确认', cancelled: '已取消', converted: '已转化'
  }
  return map[status] || status
}

const getPlanStatusType = (status: string): string => {
  const map: Record<string, string> = {
    draft: 'info', confirmed: 'success', borrowing: 'warning', completed: ''
  }
  return map[status] || ''
}

const getPlanStatusText = (status: string): string => {
  const map: Record<string, string> = {
    draft: '草稿', confirmed: '已确认', borrowing: '借用中', completed: '已完成'
  }
  return map[status] || status
}

const loadProfiles = async () => {
  try {
    const params: any = {}
    if (filterName.value) params.customer_name = filterName.value
    if (filterPhone.value) params.customer_phone = filterPhone.value
    if (filterTea.value) params.preferred_tea = filterTea.value
    if (filterRepurchase.value) params.is_repurchase = true
    const res = await customerProfileApi.getAll(params)
    profiles.value = res.data
  } catch (e) {
    ElMessage.error('加载客户档案列表失败')
  }
}

const resetFilters = () => {
  filterName.value = ''
  filterPhone.value = ''
  filterTea.value = ''
  filterRepurchase.value = false
  loadProfiles()
}

const viewProfile = async (row: CustomerProfile) => {
  try {
    const res = await customerProfileApi.getOne(row.id)
    currentProfile.value = res.data
    showDetailDialog.value = true
    activeTab.value = 'reservations'
    loadCustomerReservations(row.id)
    loadCustomerPlans(row.id)
  } catch (e) {
    ElMessage.error('加载客户档案详情失败')
  }
}

const loadCustomerReservations = async (profileId: number) => {
  loadingReservations.value = true
  try {
    const res = await customerProfileApi.getReservations(profileId)
    customerReservations.value = res.data
  } catch (e) {
    customerReservations.value = []
  } finally {
    loadingReservations.value = false
  }
}

const loadCustomerPlans = async (profileId: number) => {
  loadingPlans.value = true
  try {
    const res = await customerProfileApi.getPlans(profileId)
    customerPlans.value = res.data
  } catch (e) {
    customerPlans.value = []
  } finally {
    loadingPlans.value = false
  }
}

const editProfile = (row: CustomerProfile) => {
  editFormData.value = {
    customer_name: row.customer_name,
    preferred_tea: row.preferred_tea || '',
    preferred_color: row.preferred_color || '',
    preferred_photo_style: row.preferred_photo_style || '',
    tags: row.tags || ''
  }
  currentProfile.value = row
  showEditDialog.value = true
}

const saveProfile = async () => {
  if (!currentProfile.value) return
  try {
    await customerProfileApi.update(currentProfile.value.id, editFormData.value)
    ElMessage.success('客户档案更新成功')
    showEditDialog.value = false
    loadProfiles()
  } catch (e) {
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  loadProfiles()
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
  margin-bottom: 20px;
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
