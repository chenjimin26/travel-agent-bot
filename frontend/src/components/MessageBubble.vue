<template>
  <div class="message-wrapper" :class="message.role">
    <div class="message-bubble fade-in-up">
      <div class="message-content">
        <div class="markdown-body" v-html="renderedContent"></div>
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
import { computed } from 'vue'
import { marked } from 'marked'
import AttractionCard from './AttractionCard.vue'

const props = defineProps({
  message: {
    type: Object,
    required: true,
    validator: (obj) => obj.role && obj.content !== undefined
  }
})

function formatContent(text) {
  if (!text) return ''
  let formatted = text
    // Fix: add newline before list markers that are missing it
    .replace(/(?<!\n)([*-]\s)/g, '\n$1')
    // Fix: add newline before ### headings
    .replace(/(?<!\n)(#{1,4}\s)/g, '\n$1')
    // Fix: ensure single * is treated as list (LLM sometimes uses * without \n)
    .replace(/(?<!\n)(\*)([^\s*])/g, '\n* $2')
    // Collapse excessive blank lines
    .replace(/\n{3,}/g, '\n\n')
  return formatted
}

const renderedContent = computed(() => {
  const formatted = formatContent(props.message.content || '')
  return marked.parse(formatted)
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
  min-width: 0;
}

.user .message-bubble {
  background: var(--color-user-bubble);
  color: var(--color-user-text);
  border-bottom-right-radius: var(--radius-sm);
  white-space: pre-wrap;
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

.markdown-body :deep(h1) {
  font-size: 1.35em;
  font-weight: 700;
  margin: 0.6em 0 0.3em;
  line-height: 1.4;
}

.markdown-body :deep(h2) {
  font-size: 1.2em;
  font-weight: 700;
  margin: 0.6em 0 0.3em;
  line-height: 1.4;
}

.markdown-body :deep(h3) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 0.5em 0 0.2em;
}

.markdown-body :deep(p) {
  margin: 0.4em 0;
}

.markdown-body :deep(p:first-child) {
  margin-top: 0;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.3em 0;
  padding-left: 1.5em;
}

.markdown-body :deep(li) {
  margin: 0.15em 0;
}

.markdown-body :deep(strong),
.markdown-body :deep(b) {
  font-weight: 700;
  color: var(--color-primary-dark);
}

.markdown-body :deep(code) {
  background: var(--color-primary-light);
  padding: 0.15em 0.4em;
  border-radius: 3px;
  font-size: 0.9em;
  font-family: "JetBrains Mono", "Fira Code", monospace;
}

.markdown-body :deep(pre) {
  background: #1E293B;
  color: #E2E8F0;
  padding: 0.8em 1em;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 0.5em 0;
  font-size: 0.85em;
  line-height: 1.5;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  color: inherit;
}

.markdown-body :deep(blockquote) {
  border-left: 3px solid var(--color-primary);
  padding: 0.3em 0.8em;
  margin: 0.4em 0;
  color: var(--color-text-secondary);
  background: var(--color-primary-light);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}

.markdown-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 0.8em 0;
}

.markdown-body :deep(em),
.markdown-body :deep(i) {
  font-style: italic;
}

.markdown-body :deep(br + br) {
  display: none;
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