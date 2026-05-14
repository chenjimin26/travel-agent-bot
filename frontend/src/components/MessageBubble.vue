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
  const lines = text.split('\n')
  const result = []
  let inBlockquote = false
  for (const line of lines) {
    const trimmed = line.trim()
    // 表格行跳过
    if (trimmed.startsWith('|') && trimmed.includes('|', 1)) {
      inBlockquote = false; result.push(line); continue
    }
    // 空行：结束引用块
    if (!trimmed) {
      inBlockquote = false; result.push(line); continue
    }
    // 标题：结束引用块
    if (/^#{1,4}\s/.test(trimmed)) {
      inBlockquote = false; result.push(line); continue
    }
    // 进入或继续引用块
    if (trimmed.startsWith('>')) {
      inBlockquote = true; result.push(line); continue
    }
    // 引用块内的后续行，自动补 >
    if (inBlockquote) {
      result.push('> ' + trimmed); continue
    }
    // 普通行
    let l = line
      .replace(/([*-]\s)/g, '\n$1')
      .replace(/(#{1,4}\s)/g, '\n$1')
      .replace(/(?<!\*)\*(?!\*)(?=[：，。、！？；])/g, '')
    result.push(l)
  }
  let formatted = result.join('\n')
    // 修复不配对的星号
    .replace(/\*{3,}/g, '**')
    .replace(/\*\*([^*]+)\*(?!\*)/g, '**$1')
    .replace(/\n{3,}/g, '\n\n')
  return formatted
}

const renderedContent = computed(() => {
  const formatted = formatContent(props.message.content || '')
  return marked.parse(formatted, { gfm: true, breaks: true })
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
  padding: var(--space-md) var(--space-lg);
  border-radius: var(--radius-lg);
  font-size: 15px;
  line-height: 1.9;
  word-break: normal;
  overflow-wrap: break-word;
  min-width: 0;
  overflow: hidden;
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
  overflow: hidden;
}

.markdown-body {
  word-break: normal;
  overflow-wrap: break-word;
}

.markdown-body :deep(p) {
  margin: 0.6em 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  width: 100%;
  max-width: 100%;
  border-collapse: collapse;
  margin: 0.5em 0;
  font-size: 0.85em;
  table-layout: auto;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 4px 8px;
  border: 1px solid var(--color-border);
  text-align: left;
  white-space: normal;
  word-break: keep-all;
  overflow-wrap: break-word;
}

.markdown-body :deep(em),
.markdown-body :deep(i) {
  font-style: italic;
}

.markdown-body :deep(br + br) {
  display: none;
}

.markdown-body :deep(blockquote) {
  margin: 0.6em 0;
  padding: 0.5em 1em;
  border-left: 4px solid var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 0.93em;
  color: var(--color-text-secondary);
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

/* 段落间距和提示块样式 */
.markdown-body :deep(p) { margin: 0.6em 0; }
.markdown-body :deep(h3) { margin: 1em 0 0.3em; }
.markdown-body :deep(h4) { margin: 0.8em 0 0.2em; }
.markdown-body :deep(blockquote) { margin: 0.6em 0; padding: 0.5em 1em; border-left: 4px solid var(--color-primary); background: var(--color-primary-light); border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: 0.93em; color: var(--color-text-secondary); }
</style>