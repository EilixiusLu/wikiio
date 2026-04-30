<template>
  <Navbar />
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
</script>

<style>
/* 全局样式重置 */
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Noto Sans SC', sans-serif;
  background: #f5f7fa;
  color: #1a1a2e;
  line-height: 1.6;
}
a { color: inherit; }
</style>