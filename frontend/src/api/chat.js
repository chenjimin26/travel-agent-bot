const API_BASE = '/api/v1'

export async function checkHealth() {
  try {
    const res = await fetch('/health', {
      signal: AbortSignal.timeout(5000)
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    return { online: true, ...data }
  } catch {
    return { online: false }
  }
}

export async function sendMessage(message, sessionId = null, mode = 'fast') {
  const body = { message, mode }
  if (sessionId) body.session_id = sessionId

  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  })

  if (!response.ok) {
    const errText = await response.text().catch(() => 'Unknown error')
    throw new Error(errText || `HTTP ${response.status}`)
  }

  return await response.json()
}
