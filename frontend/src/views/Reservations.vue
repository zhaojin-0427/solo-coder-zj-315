<template>
  <div class="page-container">
    <div class="page-header">
      <h2>📅 预约排期管理</h2>
      <div style="display: flex; gap: 10px">
        <el-radio-group v-model="viewMode" size="default">
          <el-radio-button value="calendar">
            <el-icon><Calendar /></el-icon>
            日历视图
          </el-radio-button>
          <el-radio-button value="list">
            <el-icon><List /></el-icon>
            列表视图
          </el-radio-button>
        </el-radio-group>
        <el-button type="primary" class="chinese-btn" @click="openCreateDialog()">
          <el-icon><Plus /></el-icon>
          新增预约
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="filter-bar">
      <el-col :span="6">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 100%"
          @change="loadReservations"
        />
      </el-col>
      <el-col :span="4">
        <el-select v-model="filterStatus" placeholder="预约状态" clearable style="width: 100%" @change="loadReservations">
          <el-option label="待确认" value="pending" />
          <el-option label="已确认" value="confirmed" />
          <el-option label="已取消" value="cancelled" />
          <el-option label="已转化" value="converted" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select v-model="filterTea" placeholder="茶类" clearable style="width: 100%" @change="loadReservations">
          <el-option v-for="tea in TEA_CATEGORIES" :key="tea" :label="tea" :value="tea" />
        </el-select>
      </el-col>
      <el-col :span="4">
        <el-select v-model="filterColor" placeholder="主题色" clearable style="width: 100%" @change="loadReservations">
          <el-option v-for="color in COLORS" :key="color" :label="color" :value="color">
            <span class="color-dot" :style="{ background: getColorHex(color) }"></span>
            <span style="margin-left: 8px">{{ color }}</span>
          </el-option>
        </el-select>
      </el-col>
      <el-col :span="6" style="text-align: right">
        <el-button @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置筛选
        </el-button>
      </el-col>
    </el-row>

    <div v-if="viewMode === 'calendar'" class="calendar-container card-shadow">
      <div class="calendar-header">
        <el-button size="small" @click="prevMonth">
          <el-icon><ArrowLeft /></el-icon>
        </el-button>
        <span class="calendar-title">{{ currentYear }}年{{ currentMonth }}月</span>
        <el-button size="small" @click="nextMonth">
          <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button size="small" type="primary" link @click="goToToday">今天</el-button>
      </div>
      <div class="calendar-weekdays">
        <div v-for="day in weekDays" :key="day" class="weekday">{{ day }}</div>
      </div>
      <div class="calendar-grid">
        <div
          v-for="(day, idx) in calendarDays"
          :key="idx"
          class="calendar-day"
          :class="{
            'other-month': !day.isCurrentMonth,
            'today': day.isToday,
            'has-events': day.reservations.length > 0
          }"
          @click="day.isCurrentMonth && openCreateDialog(day.date)"
        >
          <div class="day-number">{{ day.day }}</div>
          <div class="day-events">
            <div
              v-for="res in day.reservations.slice(0, 2)"
              :key="res.id"
              class="event-item"
              :class="`event-${res.status}`"
              @click.stop="viewReservation(res)"
            >
              <span class="event-time">{{ res.time_slot }}</span>
              <span class="event-name">{{ res.customer_name }}</span>
            </div>
            <div v-if="day.reservations.length > 2" class="more-events">
              +{{ day.reservations.length - 2 }} 更多
            </div>
          </div>
        </div>
      </div>
    </div>

    <el-table v-if="viewMode === 'list'" :data="reservations" class="card-shadow" style="width: 100%; margin-top: 20px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="customer_name" label="客户姓名" width="120" />
      <el-table-column prop="customer_phone" label="联系电话" width="140" />
      <el-table-column prop="expected_date" label="期望日期" width="120" />
      <el-table-column prop="time_slot" label="时段" width="100" />
      <el-table-column prop="people_count" label="人数" width="80" />
      <el-table-column prop="budget" label="预算" width="100">
        <template #default="{ row }">¥{{ row.budget }}</template>
      </el-table-column>
      <el-table-column label="偏好主题色" width="120">
        <template #default="{ row }">
          <span v-if="row.preferred_color" class="color-dot" :style="{ background: getColorHex(row.preferred_color) }"></span>
          {{ row.preferred_color || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="preferred_tea" label="偏好茶类" width="100">
        <template #default="{ row }">{{ row.preferred_tea || '-' }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <span :class="['status-badge', `status-${row.status}`]">
            {{ getStatusText(row.status) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="280" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="viewReservation(row)">查看</el-button>
          <el-button size="small" type="success" link @click="confirmReservation(row)" v-if="row.status === 'pending'">确认</el-button>
          <el-button size="small" type="warning" link @click="editReservation(row)" v-if="row.status === 'pending'">编辑</el-button>
          <el-button size="small" type="danger" link @click="cancelReservation(row)" v-if="row.status !== 'cancelled' && row.status !== 'converted'">取消</el-button>
          <el-button size="small" type="primary" link @click="convertToPlan(row)" v-if="row.status === 'confirmed'">转化方案</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showFormDialog" :title="isEditing ? '编辑预约' : '新增预约'" width="700px" :close-on-click-modal="false">
      <el-form :model="formData" label-width="100px" @submit.prevent>
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
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="期望日期" required>
              <el-date-picker v-model="formData.expected_date" type="date" style="width: 100%" @change="checkConflict" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时段" required>
              <el-select v-model="formData.time_slot" style="width: 100%" @change="checkConflict">
                <el-option v-for="slot in TIME_SLOTS" :key="slot" :label="slot" :value="slot" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="人数" required>
              <el-input-number v-model="formData.people_count" :min="1" :max="30" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预算" required>
              <el-input-number v-model="formData.budget" :min="100" :max="20000" :step="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="偏好主题色">
              <el-select v-model="formData.preferred_color" placeholder="请选择主题色" clearable style="width: 100%">
                <el-option v-for="color in COLORS" :key="color" :label="color" :value="color">
                  <span class="color-dot" :style="{ background: getColorHex(color) }"></span>
                  <span style="margin-left: 8px">{{ color }}</span>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="偏好茶类">
              <el-select v-model="formData.preferred_tea" placeholder="请选择茶类" clearable style="width: 100%">
                <el-option v-for="tea in TEA_CATEGORIES" :key="tea" :label="tea" :value="tea" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="拍照风格">
          <el-select v-model="formData.photo_style" placeholder="请选择拍照风格" clearable style="width: 100%">
            <el-option v-for="style in PHOTO_STYLES" :key="style" :label="style" :value="style" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>

      <el-alert v-if="conflictResult?.has_conflict" type="error" :closable="false" style="margin-top: 15px">
        <template #title>
          <b>⚠️ 时段冲突警告：</b>该日期时段已有活动安排：
          <ul style="margin: 10px 0 0 20px">
            <li v-for="(c, idx) in conflictResult.conflicts" :key="idx">
              [{{ c.time_slot }}] {{ c.type === 'plan' ? '茶席方案' : '预约' }}: {{ c.name }} ({{ c.customer_name }})
            </li>
          </ul>
        </template>
      </el-alert>

      <template #footer>
        <el-button @click="showFormDialog = false">取消</el-button>
        <el-button type="primary" class="chinese-btn" @click="saveReservation" :disabled="conflictResult?.has_conflict && !isEditing">
          {{ isEditing ? '保存修改' : '创建预约' }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showDetailDialog" title="预约详情" width="700px">
      <div v-if="currentReservation">
        <el-descriptions :column="2" border class="card-shadow">
          <el-descriptions-item label="客户姓名">{{ currentReservation.customer_name }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentReservation.customer_phone }}</el-descriptions-item>
          <el-descriptions-item label="期望日期">{{ currentReservation.expected_date }}</el-descriptions-item>
          <el-descriptions-item label="时段">{{ currentReservation.time_slot }}</el-descriptions-item>
          <el-descriptions-item label="人数">{{ currentReservation.people_count }}人</el-descriptions-item>
          <el-descriptions-item label="预算">¥{{ currentReservation.budget }}</el-descriptions-item>
          <el-descriptions-item label="偏好主题色">
            <span v-if="currentReservation.preferred_color" class="color-dot" :style="{ background: getColorHex(currentReservation.preferred_color) }"></span>
            {{ currentReservation.preferred_color || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="偏好茶类">{{ currentReservation.preferred_tea || '-' }}</el-descriptions-item>
          <el-descriptions-item label="拍照风格">{{ currentReservation.photo_style || '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <span :class="['status-badge', `status-${currentReservation.status}`]">
              {{ getStatusText(currentReservation.status) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ currentReservation.remark || '-' }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentReservation.plans && currentReservation.plans.length > 0" style="margin-top: 20px">
          <h3 style="color: #8B4513; margin-bottom: 10px">关联的茶席方案</h3>
          <el-table :data="currentReservation.plans" border size="small">
            <el-table-column prop="name" label="方案名称" />
            <el-table-column prop="date" label="日期" width="120" />
            <el-table-column prop="time_slot" label="时段" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <span :class="['status-badge', `status-${row.status}`]">{{ getPlanStatusText(row.status) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="total_price" label="总价" width="120">
              <template #default="{ row }">¥{{ row.total_price }}</template>
            </el-table-column>
          </el-table>
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button v-if="currentReservation?.status === 'pending'" type="success" @click="confirmReservation(currentReservation)">
          确认预约
        </el-button>
        <el-button v-if="currentReservation?.status === 'pending'" type="warning" @click="editReservation(currentReservation)">
          编辑预约
        </el-button>
        <el-button v-if="currentReservation?.status === 'confirmed'" type="primary" @click="convertToPlan(currentReservation)">
          转化为茶席方案
        </el-button>
        <el-button v-if="currentReservation?.status !== 'cancelled' && currentReservation?.status !== 'converted'" type="danger" @click="cancelReservation(currentReservation)">
          取消预约
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="showConvertDialog" title="转化为茶席方案" width="500px">
      <el-form :model="convertForm" label-width="100px" @submit.prevent>
        <el-form-item label="方案名称" required>
          <el-input v-model="convertForm.name" placeholder="请输入方案名称" />
        </el-form-item>
        <el-form-item label="选择主题" required>
          <el-select v-model="convertForm.theme_id" placeholder="请选择主题" style="width: 100%">
            <el-option
              v-for="theme in themes"
              :key="theme.id"
              :label="theme.name"
              :value="theme.id"
            >
              <span class="theme-tag" :style="{ background: getThemeColor(theme) }">{{ theme.name }}</span>
              <span style="margin-left: 10px; color: #666; font-size: 12px">
                {{ theme.tea_category }} | {{ theme.style }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-alert type="info" :closable="false" style="margin-top: 10px">
          <template #title>
            转化后将自动带入以下信息：
            <ul style="margin: 8px 0 0 20px; font-size: 13px">
              <li>客户信息、人数、预算</li>
              <li>主题色、茶类、拍照风格</li>
              <li>日期时段：{{ currentReservation?.expected_date }} {{ currentReservation?.time_slot }}</li>
            </ul>
          </template>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="showConvertDialog = false">取消</el-button>
        <el-button type="primary" class="chinese-btn" @click="doConvert">确认转化</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, Calendar, List, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { reservationApi, themeApi } from '@/api'
import { TEA_CATEGORIES, COLORS, PHOTO_STYLES, TIME_SLOTS } from '@/types'
import type { Reservation, Theme, ConflictCheckResponse } from '@/types'

const reservations = ref<Reservation[]>([])
const themes = ref<Theme[]>([])
const viewMode = ref<'calendar' | 'list'>('calendar')
const dateRange = ref<string[]>([])
const filterStatus = ref('')
const filterTea = ref('')
const filterColor = ref('')

const currentDate = new Date()
const currentYear = ref(currentDate.getFullYear())
const currentMonth = ref(currentDate.getMonth() + 1)
const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const showFormDialog = ref(false)
const showDetailDialog = ref(false)
const showConvertDialog = ref(false)
const isEditing = ref(false)
const editingId = ref<number>(0)
const currentReservation = ref<Reservation | null>(null)
const conflictResult = ref<ConflictCheckResponse | null>(null)

const formData = ref({
  customer_name: '',
  customer_phone: '',
  expected_date: '',
  time_slot: '全天',
  people_count: 4,
  budget: 1000,
  preferred_color: '',
  preferred_tea: '',
  photo_style: '',
  remark: '',
  status: 'pending'
})

const convertForm = ref({
  theme_id: 0,
  name: ''
})

interface CalendarDay {
  day: number
  date: string
  isCurrentMonth: boolean
  isToday: boolean
  reservations: Reservation[]
}

const calendarDays = computed<CalendarDay[]>(() => {
  const year = currentYear.value
  const month = currentMonth.value - 1
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startDay = firstDay.getDay()
  const daysInMonth = lastDay.getDate()
  
  const today = new Date()
  const todayStr = formatDate(today)
  
  const days: CalendarDay[] = []
  
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startDay - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i
    const date = new Date(year, month - 1, day)
    days.push({
      day,
      date: formatDate(date),
      isCurrentMonth: false,
      isToday: false,
      reservations: getReservationsForDate(formatDate(date))
    })
  }
  
  for (let i = 1; i <= daysInMonth; i++) {
    const date = new Date(year, month, i)
    const dateStr = formatDate(date)
    days.push({
      day: i,
      date: dateStr,
      isCurrentMonth: true,
      isToday: dateStr === todayStr,
      reservations: getReservationsForDate(dateStr)
    })
  }
  
  const remainingDays = 42 - days.length
  for (let i = 1; i <= remainingDays; i++) {
    const date = new Date(year, month + 1, i)
    days.push({
      day: i,
      date: formatDate(date),
      isCurrentMonth: false,
      isToday: false,
      reservations: getReservationsForDate(formatDate(date))
    })
  }
  
  return days
})

const getReservationsForDate = (dateStr: string): Reservation[] => {
  return reservations.value.filter(r => r.expected_date === dateStr && r.status !== 'cancelled')
}

const formatDate = (date: Date): string => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

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

const getThemeColor = (theme: Theme): string => getColorHex(theme?.color || '')

const getStatusText = (status: string): string => {
  const map: Record<string, string> = {
    pending: '待确认',
    confirmed: '已确认',
    cancelled: '已取消',
    converted: '已转化'
  }
  return map[status] || status
}

const getPlanStatusText = (status: string): string => {
  const map: Record<string, string> = {
    draft: '草稿',
    confirmed: '已确认',
    borrowing: '借用中',
    completed: '已完成'
  }
  return map[status] || status
}

const prevMonth = () => {
  if (currentMonth.value === 1) {
    currentMonth.value = 12
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 12) {
    currentMonth.value = 1
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

const goToToday = () => {
  const today = new Date()
  currentYear.value = today.getFullYear()
  currentMonth.value = today.getMonth() + 1
}

const resetFilters = () => {
  dateRange.value = []
  filterStatus.value = ''
  filterTea.value = ''
  filterColor.value = ''
  loadReservations()
}

const checkConflict = async () => {
  if (!formData.value.expected_date || !formData.value.time_slot) return
  try {
    const res = await reservationApi.checkConflict({
      check_date: formData.value.expected_date,
      time_slot: formData.value.time_slot,
      exclude_reservation_id: isEditing.value ? editingId.value : undefined
    })
    conflictResult.value = res.data
  } catch (e) {
    conflictResult.value = null
  }
}

const openCreateDialog = (date?: string | Event) => {
  isEditing.value = false
  editingId.value = 0
  conflictResult.value = null
  const parsedDate = typeof date === 'string' ? date : ''
  formData.value = {
    customer_name: '',
    customer_phone: '',
    expected_date: parsedDate,
    time_slot: '全天',
    people_count: 4,
    budget: 1000,
    preferred_color: '',
    preferred_tea: '',
    photo_style: '',
    remark: '',
    status: 'pending'
  }
  showFormDialog.value = true
}

const editReservation = (row: Reservation) => {
  isEditing.value = true
  editingId.value = row.id
  conflictResult.value = null
  formData.value = {
    customer_name: row.customer_name,
    customer_phone: row.customer_phone,
    expected_date: row.expected_date,
    time_slot: row.time_slot,
    people_count: row.people_count,
    budget: row.budget,
    preferred_color: row.preferred_color || '',
    preferred_tea: row.preferred_tea || '',
    photo_style: row.photo_style || '',
    remark: row.remark || '',
    status: row.status
  }
  showDetailDialog.value = false
  showFormDialog.value = true
}

const viewReservation = async (row: Reservation) => {
  try {
    const res = await reservationApi.getOne(row.id)
    currentReservation.value = res.data
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

const saveReservation = async () => {
  if (!formData.value.customer_name || !formData.value.customer_phone ||
      !formData.value.expected_date || !formData.value.time_slot ||
      !formData.value.people_count || !formData.value.budget) {
    ElMessage.warning('请填写必填信息')
    return
  }
  try {
    if (isEditing.value) {
      await reservationApi.update(editingId.value, formData.value)
      ElMessage.success('预约修改成功')
    } else {
      await reservationApi.create(formData.value)
      ElMessage.success('预约创建成功')
    }
    showFormDialog.value = false
    loadReservations()
  } catch (e: any) {
    if (e?.response?.status === 409) {
      conflictResult.value = e.response.data.detail.conflicts
        ? { has_conflict: true, conflicts: e.response.data.detail.conflicts }
        : { has_conflict: true, conflicts: [] }
      ElMessage.error(e.response.data.detail?.message || '时段冲突，无法保存')
    } else {
      ElMessage.error(isEditing.value ? '修改失败' : '创建失败')
    }
  }
}

const confirmReservation = async (row: Reservation) => {
  try {
    await ElMessageBox.confirm(
      `确定要确认 ${row.customer_name} 的预约吗？确认后将锁定该时段。`,
      '确认预约',
      { type: 'warning' }
    )
    await reservationApi.confirm(row.id)
    ElMessage.success('预约已确认')
    loadReservations()
    if (currentReservation.value?.id === row.id) {
      currentReservation.value.status = 'confirmed'
    }
  } catch (e: any) {
    if (e?.response?.status === 409) {
      const conflicts = e.response.data.detail?.conflicts || []
      const conflictMsgs = conflicts.map((c: any) =>
        `[${c.time_slot}] ${c.type === 'plan' ? '茶席方案' : '预约'}: ${c.name}`
      ).join('\n')
      ElMessage.error(`时段冲突，无法确认：\n${conflictMsgs}`)
    } else if (e !== 'cancel') {
      ElMessage.error('确认失败')
    }
  }
}

const cancelReservation = async (row: Reservation) => {
  try {
    await ElMessageBox.confirm(
      `确定要取消 ${row.customer_name} 的预约吗？此操作不可恢复。`,
      '取消预约',
      { type: 'warning' }
    )
    await reservationApi.cancel(row.id)
    ElMessage.success('预约已取消')
    loadReservations()
    if (currentReservation.value?.id === row.id) {
      currentReservation.value.status = 'cancelled'
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const convertToPlan = (row: Reservation) => {
  currentReservation.value = row
  convertForm.value = {
    theme_id: 0,
    name: `${row.customer_name}-${row.expected_date}`
  }
  showDetailDialog.value = false
  showConvertDialog.value = true
}

const doConvert = async () => {
  if (!convertForm.value.name || !convertForm.value.theme_id) {
    ElMessage.warning('请填写方案名称并选择主题')
    return
  }
  try {
    const res = await reservationApi.convert(currentReservation.value!.id, convertForm.value)
    ElMessage.success(`已成功转化为茶席方案，方案ID: ${res.data.id}`)
    showConvertDialog.value = false
    loadReservations()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '转化失败')
  }
}

const loadReservations = async () => {
  try {
    const params: any = {}
    if (filterStatus.value) params.status = filterStatus.value
    if (dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    if (filterTea.value) params.tea_category = filterTea.value
    if (filterColor.value) params.theme_color = filterColor.value
    const res = await reservationApi.getAll(params)
    reservations.value = res.data
  } catch (e) {
    ElMessage.error('加载预约列表失败')
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

onMounted(() => {
  loadReservations()
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

.calendar-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
  margin-bottom: 15px;
}

.calendar-title {
  font-size: 18px;
  font-weight: bold;
  color: #8B4513;
  min-width: 120px;
  text-align: center;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 2px solid #d4c4a8;
  margin-bottom: 8px;
}

.weekday {
  text-align: center;
  padding: 10px;
  font-weight: bold;
  color: #8B4513;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  min-height: 100px;
  padding: 6px;
  border: 1px solid #f0e8dc;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fffef8;
}

.calendar-day:hover {
  background: #f5f0e8;
  border-color: #d4c4a8;
}

.calendar-day.other-month {
  background: #faf7f0;
  opacity: 0.5;
}

.calendar-day.today {
  background: #fff5e6;
  border-color: #d4a574;
}

.calendar-day.has-events {
  background: #f0f8ff;
}

.day-number {
  font-weight: bold;
  color: #5c4033;
  margin-bottom: 4px;
}

.day-events {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-item {
  font-size: 11px;
  padding: 3px 6px;
  border-radius: 3px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.event-item:hover {
  opacity: 0.8;
}

.event-pending {
  background: #fff3cd;
  color: #856404;
}

.event-confirmed {
  background: #d4edda;
  color: #155724;
}

.event-converted {
  background: #d1ecf1;
  color: #0c5460;
}

.event-time {
  font-weight: bold;
  margin-right: 4px;
}

.more-events {
  font-size: 11px;
  color: #8B4513;
  text-align: center;
  padding: 2px;
}

.theme-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 12px;
  color: #fff;
  font-size: 12px;
}

.status-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
  color: #fff;
}

.status-pending {
  background: #f0ad4e;
}

.status-confirmed {
  background: #5cb85c;
}

.status-cancelled {
  background: #d9534f;
}

.status-converted {
  background: #5bc0de;
}

.status-draft {
  background: #999;
}

.status-borrowing {
  background: #f0ad4e;
}

.status-completed {
  background: #5cb85c;
}
</style>
