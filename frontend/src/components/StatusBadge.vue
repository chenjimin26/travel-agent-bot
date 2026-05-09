<template>
  <div class="status-badge" :class="{ online: isOnline, offline: !isOnline }">
    <span class="dot"></span>
    <span class="label">{{ isOnline ? '在线' : '离线' }}</span>
  </div>
</template>

<script setup>
defineProps({
  isOnline: { type: Boolean, default: true }
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.status-badge.online {
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.status-badge.offline {
  background: #FEE2E2;
  color: #DC2626;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.online .dot {
  background: var(--color-success);
  animation: pulse-dot 2s ease-in-out infinite;
}

.offline .dot {
  background: var(--color-error);
}
</style>