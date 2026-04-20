const BASE_URL = import.meta.env.VITE_API_BASE_URL
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// ─── Mock 응답 ────────────────────────────────────────────────
const MOCK_RESPONSES = {
  analyzeSymptoms: () => ({
    session_id: 'mock-session-001',
  }),
  matchBody: () => ({
    model_id: 'mock-model-A',
  }),
  getTapingRecommend: () => ({
    taping_options: [
      {
        id: 'A',
        name: 'IT band 이완 테이핑',
        tape: 'Y-strip',
        stretch: 15,
        why: '러닝 후 외측 긴장에 가장 일반적인 예방 테이핑이에요.',
        step_glb_urls: [],
        video_url: '',
        disclaimer: '이 서비스는 예방을 위한 가이드예요. 지속되는 증상은 전문가에게 확인해보세요.',
      },
      {
        id: 'B',
        name: '무릎 안정화 테이핑',
        tape: 'I-strip',
        stretch: 25,
        why: '무릎 전반적 안정감 보강에 도움이 될 수 있어요.',
        step_glb_urls: [],
        video_url: '',
        disclaimer: '이 서비스는 예방을 위한 가이드예요. 지속되는 증상은 전문가에게 확인해보세요.',
      },
    ],
  }),
  saveSession: () => ({ ok: true }),
}

function mockDelay(fn) {
  return new Promise((resolve) => setTimeout(() => resolve(fn()), 800))
}

// ─── EP1: 증상 분석 ──────────────────────────────────────────
/**
 * @param {{ body_part: string, situation: string, symptom_type: string, user_text: string|null }} params
 * @returns {Promise<{ session_id: string }>}
 */
export async function analyzeSymptoms({ body_part, situation, symptom_type, user_text }) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.analyzeSymptoms)

  const res = await fetch(`${BASE_URL}/api/symptoms/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ body_part, situation, symptom_type, user_text }),
  })
  if (!res.ok) throw new Error(`EP1 ${res.status}`)
  return res.json()
}

// ─── EP2: 신체 매칭 ──────────────────────────────────────────
/**
 * @param {FormData} formData  image, session_id, height_cm, weight_kg, gender(nullable)
 * @returns {Promise<{ model_id: string }>}
 */
export async function matchBody(formData) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.matchBody)

  const res = await fetch(`${BASE_URL}/api/body/match`, {
    method: 'POST',
    body: formData, // multipart/form-data — Content-Type 헤더 설정 안 함 (browser 자동)
  })
  if (!res.ok) throw new Error(`EP2 ${res.status}`)
  return res.json()
}

// ─── EP3: 테이핑 추천 ─────────────────────────────────────────
/**
 * @param {{ session_id: string, model_id: string|null }} params
 * @returns {Promise<{ taping_options: TapingOption[] }>}
 */
export async function getTapingRecommend({ session_id, model_id }) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.getTapingRecommend)

  const res = await fetch(`${BASE_URL}/api/taping/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, model_id }),
  })
  if (!res.ok) throw new Error(`EP3 ${res.status}`)
  return res.json()
}

// ─── EP4: 세션 저장 ──────────────────────────────────────────
/**
 * @param {{ session_id: string, taping_id: string }} params
 * @returns {Promise<{ ok: boolean }>}
 */
export async function saveSession({ session_id, taping_id }) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.saveSession)

  const res = await fetch(`${BASE_URL}/api/session/save`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, taping_id }),
  })
  if (!res.ok) throw new Error(`EP4 ${res.status}`)
  return res.json()
}
