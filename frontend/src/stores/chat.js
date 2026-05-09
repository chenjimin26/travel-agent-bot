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
  const queryMode = ref('fast')

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
    let conv = currentConversation.value
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
      isStreaming: false
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
    queryMode,
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