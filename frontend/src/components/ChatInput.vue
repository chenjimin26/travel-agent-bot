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