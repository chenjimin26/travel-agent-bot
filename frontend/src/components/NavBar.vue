<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <span class="brand-icon">🌍</span>
      <h1 class="brand-title">旅行攻略助手</h1>
    </div>
    <div class="navbar-actions">
      <button class="mode-toggle" @click="toggleMode" :title="modeLabel">
        <span class="mode-icon">{{ store.queryMode === 'precision' ? '🎯' : '⚡' }}</span>
        <span class="mode-text">{{ store.queryMode === 'precision' ? '精度' : '快速' }}</span>
      </button>
      <StatusBadge :is-online="isOnline" />
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useChatStore } from '../stores/chat'
import StatusBadge from './StatusBadge.vue'

defineProps({
  isOnline: { type: Boolean, default: true }
})

const store = useChatStore()

const modeLabel = computed(() =>
  store.queryMode === 'precision' ? '切换到快速查询' : '切换到精度查询'
)

function toggleMode() {
  store.queryMode = store.queryMode === 'precision' ? 'fast' : 'precision'
}
</script>

<style scoped>
.navbar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-lg);
  background: var(--color-ai-bubble);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
  z-index: 10;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.brand-icon {
  font-size: 28px;
  line-height: 1;
}

.brand-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text);
  letter-spacing: 0.5px;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
}

.mode-toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border: 1px solid var(--color-border);
  border-radius: 20px;
  background: var(--color-bg);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  font-family: var(--font-family);
}

.mode-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.mode-icon {
  font-size: 14px;
}

.mode-text {
  font-size: 12px;
}
</style>