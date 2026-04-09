<script setup>
import { ref } from "vue";

// 底部标签栏选中索引
const active = ref(0);
</script>

<template>
  <div class="app-layout">
    <router-view />
    <van-tabbar v-model="active" class="tech-tabbar" active-color="#409eff" inactive-color="#909399" :border="false" route>
      <van-tabbar-item icon="home-o" to="/home">首页</van-tabbar-item>
      <van-tabbar-item icon="orders-o" to="/orders">客诉</van-tabbar-item>
      <van-tabbar-item icon="contact-o" to="/profile">我</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  padding-bottom: 50px;
}
.tech-tabbar {
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.05);
}
</style>
