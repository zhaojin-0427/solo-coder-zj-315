<template>
  <div class="app-container">
    <header class="chinese-header">
      <div class="header-content">
        <h1>🍵 新中式茶席主题策划与器物借用管理系统</h1>
        <el-menu
          mode="horizontal"
          :router="true"
          :default-active="$route.path"
          class="nav-menu"
        >
          <el-menu-item index="/reservations">
            <el-icon><Calendar /></el-icon>
            预约排期
          </el-menu-item>
          <el-menu-item index="/customer-profiles">
            <el-icon><User /></el-icon>
            客户档案
          </el-menu-item>
          <el-menu-item index="/tea-plans">
            <el-icon><Document /></el-icon>
            主题方案
          </el-menu-item>
          <el-menu-item index="/utensils">
            <el-icon><Collection /></el-icon>
            器物库
          </el-menu-item>
          <el-menu-item index="/borrow-lists">
            <el-icon><List /></el-icon>
            布席清单
          </el-menu-item>
          <el-menu-item index="/reviews">
            <el-icon><EditPen /></el-icon>
            活动复盘
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><DataAnalysis /></el-icon>
            数据统计
          </el-menu-item>
        </el-menu>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import { Calendar, Document, Collection, List, EditPen, DataAnalysis, User } from '@element-plus/icons-vue'
</script>

<style scoped>
.header-content {
  max-width: 1400px;
  margin: 0 auto;
}

.nav-menu {
  margin-top: 15px;
}
</style>
