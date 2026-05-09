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

  if (!store.currentConversation) {
    store.newConversation()
  }

  store.addMessage('user', text)
  store.isStreaming = true

  try {
    const data = await sendMessage(text, store.currentId, store.queryMode)
    store.addMessage('assistant', data.message, data.sources || [])
  } catch (err) {
    store.addMessage('assistant', `❌ ${err.message || '网络错误，请重试'}`, [])
  } finally {
    store.isStreaming = false
    scrollToBottom()
  }
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