<template>
  <div class="page-container">
    <div class="page-header">
      <h2>📊 数据统计</h2>
      <el-button type="primary" class="chinese-btn" @click="loadStats">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
    </div>

    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <div class="stat-card">
          <div class="label">总订单数</div>
          <div class="value">{{ stats?.total_orders || 0 }}</div>
          <el-icon><Tickets /></el-icon>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="label">总营收</div>
          <div class="value">¥{{ (stats?.total_revenue || 0).toFixed(0) }}</div>
          <el-icon><Money /></el-icon>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="label">平均评分</div>
          <div class="value">{{ (stats?.avg_rating || 0).toFixed(1) }}</div>
          <el-icon><Star /></el-icon>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card">
          <div class="label">平均客单价</div>
          <div class="value">¥{{ avgPrice.toFixed(0) }}</div>
          <el-icon><PriceTag /></el-icon>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">📈 各主题预约量</h3>
          <v-chart class="chart" :option="themeChartOption" autoresize />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">💰 客单价区间分布</h3>
          <v-chart class="chart" :option="priceChartOption" autoresize />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">🎨 主题色预约量</h3>
          <v-chart class="chart" :option="colorReservationChartOption" autoresize />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">🍵 茶类预约量</h3>
          <v-chart class="chart" :option="teaCategoryReservationChartOption" autoresize />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">🏆 器物使用频次 TOP 10</h3>
          <v-chart class="chart" :option="usageChartOption" autoresize />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">⚠️ 器物破损率</h3>
          <v-chart class="chart" :option="damageChartOption" autoresize />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">🔄 复购茶席类型统计</h3>
          <v-chart class="chart" :option="repeatChartOption" autoresize />
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">📋 器物使用频次明细</h3>
          <el-table :data="stats?.utensil_usage_stats || []" size="small">
            <el-table-column prop="utensil_name" label="器物名称" width="200" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="usage_count" label="使用次数" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="primary" size="small">{{ row.usage_count }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">🔧 器物破损明细</h3>
          <el-table :data="stats?.damage_stats || []" size="small">
            <el-table-column prop="utensil_name" label="器物名称" width="200" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="damage_count" label="破损次数" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="row.damage_count > 0 ? 'danger' : 'success'" size="small">
                  {{ row.damage_count }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="damage_rate" label="破损率" width="120" align="center">
              <template #default="{ row }">
                <el-progress 
                  :percentage="Math.min(row.damage_rate, 100)" 
                  :color="row.damage_rate > 10 ? '#f56c6c' : '#67c23a'"
                  :stroke-width="10"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">🎨 主题色预约量明细</h3>
          <el-table :data="stats?.color_reservation_stats || []" size="small">
            <el-table-column prop="theme_color" label="主题色" width="150">
              <template #default="{ row }">
                <span class="color-dot" :style="{ background: getColorHex(row.theme_color) }"></span>
                {{ row.theme_color }}
              </template>
            </el-table-column>
            <el-table-column prop="count" label="预约量" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="primary" size="small">{{ row.count }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card card-shadow">
          <h3 class="chart-title">🍵 茶类预约量明细</h3>
          <el-table :data="stats?.tea_category_reservation_stats || []" size="small">
            <el-table-column prop="tea_category" label="茶类" width="150" />
            <el-table-column prop="count" label="预约量" width="120" align="center">
              <template #default="{ row }">
                <el-tag type="primary" size="small">{{ row.count }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import { Refresh, Tickets, Money, Star, PriceTag } from '@element-plus/icons-vue'
import { statsApi } from '@/api'
import type { StatisticsResponse } from '@/types'

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const stats = ref<StatisticsResponse | null>(null)

const avgPrice = computed(() => {
  if (!stats.value || stats.value.total_orders === 0) return 0
  return stats.value.total_revenue / stats.value.total_orders
})

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

const themeChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' }
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: stats.value?.theme_stats.map(t => t.theme_name) || [],
    axisLabel: { color: '#8B4513' }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#8B4513' }
  },
  series: [{
    data: stats.value?.theme_stats.map(t => t.count) || [],
    type: 'bar',
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: '#CD853F' },
          { offset: 1, color: '#8B4513' }
        ]
      },
      borderRadius: [8, 8, 0, 0]
    },
    barWidth: '50%'
  }]
}))

const priceChartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c}个 ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    name: '客单价区间',
    type: 'pie',
    radius: ['40%', '70%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: false },
    emphasis: {
      label: { show: true, fontSize: 16, fontWeight: 'bold' }
    },
    data: stats.value?.price_range_stats.map(p => ({
      value: p.count,
      name: p.range
    })) || [],
    color: ['#D2B48C', '#CD853F', '#A0522D', '#8B4513', '#654321']
  }]
}))

const colorReservationChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: (params: any) => {
      const p = params[0]
      return `${p.name}<br/>预约量: <b>${p.value}</b>`
    }
  },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: stats.value?.color_reservation_stats.map(c => c.theme_color) || [],
    axisLabel: { color: '#8B4513' }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#8B4513' }
  },
  series: [{
    data: stats.value?.color_reservation_stats.map(c => ({
      value: c.count,
      itemStyle: {
        color: getColorHex(c.theme_color),
        borderRadius: [8, 8, 0, 0]
      }
    })) || [],
    type: 'bar',
    barWidth: '50%'
  }]
}))

const teaCategoryReservationChartOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c}次 ({d}%)' },
  legend: { orient: 'vertical', left: 'left' },
  series: [{
    name: '茶类预约量',
    type: 'pie',
    radius: ['35%', '65%'],
    avoidLabelOverlap: false,
    itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
    label: { show: true, formatter: '{b}\n{c}次' },
    emphasis: {
      label: { show: true, fontSize: 16, fontWeight: 'bold' }
    },
    data: stats.value?.tea_category_reservation_stats.map(t => ({
      value: t.count,
      name: t.tea_category
    })) || [],
    color: ['#8FBC8F', '#CD853F', '#A0522D', '#8B4513', '#B8860B', '#556B2F']
  }]
}))

const usageChartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'value',
    axisLabel: { color: '#8B4513' }
  },
  yAxis: {
    type: 'category',
    data: stats.value?.utensil_usage_stats.map(u => u.utensil_name).reverse() || [],
    axisLabel: { color: '#8B4513' }
  },
  series: [{
    data: stats.value?.utensil_usage_stats.map(u => u.usage_count).reverse() || [],
    type: 'bar',
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [
          { offset: 0, color: '#556B2F' },
          { offset: 1, color: '#8FBC8F' }
        ]
      },
      borderRadius: [0, 8, 8, 0]
    }
  }]
}))

const damageChartOption = computed(() => ({
  tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: stats.value?.damage_stats.map(d => d.utensil_name) || [],
    axisLabel: { color: '#8B4513', rotate: 30 }
  },
  yAxis: {
    type: 'value',
    max: 100,
    axisLabel: { color: '#8B4513', formatter: '{value}%' }
  },
  series: [{
    data: stats.value?.damage_stats.map(d => Math.min(d.damage_rate, 100)) || [],
    type: 'line',
    smooth: true,
    itemStyle: { color: '#CD5C5C' },
    areaStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: 'rgba(205, 92, 92, 0.5)' },
          { offset: 1, color: 'rgba(205, 92, 92, 0.05)' }
        ]
      }
    },
    lineStyle: { width: 3 }
  }]
}))

const repeatChartOption = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  legend: { data: ['复购次数', '总订单数'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: stats.value?.repeat_type_stats.map(r => r.tea_type) || [],
    axisLabel: { color: '#8B4513' }
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#8B4513' }
  },
  series: [
    {
      name: '复购次数',
      type: 'bar',
      data: stats.value?.repeat_type_stats.map(r => r.count) || [],
      itemStyle: {
        color: '#9370DB',
        borderRadius: [8, 8, 0, 0]
      },
      barWidth: '40%'
    }
  ]
}))

const loadStats = async () => {
  try {
    const res = await statsApi.getStatistics()
    stats.value = res.data
  } catch (e) {
    console.error('加载统计数据失败', e)
  }
}

onMounted(() => {
  loadStats()
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

.chart-card {
  padding: 20px;
  background: #fffaf0;
  border-radius: 8px;
}

.chart-title {
  color: #8B4513;
  font-size: 16px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px dashed #d4c4a8;
}

.chart {
  height: 350px;
}

.stat-card {
  position: relative;
  background: linear-gradient(135deg, #fffaf0 0%, #f5e6d3 100%);
  border-radius: 12px;
  padding: 25px;
  text-align: left;
  border: 1px solid #d4c4a8;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(139, 69, 19, 0.2);
}

.stat-card .label {
  color: #8B7355;
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-card .value {
  font-size: 32px;
  font-weight: bold;
  color: #8B4513;
}

.stat-card .el-icon {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 40px;
  opacity: 0.2;
  color: #8B4513;
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
