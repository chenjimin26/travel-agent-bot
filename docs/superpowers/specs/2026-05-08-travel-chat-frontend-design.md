# Travel Chat Frontend Design Spec

**Date**: 2026-05-08  
**Status**: Draft → Review

---

## 1. Overview

Build a **旅行攻略助手** (Travel Assistant) frontend for the existing Travel RAG Chatbot API. The frontend will be a single-page web application using Vue 3 + Vite, connected to the FastAPI backend at `/api/v1/chat` and `/health`.

### Core Features
- Streamed AI responses with typing animation effect
- Conversation history sidebar (persisted in localStorage)
- Attraction cards displayed inline with AI responses
- Beautiful travel-themed UI with Chinese font support

---

## 2. Architecture

```
frontend/                          ← New directory alongside app/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js                    ← Vue app entry
│   ├── App.vue                    ← Root layout
│   ├── api/
│   │   └── chat.js               ← API client (SSE streaming, health check)
│   ├── components/
│   │   ├── NavBar.vue            ← Top navigation bar
│   │   ├── Sidebar.vue           ← Conversation history panel
│   │   ├── ChatArea.vue          ← Main chat display area
│   │   ├── MessageBubble.vue     ← Single message (user or AI)
│   │   ├── AttractionCard.vue    ← Attraction info card
│   │   ├── ChatInput.vue         ← Input box with send button
│   │   └── StatusBadge.vue       ← API status indicator
│   ├── stores/
│   │   └── chat.js               ← Pinia store (messages, conversations, streaming)
│   └── styles/
│       └── main.css              ← Global styles, CSS variables, animations
└── public/
    └── vite.svg
```

### Data Flow

```
User Input → ChatInput.vue → Pinia store (add message)
     ↓
api/chat.js → POST /api/v1/chat (SSE streaming)
     ↓
StreamingReader → Pinia store (append tokens) → MessageBubble (reactive typing)
     ↓
On stream complete → Parse sources → AttractionCard components
```

---

## 3. Component Details

### 3.1 Layout (App.vue)

Three-column layout:
- **Top NavBar** (fixed, 64px high): logo, API status badge, settings icon
- **Left Sidebar** (280px): conversation history list + new chat button
- **Main ChatArea** (flex: 1): scrollable message list + fixed ChatInput at bottom

### 3.2 NavBar.vue

- Logo text "旅行攻略助手" with a globe/travel icon
- StatusBadge component showing green ● "在线" or red ● "离线"
- Health check polls `/health` every 30 seconds

### 3.3 Sidebar.vue

- Header: "对话历史"
- "新对话" button (prominent, theme color)
- Conversation list items showing: first message preview (truncated 30 chars), relative date
- Active conversation highlighted with left border accent
- Click to switch conversation, hover shows delete icon

### 3.4 ChatArea.vue

- Scrollable container with `overflow-y: auto`, auto-scrolls to bottom on new messages
- Welcome state: centered "旅行攻略助手" with subtitle "问我任何旅行问题..." and 3 suggestion quick-start buttons
- Empty state: "开始一段新的对话吧" placeholder

### 3.5 MessageBubble.vue

User messages (right-aligned):
- Theme-color background (`#10B981`), white text
- `border-radius: 16px 16px 4px 16px`
- Timestamp below (small, gray)

AI messages (left-aligned):
- White background with light border
- `border-radius: 16px 16px 16px 4px`
- Streaming text (characters appear one by one, 30ms interval)
- Red cursor "▊" blinks while streaming
- Source card grid below message text (if sources present)
- "参考 X 个景点" summary line

### 3.6 AttractionCard.vue

Card displays:
- Icon/gradient header with attraction name
- Location line with pin emoji
- Ticket price with ticket emoji
- Opening hours with clock emoji
- Best season with flower emoji
- Tags as colored badges
- Description text (2-line clamp with expand)

Visual: white card, `box-shadow: 0 1px 3px rgba(0,0,0,0.1)`, hover lifts with `translateY(-4px)` transition

### 3.7 ChatInput.vue

- Rounded textarea with shadow
- Auto-resize (up to 4 lines)
- Send button (circle, theme color, arrow icon)
- Placeholder: "输入你的旅行问题..."
- Enter to send, Shift+Enter for newline
- Disabled state when streaming (gray button, cursor not-allowed)

### 3.8 StatusBadge.vue

- Green dot + "在线" when API ping succeeds
- Red dot + "离线" when ping fails
- Animated pulse on green dot

---

## 4. Visual Design System

### Colors (CSS Variables)

```css
--color-primary: #10B981;        /* Emerald-500 - theme */
--color-primary-dark: #059669;   /* Emerald-600 - hover */
--color-bg: #F8FAFC;             /* Slate-50 - page background */
--color-sidebar: #1E293B;        /* Slate-800 - sidebar */
--color-text: #1F2937;           /* Gray-800 - primary text */
--color-text-secondary: #6B7280; /* Gray-500 - secondary text */
--color-border: #E5E7EB;         /* Gray-200 - borders */
--color-error: #EF4444;           /* Red-500 */
--color-success: #22C55E;        /* Green-500 */
--color-user-bubble: #10B981;
--color-ai-bubble: #FFFFFF;
```

### Typography

- Font family: `"PingFang SC", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`
- Base size: 16px
- Line height: 1.6

### Spacing Scale

- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, 2xl: 48px

### Animations

- Message enter: `fadeInUp` 0.3s ease-out
- Typing cursor: blink 1s step-end infinite
- Button hover: `translateY(-2px)` + shadow increase
- Card hover: `translateY(-4px)` + shadow increase
- Status dot: pulse 2s infinite

---

## 5. API Integration

### 5.1 Health Check
```
GET /health → { "status": "ok", "attractions_count": 123 }
```
Used for NavBar status indicator.

### 5.2 Chat (SSE Streaming)
```
POST /api/v1/chat
Body: { "message": "北京有什么好玩的?", "session_id": "optional" }

Response: text/event-stream
data: token1
data: token2
...
data: [DONE]
```

Frontend uses `fetch()` with `ReadableStream` reader to process SSE chunks. Each token is appended to the current AI message in Pinia store.

### 5.3 Error Handling
- Network error: show "网络连接失败，请检查网络" toast
- 4xx errors: show API error message from response body
- 5xx errors: show "服务器繁忙，请稍后重试" toast
- Retry timeout: 10 seconds for streaming timeout

---

## 6. State Management (Pinia)

### useChatStore

```javascript
{
  // State
  conversations: Map<string, Conversation>,  // keyed by UUID
  currentConversationId: string | null,
  isStreaming: boolean,
  apiOnline: boolean,

  // Conversation shape
  Conversation: {
    id: string,
    title: string,          // first user message, truncated
    messages: Message[],
    createdAt: Date,
    updatedAt: Date,
  },

  // Message shape
  Message: {
    id: string,
    role: 'user' | 'assistant',
    content: string,
    sources: AttractionSource[],  // only on assistant messages
    timestamp: Date,
    isStreaming: boolean,         // true while tokens arriving
  },

  // AttractionSource shape
  AttractionSource: {
    name: string,
    city: string,
    ticket: string,
    open_time: string,
    best_season: string,
    tags: string[],
    description: string,
  }
}
```

### Persistence
- Conversations saved to `localStorage` under key `travel-chat-conversations`
- Maximum 50 conversations stored
- Oldest conversations pruned when limit exceeded
- Loaded on app startup

---

## 7. Build & Dev Setup

### package.json dependencies
```json
{
  "dependencies": {
    "vue": "^3.4",
    "pinia": "^2.1",
    "@vueuse/core": "^10.7"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0",
    "vite": "^5.0"
  }
}
```

### vite.config.js
```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

### Running
```bash
cd frontend && npm install && npm run dev
```

---

## 8. Responsive Design

| Breakpoint | Layout |
|---|---|
| ≥1024px | Full sidebar + chat area |
| 768-1023px | Collapsible sidebar (hamburger toggle) |
| <768px | Full-screen chat, no sidebar, hamburger menu overlay |

---

## 9. Success Criteria

1. User can type a travel question and receive a streamed AI response with typing animation
2. AI responses display attraction cards with all metadata fields
3. Conversation history persists across page refreshes
4. Multiple conversations can be created and switched between
5. Health status indicator shows green/red based on API availability
6. Frontend runs on `npm run dev` and proxies API calls to the FastAPI backend
7. Works on desktop and mobile screen sizes

---

## 10. Out of Scope (for this iteration)

- User authentication / login
- Map visualization of attractions
- Image display for attractions
- Voice input
- Dark mode toggle
- Markdown rendering (plain text only)
