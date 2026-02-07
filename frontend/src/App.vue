<script setup>
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  if (userStore.token) {
    userStore.fetchUserInfo()
  }
})
</script>

<template>
  <router-view />
</template>

<style>
/* Global styles are in assets/main.css */
</style>
