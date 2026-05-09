# Travel Chat Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Vue 3 + Vite single-page chat frontend for the Travel RAG Chatbot API with streaming responses, conversation history, and attraction cards.

**Architecture:** Vue 3 SPA with Pinia store, SSE streaming via native fetch, localStorage persistence. Components communicate through Pinia store only. Vite dev server proxies `/api` to FastAPI backend at `localhost:8000`.

**Tech Stack:** Vue 3.4, Pinia 2.1, Vite 5, @vueuse/core 10.7

---

## Wave 1: Foundation (all parallel)

### Task 1: Project Scaffold

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "travel-chat-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "pinia": "^2.1.0",
    "@vueuse/core": "^10.7.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.4.0"
  }
}
```

- [ ] **Step 2: Create vite.config.js**

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

- [ ] **Step 3: Create index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>旅行攻略助手</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🌍</text></svg>" />
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: Install dependencies**

```bash
cd frontend && npm install
```

---

### Task 2: Global Styles

**Files:**
- Create: `frontend/src/styles/main.css`

- [ ] **Step 1: Create main.css with CSS variables and base styles**

```css
/* ===== CSS Variables ===== */
:root {
  --color-primary: #10B981;
  --color-primary-dark: #059669;
  --color-primary-light: #D1FAE5;
  --color-bg: #F8FAFC;
  --color-sidebar: #1E293B;
  --color-sidebar-hover: #334155;
  --color-sidebar-text: #CBD5E1;
  --color-text: #1F2937;
  --color-text-secondary: #6B7280;
  --color-border: #E5E7EB;
  --color-error: #EF4444;
  --color-success: #22C55E;
  --color-user-bubble: #10B981;
  --color-user-text: #FFFFFF;
  --color-ai-bubble: #FFFFFF;
  --color-card-bg: #FFFFFF;
  --color-input-bg: #FFFFFF;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 4px 6px rgba(0, 0, 0, 0.07), 0 2px 4px rgba(0, 0, 0, 0.06);
  --shadow-xl: 0 10px 15px rgba(0, 0, 0, 0.1), 0 4px 6px rgba(0, 0, 0, 0.05);
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --transition-fast: 150ms ease;
  --transition-normal: 300ms ease;
  --font-family: "PingFang SC", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* ===== Reset ===== */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-family);
  color: var(--color-text);
  background: var(--color-bg);
  line-height: 1.6;
  overflow: hidden;
  height: 100vh;
}

#app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* ===== Scrollbar ===== */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-text-secondary);
}

/* ===== Animations ===== */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.fade-in-up {
  animation: fadeInUp var(--transition-normal) ease-out;
}

/* ===== Utility ===== */
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

---

### Task 3: Pinia Store

**Files:**
- Create: `frontend/src/stores/chat.js`

- [ ] **Step 1: Create chat store with messages, conversations, streaming, API status**

```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const STORAGE_KEY = 'travel-chat-conversations'
const MAX_CONVERSATIONS = 50

function loadConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const data = JSON.parse(raw)
    return Array.isArray(data) ? data : []
  } catch {
    return []
  }
}

function saveConversations(conversations) {
  try {
    const trimmed = conversations.slice(-MAX_CONVERSATIONS)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
  } catch { /* storage full, ignore */ }
}

export const useChatStore = defineStore('chat', () => {
  const conversations = ref(loadConversations())
  const currentId = ref(null)
  const isStreaming = ref(false)
  const apiOnline = ref(true)

  const currentConversation = computed(() =>
    conversations.value.find(c => c.id === currentId.value) || null
  )

  const messages = computed(() =>
    currentConversation.value?.messages || []
  )

  function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).slice(2, 9)
  }

  function newConversation() {
    const conv = {
      id: generateId(),
      title: '新对话',
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    }
    conversations.value.push(conv)
    currentId.value = conv.id
    saveConversations(conversations.value)
    return conv
  }

  function switchConversation(id) {
    currentId.value = id
  }

  function deleteConversation(id) {
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (currentId.value === id) {
      currentId.value = conversations.value.length > 0
        ? conversations.value[conversations.value.length - 1].id
        : null
    }
    saveConversations(conversations.value)
  }

  function addMessage(role, content, sources = null) {
    const conv = currentConversation.value
    if (!conv) {
      const c = newConversation()
      conv = c
    }
    const msg = {
      id: generateId(),
      role,
      content,
      sources,
      timestamp: new Date().toISOString(),
      isStreaming: role === 'assistant'
    }
    conv.messages.push(msg)
    if (role === 'user' && conv.messages.length <= 2) {
      conv.title = content.slice(0, 30) + (content.length > 30 ? '...' : '')
    }
    conv.updatedAt = new Date().toISOString()
    saveConversations(conversations.value)
    return msg
  }

  function appendToken(token) {
    const conv = currentConversation.value
    if (!conv || conv.messages.length === 0) return
    const lastMsg = conv.messages[conv.messages.length - 1]
    if (lastMsg.role === 'assistant') {
      lastMsg.content += token
    }
  }

  function finishStreaming(sources = []) {
    const conv = currentConversation.value
    if (!conv || conv.messages.length === 0) return
    const lastMsg = conv.messages[conv.messages.length - 1]
    if (lastMsg.role === 'assistant') {
      lastMsg.isStreaming = false
      lastMsg.sources = sources
    }
    isStreaming.value = false
    conv.updatedAt = new Date().toISOString()
    saveConversations(conversations.value)
  }

  function updateTitle(id, title) {
    const conv = conversations.value.find(c => c.id === id)
    if (conv) {
      conv.title = title
      saveConversations(conversations.value)
    }
  }

  return {
    conversations,
    currentId,
    isStreaming,
    apiOnline,
    currentConversation,
    messages,
    newConversation,
    switchConversation,
    deleteConversation,
    addMessage,
    appendToken,
    finishStreaming,
    updateTitle
  }
})
```

**QA:** Console log after store import to verify it instantiates without errors.

---

### Task 4: API Client

**Files:**
- Create: `frontend/src/api/chat.js`

- [ ] **Step 1: Create API client with health check and SSE streaming**

```javascript
const API_BASE = '/api/v1'

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE.replace('/v1', '')}/health`, {
      signal: AbortSignal.timeout(5000)
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    return { online: true, ...data }
  } catch {
    return { online: false }
  }
}

export async function sendMessage(message, sessionId = null, callbacks = {}) {
  const { onToken, onDone, onError } = callbacks

  const body = { message }
  if (sessionId) body.session_id = sessionId

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      const errText = await response.text().catch(() => 'Unknown error')
      throw new Error(errText || `HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let sources = []

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || trimmed === 'data: [DONE]') continue

        if (trimmed.startsWith('data: ')) {
          const data = trimmed.slice(6)
          // Try to parse as JSON (sources)
          try {
            const parsed = JSON.parse(data)
            if (parsed.sources) {
              sources = parsed.sources
            }
          } catch {
            // Plain text token
            if (onToken) onToken(data)
          }
        }
      }
    }

    if (onDone) onDone(sources)
  } catch (err) {
    if (err.name === 'AbortError') return
    if (onError) onError(err.message || '网络连接失败，请检查网络')
  }
}
```

**QA:** After main.js is set up, check that `checkHealth()` resolves in browser console.

---

## Wave 2: Components (all parallel)

### Task 5: StatusBadge + NavBar

**Files:**
- Create: `frontend/src/components/StatusBadge.vue`
- Create: `frontend/src/components/NavBar.vue`

- [ ] **Step 1: Create StatusBadge.vue**

```vue
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
```

- [ ] **Step 2: Create NavBar.vue**

```vue
<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <span class="brand-icon">🌍</span>
      <h1 class="brand-title">旅行攻略助手</h1>
    </div>
    <div class="navbar-actions">
      <StatusBadge :is-online="isOnline" />
    </div>
  </nav>
</template>

<script setup>
import StatusBadge from './StatusBadge.vue'

defineProps({
  isOnline: { type: Boolean, default: true }
})
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
</style>
```

**QA:** Open dev server, verify NavBar renders with logo and status badge.

---

### Task 6: Sidebar

**Files:**
- Create: `frontend/src/components/Sidebar.vue`

- [ ] **Step 1: Create Sidebar.vue with conversation list**

```vue
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
      <button
        v-for="conv in sortedConversations"
        :key="conv.id"
        class="conv-item"
        :class="{ active: conv.id === store.currentId }"
        @click="store.switchConversation(conv.id)"
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
      </button>

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
```

**QA:** Open dev server, verify sidebar shows empty state, click "新对话" creates one, delete works.

---

### Task 7: AttractionCard

**Files:**
- Create: `frontend/src/components/AttractionCard.vue`

- [ ] **Step 1: Create AttractionCard.vue**

```vue
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
```

**QA:** Import and render with sample data, verify all fields display correctly.

---

### Task 8: ChatInput

**Files:**
- Create: `frontend/src/components/ChatInput.vue`

- [ ] **Step 1: Create ChatInput.vue**

```vue
<template>
  <div class="chat-input-wrapper">
    <div class="chat-input-container">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        class="chat-input"
        :placeholder="isStreaming ? '等待回复中...' : '输入你的旅行问题...'"
        :disabled="isStreaming"
        :rows="1"
        @input="autoResize"
        @keydown.enter.exact.prevent="handleSend"
      ></textarea>
      <button
        class="send-btn"
        :class="{ disabled: !canSend }"
        :disabled="!canSend"
        @click="handleSend"
      >
        <svg v-if="!isStreaming" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="22" y1="2" x2="11" y2="13"></line>
          <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinner">
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  isStreaming: { type: Boolean, default: false }
})

const emit = defineEmits(['send'])

const inputText = ref('')
const textareaRef = ref(null)

const canSend = computed(() =>
  inputText.value.trim().length > 0 && !props.isStreaming
)

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 120) + 'px'
}

function handleSend() {
  const text = inputText.value.trim()
  if (!canSend.value) return
  emit('send', text)
  inputText.value = ''
  const el = textareaRef.value
  if (el) {
    el.style.height = 'auto'
  }
}
</script>

<style scoped>
.chat-input-wrapper {
  padding: var(--space-md) var(--space-lg);
  background: var(--color-bg);
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
}

.chat-input-container {
  display: flex;
  align-items: flex-end;
  gap: var(--space-sm);
  background: var(--color-input-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-sm) var(--space-sm) var(--space-sm) var(--space-md);
  box-shadow: var(--shadow-sm);
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.chat-input-container:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  resize: none;
  font-family: var(--font-family);
  font-size: 15px;
  line-height: 1.5;
  color: var(--color-text);
  background: transparent;
  padding: 6px 0;
  max-height: 120px;
}

.chat-input::placeholder {
  color: #9CA3AF;
}

.chat-input:disabled {
  cursor: not-allowed;
}

.send-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.send-btn:hover:not(.disabled) {
  background: var(--color-primary-dark);
  transform: scale(1.05);
}

.send-btn:active:not(.disabled) {
  transform: scale(0.95);
}

.send-btn.disabled {
  background: #D1D5DB;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1.5s linear infinite;
}
</style>
```

**QA:** Verify input: typing enables send button, Enter sends, Shift+Enter newline, disabled when streaming.

---

### Task 9: MessageBubble

**Files:**
- Create: `frontend/src/components/MessageBubble.vue`

- [ ] **Step 1: Create MessageBubble.vue with attraction cards and typing cursor**

```vue
<template>
  <div class="message-wrapper" :class="message.role">
    <div class="message-bubble fade-in-up">
      <div class="message-content">
        <span>{{ message.content }}</span>
        <span v-if="message.isStreaming" class="typing-cursor">▊</span>
      </div>

      <div
        v-if="message.role === 'assistant' && message.sources && message.sources.length > 0"
        class="message-sources"
      >
        <p class="sources-header">📌 参考景点 ({{ message.sources.length }})</p>
        <div class="sources-grid">
          <AttractionCard
            v-for="(source, idx) in message.sources"
            :key="idx"
            :attraction="source"
          />
        </div>
      </div>
    </div>

    <span class="message-time">{{ formatTime(message.timestamp) }}</span>
  </div>
</template>

<script setup>
import AttractionCard from './AttractionCard.vue'

defineProps({
  message: {
    type: Object,
    required: true,
    validator: (obj) => obj.role && obj.content !== undefined
  }
})

function formatTime(iso) {
  const d = new Date(iso)
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
.message-wrapper {
  display: flex;
  flex-direction: column;
  max-width: 75%;
  margin-bottom: var(--space-lg);
}

.message-wrapper.user {
  align-self: flex-end;
  align-items: flex-end;
}

.message-wrapper.assistant {
  align-self: flex-start;
  align-items: flex-start;
}

.message-bubble {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-lg);
  font-size: 15px;
  line-height: 1.7;
  word-break: break-word;
  white-space: pre-wrap;
  min-width: 0;
}

.user .message-bubble {
  background: var(--color-user-bubble);
  color: var(--color-user-text);
  border-bottom-right-radius: var(--radius-sm);
}

.assistant .message-bubble {
  background: var(--color-ai-bubble);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.message-content {
  position: relative;
}

.typing-cursor {
  display: inline;
  color: var(--color-primary);
  font-weight: bold;
  animation: blink 1s step-end infinite;
}

.message-time {
  font-size: 11px;
  color: var(--color-text-secondary);
  margin-top: 4px;
  padding: 0 4px;
}

.message-sources {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border);
}

.sources-header {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-sm);
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-sm);
}
</style>
```

**QA:** Render with sample user/assistant messages, verify bubble styles and attraction cards.

---

### Task 10: ChatArea

**Files:**
- Create: `frontend/src/components/ChatArea.vue`

- [ ] **Step 1: Create ChatArea.vue**

```vue
<template>
  <main class="chat-area">
    <!-- Welcome state -->
    <div v-if="!store.currentConversation || store.messages.length === 0" class="welcome">
      <div class="welcome-icon">🌍</div>
      <h2 class="welcome-title">旅行攻略助手</h2>
      <p class="welcome-subtitle">问我任何旅行问题，我会为你推荐最佳景点和行程</p>
      <div class="quick-prompts">
        <button
          v-for="prompt in quickPrompts"
          :key="prompt"
          class="prompt-btn"
          @click="handleQuickPrompt(prompt)"
        >
          {{ prompt }}
        </button>
      </div>
    </div>

    <!-- Messages -->
    <div v-else class="messages-container" ref="messagesRef">
      <MessageBubble
        v-for="msg in store.messages"
        :key="msg.id"
        :message="msg"
      />
    </div>

    <!-- Input -->
    <ChatInput :is-streaming="store.isStreaming" @send="handleSend" />
  </main>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '../stores/chat'
import { sendMessage, checkHealth } from '../api/chat'
import MessageBubble from './MessageBubble.vue'
import ChatInput from './ChatInput.vue'

const store = useChatStore()
const messagesRef = ref(null)

const quickPrompts = [
  '北京三日游推荐',
  '上海有什么必吃美食？',
  '杭州春季赏花路线'
]

async function handleSend(text) {
  if (store.isStreaming) return

  // Ensure a conversation exists
  if (!store.currentConversation) {
    store.newConversation()
  }

  // Add user message
  store.addMessage('user', text)

  // Add placeholder assistant message
  store.addMessage('assistant', '')
  store.isStreaming = true

  await nextTick()
  scrollToBottom()

  await sendMessage(text, store.currentId, {
    onToken(token) {
      store.appendToken(token)
      scrollToBottom()
    },
    onDone(sources) {
      store.finishStreaming(sources)
    },
    onError(errMsg) {
      store.finishStreaming([])
      // Replace streaming placeholder with error
      const conv = store.currentConversation
      if (conv && conv.messages.length > 0) {
        const last = conv.messages[conv.messages.length - 1]
        if (last.role === 'assistant') {
          last.content = `❌ ${errMsg}`
        }
      }
    }
  })
}

function handleQuickPrompt(text) {
  handleSend(text)
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

// Auto-scroll when messages change
watch(() => store.messages.length, () => {
  scrollToBottom()
})
</script>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--color-bg);
}

.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: var(--space-2xl);
}

.welcome-icon {
  font-size: 64px;
  margin-bottom: var(--space-lg);
  animation: fadeInUp 0.6s ease-out;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-sm);
}

.welcome-subtitle {
  font-size: 16px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-xl);
  max-width: 400px;
}

.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-sm);
  justify-content: center;
}

.prompt-btn {
  padding: 8px 20px;
  background: var(--color-ai-bubble);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  font-size: 14px;
  color: var(--color-text);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: var(--font-family);
}

.prompt-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-lg);
  display: flex;
  flex-direction: column;
}
</style>
```

**QA:** Click "新对话" in sidebar, verify welcome screen. Type a question, verify streaming response.

---

## Wave 3: Assembly

### Task 11: App.vue

**Files:**
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Create App.vue root layout**

```vue
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
  // Initial health check
  const result = await checkHealth()
  store.apiOnline = result.online

  // Poll every 30s
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
```

---

### Task 12: main.js

**Files:**
- Create: `frontend/src/main.js`

- [ ] **Step 1: Create main.js entry point**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import './styles/main.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')
```

---

## Wave 4: Verification

### Task 13: Integration Verification

- [ ] **Step 1: Start backend server**

```bash
cd /Users/chenjimin/travel-agent-bot
source venv/bin/activate
uvicorn app.server:app --reload --port 8000
```

- [ ] **Step 2: Start frontend dev server (separate terminal)**

```bash
cd /Users/chenjimin/travel-agent-bot/frontend
npm run dev
```

- [ ] **Step 3: Open browser at http://localhost:5173**

Verify:
1. NavBar shows "旅行攻略助手" logo and green "在线" badge
2. Sidebar shows "对话历史" with "新对话" button
3. Welcome screen shows with 3 quick prompts
4. Click a quick prompt → message sends, streaming typing appears
5. AI response appears with typing animation
6. If backend returns sources, attraction cards display
7. Create multiple conversations, switch between them
8. Close and reopen browser → conversations persist
9. Stop backend → status badge turns red "离线"
10. Restart backend → status badge turns green again

- [ ] **Step 4: Fix any issues found during manual testing**
