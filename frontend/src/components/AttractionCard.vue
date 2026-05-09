<template>
  <div class="attraction-card">
    <div class="card-header">
      <span class="card-icon">🏯</span>
      <div class="card-title-group">
        <h4 class="card-name">{{ attraction.name }}</h4>
        <span class="card-city">📍 {{ attraction.city }}</span>
      </div>
    </div>
    <div class="card-body">
      <div class="card-meta">
        <span v-if="attraction.ticket" class="meta-item">
          <span class="meta-icon">🎫</span>
          {{ attraction.ticket }}
        </span>
        <span v-if="attraction.open_time" class="meta-item">
          <span class="meta-icon">⏱️</span>
          {{ attraction.open_time }}
        </span>
        <span v-if="attraction.best_season" class="meta-item">
          <span class="meta-icon">🌸</span>
          {{ attraction.best_season }}
        </span>
      </div>
      <div v-if="attraction.tags && attraction.tags.length" class="card-tags">
        <span v-for="tag in attraction.tags" :key="tag" class="tag">
          #{{ tag }}
        </span>
      </div>
      <p v-if="attraction.description" class="card-desc line-clamp-2">
        {{ attraction.description }}
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  attraction: {
    type: Object,
    required: true,
    validator: (obj) => obj.name
  }
})
</script>

<style scoped>
.attraction-card {
  background: var(--color-card-bg);
  border-radius: var(--radius-lg);
  padding: var(--space-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border);
  transition: all var(--transition-normal);
  animation: fadeInUp var(--transition-normal) ease-out;
  width: 100%;
  min-width: 0;
}

.attraction-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.card-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.card-icon {
  font-size: 24px;
  flex-shrink: 0;
  margin-top: 2px;
}

.card-title-group {
  min-width: 0;
}

.card-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: 2px;
}

.card-city {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.card-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs) var(--space-md);
}

.meta-item {
  font-size: 12px;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 3px;
}

.meta-icon {
  font-size: 14px;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.tag {
  font-size: 11px;
  padding: 2px 8px;
  background: var(--color-primary-light);
  color: var(--color-primary-dark);
  border-radius: 12px;
  font-weight: 500;
}

.card-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}
</style>