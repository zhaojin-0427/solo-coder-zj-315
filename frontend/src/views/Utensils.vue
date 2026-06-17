<template>
  <div class="page-container">
    <div class="page-header">
      <h2>🏺 器物库管理</h2>
      <el-button type="primary" class="chinese-btn" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新增器物
      </el-button>
    </div>

    <el-row :gutter="20" class="filter-bar">
      <el-col :span="6">
        <el-select v-model="filterCategory" placeholder="选择分类" clearable @change="loadUtensils">
          <el-option v-for="cat in UTENSIL_CATEGORIES" :key="cat" :label="cat" :value="cat" />
        </el-select>
      </el-col>
      <el-col :span="6">
        <el-input v-model="searchKeyword" placeholder="搜索器物名称" clearable @input="loadUtensils" />
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col v-for="utensil in filteredUtensils" :key="utensil.id" :span="6">
        <div class="utensil-card card-shadow" style="padding: 20px; margin-bottom: 20px">
          <div class="utensil-icon">
            {{ getCategoryIcon(utensil.category) }}
          </div>
          <h4 style="color: #8B4513; margin: 10px 0 5px">{{ utensil.name }}</h4>
          <div class="utensil-info">
            <span class="tag">{{ utensil.category }}</span>
            <span class="tag tag-material">{{ utensil.material }}</span>
            <span class="tag tag-color" :style="{ background: getColorStyle(utensil.color) }">
              {{ utensil.color }}
            </span>
          </div>
          <div style="margin: 10px 0; font-size: 12px; color: #666">
            风格: {{ utensil.style }}
          </div>
          <div class="utensil-stats">
            <div>
              <span class="stat-label">价格</span>
              <span class="stat-value">¥{{ utensil.price }}</span>
            </div>
            <div>
              <span class="stat-label">库存</span>
              <span class="stat-value" :class="{ 'low-stock': utensil.available < 3 }">
                {{ utensil.available }}/{{ utensil.quantity }}
              </span>
            </div>
          </div>
          <div style="margin-top: 10px; font-size: 12px; color: #888; line-height: 1.5">
            {{ utensil.description }}
          </div>
          <div style="margin-top: 15px">
            <el-button size="small" type="primary" link @click="editUtensil(utensil)">编辑</el-button>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog v-model="showCreateDialog" :title="isEditing ? '编辑器物' : '新增器物'" width="600px">
      <el-form :model="formData" label-width="100px" @submit.prevent>
        <el-form-item label="器物名称" required>
          <el-input v-model="formData.name" placeholder="请输入器物名称" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" required>
              <el-select v-model="formData.category" placeholder="请选择分类" style="width: 100%">
                <el-option v-for="cat in UTENSIL_CATEGORIES" :key="cat" :label="cat" :value="cat" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材质" required>
              <el-select v-model="formData.material" placeholder="请选择材质" style="width: 100%">
                <el-option v-for="mat in MATERIALS" :key="mat" :label="mat" :value="mat" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="颜色" required>
              <el-select v-model="formData.color" placeholder="请选择颜色" style="width: 100%">
                <el-option v-for="color in COLORS" :key="color" :label="color" :value="color">
                  <span class="color-dot" :style="{ background: getColorStyle(color) }"></span>
                  {{ color }}
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="风格" required>
              <el-input v-model="formData.style" placeholder="请输入风格" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="价格" required>
              <el-input-number v-model="formData.price" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总数量" required>
              <el-input-number v-model="formData.quantity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="可用数" required>
              <el-input-number v-model="formData.available" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" class="chinese-btn" @click="saveUtensil">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { utensilApi } from '@/api'
import { UTENSIL_CATEGORIES, MATERIALS, COLORS } from '@/types'
import type { Utensil } from '@/types'

const utensils = ref<Utensil[]>([])
const filterCategory = ref<string>('')
const searchKeyword = ref<string>('')
const showCreateDialog = ref(false)
const isEditing = ref(false)
const editingId = ref<number>(0)

const formData = ref({
  name: '',
  category: '',
  material: '',
  color: '',
  style: '',
  price: 0,
  quantity: 1,
  available: 1,
  description: '',
  image_url: ''
})

const filteredUtensils = computed(() => {
  return utensils.value.filter(u => {
    const matchCategory = !filterCategory.value || u.category === filterCategory.value
    const matchKeyword = !searchKeyword.value || u.name.includes(searchKeyword.value)
    return matchCategory && matchKeyword
  })
})

const getCategoryIcon = (category: string) => {
  const icons: Record<string, string> = {
    '盖碗': '🍵',
    '茶海': '🫖',
    '杯盏': '🥛',
    '席布': '🧣',
    '花器': '🌸'
  }
  return icons[category] || '🏺'
}

const getColorStyle = (color: string) => {
  const colorMap: Record<string, string> = {
    '朱红': '#CD5C5C', '赭石': '#A0522D', '胭脂': '#C71585',
    '琥珀': '#FFBF00', '金黄': '#FFD700', '橙黄': '#FFA500',
    '青色': '#5F9EA0', '湖蓝': '#4682B4', '黛绿': '#556B2F',
    '松石': '#40E0D0', '月白': '#B0C4DE', '藏青': '#2F4F4F',
    '米白': '#F5F5DC', '象牙': '#FFFFF0', '玄黑': '#1C1C1C',
    '紫砂': '#8B4513', '灰墨': '#696969', '素白': '#FFFFFF',
    '青花': '#1E90FF'
  }
  return colorMap[color] || '#8B4513'
}

const loadUtensils = async () => {
  try {
    const res = await utensilApi.getAll(filterCategory.value || undefined)
    utensils.value = res.data
  } catch (e) {
    ElMessage.error('加载器物失败')
  }
}

const editUtensil = (utensil: Utensil) => {
  isEditing.value = true
  editingId.value = utensil.id
  formData.value = { ...utensil }
  showCreateDialog.value = true
}

const closeDialog = () => {
  showCreateDialog.value = false
  isEditing.value = false
  resetForm()
}

const resetForm = () => {
  formData.value = {
    name: '',
    category: '',
    material: '',
    color: '',
    style: '',
    price: 0,
    quantity: 1,
    available: 1,
    description: '',
    image_url: ''
  }
}

const saveUtensil = async () => {
  if (!formData.value.name || !formData.value.category || !formData.value.material || !formData.value.color || !formData.value.style) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    if (isEditing.value) {
      await utensilApi.update(editingId.value, formData.value)
      ElMessage.success('更新成功')
    } else {
      await utensilApi.create(formData.value as any)
      ElMessage.success('新增成功')
    }
    closeDialog()
    loadUtensils()
  } catch (e) {
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  loadUtensils()
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

.utensil-icon {
  font-size: 48px;
  text-align: center;
  margin-bottom: 10px;
}

.utensil-info {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  background: #e8dcc8;
  color: #8B4513;
}

.tag-material {
  background: #d4e8d4;
  color: #2E7D32;
}

.tag-color {
  color: #fff;
}

.utensil-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px dashed #d4c4a8;
}

.stat-label {
  display: block;
  font-size: 11px;
  color: #888;
}

.stat-value {
  display: block;
  font-size: 16px;
  font-weight: bold;
  color: #8B4513;
}

.low-stock {
  color: #CD5C5C;
}

.color-dot {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 8px;
  vertical-align: middle;
}

.filter-bar {
  margin-bottom: 10px;
}
</style>
