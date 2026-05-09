<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h2 class="sidebar-title">对话历史</h2>
    </div>

    <button class="new-chat-btn" @click="store.newConversation()">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      新对话
    </button>

    <div class="conversation-list">
      <div
        v-for="conv in sortedConversations"
        :key="conv.id"
        class="conv-item"
        :class="{ active: conv.id === store.currentId }"
        @click="store.switchConversation(conv.id)"
        role="button"
        tabindex="0"
      >
        <div class="conv-content">
          <span class="conv-title text-ellipsis">{{ conv.title }}</span>
          <span class="conv-date">{{ formatDate(conv.updatedAt) }}</span>
        </div>
        <button
          class="conv-delete"
          @click.stop="store.deleteConversation(conv.id)"
          title="删除对话"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"></path>
          </svg>
        </button>
      </div>

      <div v-if="sortedConversations.length === 0" class="sidebar-empty">
        暂无对话，开始一段新的旅行提问吧
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useChatStore } from '../stores/chat'

const store = useChatStore()

const sortedConversations = computed(() =>
  [...store.conversations].sort((a, b) =>
    new Date(b.updatedAt) - new Date(a.updatedAt)
  )
)

function formatDate(iso) {
  const d = new Date(iso)
  const now = new Date()
  const diff = now - d
  if (diff < 3600000) return '刚刚'
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.sidebar {
  width: 280px;
  background: var(--color-sidebar);
  color: var(--color-sidebar-text);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  border-right: 1px solid #1E293B;
}

.sidebar-header {
  padding: var(--space-lg) var(--space-md) var(--space-sm);
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #94A3B8;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin: var(--space-sm) var(--space-md);
  padding: 10px 16px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.new-chat-btn:hover {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-sm) 0;
}

.conv-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 10px var(--space-md);
  background: none;
  border: none;
  color: var(--color-sidebar-text);
  text-align: left;
  cursor: pointer;
  transition: background var(--transition-fast);
  gap: var(--space-sm);
}

.conv-item:hover {
  background: var(--color-sidebar-hover);
}

.conv-item.active {
  background: var(--color-sidebar-hover);
  border-left: 3px solid var(--color-primary);
  padding-left: calc(var(--space-md) - 3px);
}

.conv-content {
  flex: 1;
  min-width: 0;
}

.conv-title {
  display: block;
  font-size: 14px;
  color: #E2E8F0;
}

.conv-date {
  display: block;
  font-size: 12px;
  color: #64748B;
  margin-top: 2px;
}

.conv-delete {
  background: none;
  border: none;
  color: #64748B;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  opacity: 0;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.conv-item:hover .conv-delete {
  opacity: 1;
}

.conv-delete:hover {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.1);
}

.sidebar-empty {
  padding: var(--space-lg) var(--space-md);
  text-align: center;
  font-size: 13px;
  color: #64748B;
  line-height: 1.6;
}
</style>