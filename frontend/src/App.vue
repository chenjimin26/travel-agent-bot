<template>
  <div class="app-layout">
    <NavBar :is-online="store.apiOnline" />
    <div class="app-body">
      <Sidebar />
      <ChatArea />
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useChatStore } from './stores/chat'
import { checkHealth } from './api/chat'
import NavBar from './components/NavBar.vue'
import Sidebar from './components/Sidebar.vue'
import ChatArea from './components/ChatArea.vue'

const store = useChatStore()

let healthTimer = null

onMounted(async () => {
  const result = await checkHealth()
  store.apiOnline = result.online

  healthTimer = setInterval(async () => {
    const r = await checkHealth()
    store.apiOnline = r.online
  }, 30000)
})

onUnmounted(() => {
  if (healthTimer) clearInterval(healthTimer)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.app-body {
  display: flex;
  flex: 1;
  min-height: 0;
}
</style>