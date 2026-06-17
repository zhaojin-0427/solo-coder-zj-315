<template>
  <div class="page-container">
    <div class="page-header">
      <h2>📋 布席清单管理</h2>
    </div>

    <el-row :gutter="20" class="filter-bar">
      <el-col :span="6">
        <el-select v-model="filterStatus" placeholder="选择状态" clearable @change="loadBorrowLists">
          <el-option label="待借用" value="pending" />
          <el-option label="借用中" value="borrowing" />
          <el-option label="已归还" value="returned" />
        </el-select>
      </el-col>
    </el-row>

    <el-table :data="borrowLists" class="card-shadow" style="width: 100%; margin-top: 20px">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="plan_id" label="方案ID" width="100" />
      <el-table-column label="方案名称" width="180">
        <template #default="{ row }">{{ getPlanName(row.plan_id) }}</template>
      </el-table-column>
      <el-table-column prop="borrow_date" label="借用日期" width="120" />
      <el-table-column prop="return_date" label="归还日期" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <span :class="['status-badge', `status-${row.status}`]">
            {{ getStatusText(row.status) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" link @click="viewDetail(row)">查看明细</el-button>
          <el-button size="small" type="success" link @click="startBorrow(row)" v-if="row.status === 'pending'">开始借用</el-button>
          <el-button size="small" type="warning" link @click="completeReturn(row)" v-if="row.status === 'borrowing'">完成归还</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="showDetailDialog" title="布席清单明细" width="800px">
      <div v-if="currentBorrow">
        <el-descriptions :column="2" border class="card-shadow" style="margin-bottom: 20px">
          <el-descriptions-item label="方案名称">{{ getPlanName(currentBorrow.plan_id) }}</el-descriptions-item>
          <el-descriptions-item label="借用日期">{{ currentBorrow.borrow_date }}</el-descriptions-item>
          <el-descriptions-item label="应还日期">{{ currentBorrow.return_date }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <span :class="['status-badge', `status-${currentBorrow.status}`]">
              {{ getStatusText(currentBorrow.status) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin: 20px 0 10px">借用器物明细</h3>
        <el-table :data="currentBorrow.items" class="card-shadow">
          <el-table-column prop="utensil.name" label="器物名称" width="180" />
          <el-table-column prop="utensil.category" label="分类" width="100" />
          <el-table-column prop="utensil.material" label="材质" width="100" />
          <el-table-column prop="quantity" label="数量" width="80" align="center" />
          <el-table-column label="单价" width="100">
            <template #default="{ row }">¥{{ row.utensil.price }}</template>
          </el-table-column>
          <el-table-column label="小计" width="120">
            <template #default="{ row }">¥{{ row.utensil.price * row.quantity }}</template>
          </el-table-column>
          <el-table-column label="借用状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.borrowed ? 'success' : 'info'" size="small">
                {{ row.borrowed ? '已借出' : '待借出' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="归还状态" width="120">
            <template #default="{ row }">
              <el-tag :type="row.returned ? 'success' : 'warning'" size="small">
                {{ row.returned ? '已归还' : '待归还' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button 
                v-if="!row.borrowed" 
                size="small" 
                type="success" 
                link
                @click="markBorrowed(row)"
              >
                确认借出
              </el-button>
              <el-button 
                v-if="row.borrowed && !row.returned" 
                size="small" 
                type="warning" 
                link
                @click="markReturned(row)"
              >
                确认归还
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div style="margin-top: 20px; text-align: right; font-size: 18px; color: #8B4513">
          合计: ¥{{ calculateTotal() }}
        </div>
      </div>
      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { borrowListApi, teaPlanApi } from '@/api'
import type { BorrowList, TeaPlan } from '@/types'

const borrowLists = ref<BorrowList[]>([])
const plans = ref<TeaPlan[]>([])
const filterStatus = ref<string>('')
const showDetailDialog = ref(false)
const currentBorrow = ref<BorrowList | null>(null)

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待借用',
    borrowing: '借用中',
    returned: '已归还'
  }
  return map[status] || status
}

const getPlanName = (planId: number) => {
  const plan = plans.value.find(p => p.id === planId)
  return plan?.name || `方案#${planId}`
}

const loadBorrowLists = async () => {
  try {
    const res = await borrowListApi.getAll(filterStatus.value || undefined)
    borrowLists.value = res.data
  } catch (e) {
    ElMessage.error('加载清单失败')
  }
}

const loadPlans = async () => {
  try {
    const res = await teaPlanApi.getAll()
    plans.value = res.data
  } catch (e) {
    ElMessage.error('加载方案失败')
  }
}

const viewDetail = async (row: BorrowList) => {
  try {
    const res = await borrowListApi.getOne(row.id)
    currentBorrow.value = res.data
    showDetailDialog.value = true
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

const startBorrow = async (row: BorrowList) => {
  try {
    await borrowListApi.update(row.id, { status: 'borrowing' })
    ElMessage.success('已开始借用')
    loadBorrowLists()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const completeReturn = async (row: BorrowList) => {
  try {
    await borrowListApi.update(row.id, { status: 'returned' })
    ElMessage.success('已完成归还')
    loadBorrowLists()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const markBorrowed = async (item: any) => {
  try {
    await borrowListApi.updateItem(item.id, { borrowed: true })
    ElMessage.success('已确认借出')
    if (currentBorrow.value) {
      const res = await borrowListApi.getOne(currentBorrow.value.id)
      currentBorrow.value = res.data
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const markReturned = async (item: any) => {
  try {
    await borrowListApi.updateItem(item.id, { returned: true })
    ElMessage.success('已确认归还')
    if (currentBorrow.value) {
      const res = await borrowListApi.getOne(currentBorrow.value.id)
      currentBorrow.value = res.data
    }
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const calculateTotal = () => {
  if (!currentBorrow.value) return 0
  return currentBorrow.value.items.reduce((sum, item) => {
    return sum + item.utensil.price * item.quantity
  }, 0)
}

onMounted(() => {
  loadBorrowLists()
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

.filter-bar {
  margin-bottom: 10px;
}

.status-pending {
  background: #e2e8f0;
  color: #475569;
}

.status-returned {
  background: #d1fae5;
  color: #065f46;
}
</style>
