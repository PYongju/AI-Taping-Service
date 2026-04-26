// const BASE_URL = import.meta.env.VITE_API_BASE_URL;
// const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";
const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";

// ─── Mock 응답 ────────────────────────────────────────────────
const MOCK_RESPONSES = {
  analyzeSymptoms: () => ({
    session_id: "mock-session-001",
  }),
  matchBody: () => ({
    model_id: "mock-model-A",
  }),
  getTapingRecommend: () => ({
    session_id: "mock-session-001",
    status: "TAPE_GENERATED",
    model_url: "",
    video_url: "",
    registry_key: "KNEE_BASIC_001",
    options: [
      {
        title: "기본 무릎 고정 테이핑",
        registry_key: "KNEE_BASIC_001",
        taping_id: "A",
        name: "IT band 이완 테이핑",
        tape_type: "Y-strip",
        stretch_pct: 15,
        why: "러닝 후 외측 긴장에 가장 일반적인 예방 테이핑이에요.",
        coach:
          "💡 테이핑 전 부위를 깨끗이 닦고, 털이 있다면 면도 후 붙여주세요.",
        steps: [],
        step_glb_urls: [],
        video_url: "",
        disclaimer:
          "이 서비스는 예방을 위한 가이드예요. 지속되는 증상은 전문가에게 확인해보세요.",
      },
      {
        title: "무릎 안정화 테이핑",
        registry_key: "KNEE_STABLE_002",
        taping_id: "B",
        name: "무릎 안정화 테이핑",
        tape_type: "I-strip",
        stretch_pct: 25,
        why: "무릎 전반적 안정감 보강에 도움이 될 수 있어요.",
        coach: "💡 stretch 25%는 조금 당긴 상태로 붙이는 거예요.",
        steps: [],
        step_glb_urls: [],
        video_url: "",
        disclaimer:
          "이 서비스는 예방을 위한 가이드예요. 지속되는 증상은 전문가에게 확인해보세요.",
      },
    ],
  }),
  saveSession: () => ({ ok: true }),
};

function mockDelay(fn) {
  return new Promise((resolve) => setTimeout(() => resolve(fn()), 800));
}

// ─── EP1: 증상 분석 ──────────────────────────────────────────
/**
 * @param {{ body_part: string, situation: string, symptom_type: string, raw_text: string }} params
 * @returns {Promise<{ session_id: string }>}
 */
export async function analyzeSymptoms({
  body_part,
  situation,
  symptom_type,
  raw_text,
  height_cm,
  weight_kg,
  gender,
}) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.analyzeSymptoms);

  const res = await fetch(`${BASE_URL}/api/v1/symptoms/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    // 🌟 수정됨: 백엔드 모델에 맞춰 raw_text 및 신체 정보 전달
    body: JSON.stringify({
      body_part,
      situation,
      symptom_type,
      raw_text,
      height_cm,
      weight_kg,
      gender,
    }),
  });
  if (!res.ok) throw new Error(`EP1 ${res.status}`);
  return res.json();
}

// ─── EP2: 신체 매칭 ──────────────────────────────────────────
/**
 * @param {FormData} formData  image, session_id, gender(nullable)
 * @returns {Promise<{ session_id?: string, model_id?: string }>}
 */
export async function matchBody(formData) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.matchBody);

  const res = await fetch(`${BASE_URL}/api/v1/body/match`, {
    method: "POST",
    body: formData, // multipart/form-data — Content-Type 헤더 설정 안 함 (browser 자동)
  });
  if (!res.ok) throw new Error(`EP2 ${res.status}`);
  return res.json();
}

// ─── EP3: 테이핑 추천 ─────────────────────────────────────────
/**
 * @param {{ session_id: string, model_id: string|null, privacy_opt_out?: boolean }} params
 * @returns {Promise<{ options: TapingOption[] }>}
 */
export async function getTapingRecommend({
  session_id,
  model_id,
  privacy_opt_out,
}) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.getTapingRecommend);

  const res = await fetch(`${BASE_URL}/api/v1/taping/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id, model_id, privacy_opt_out }),
  });
  if (!res.ok) throw new Error(`EP3 ${res.status}`);
  return res.json();
}

// ─── EP4: 세션 저장 ──────────────────────────────────────────
/**
 * @param {{ session_id: string, taping_id: string }} params
 * @returns {Promise<{ ok: boolean }>}
 */
export async function saveSession({ session_id, taping_id }) {
  if (USE_MOCK) return mockDelay(MOCK_RESPONSES.saveSession);

  const res = await fetch(`${BASE_URL}/api/v1/session/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id, taping_id }),
  });
  if (!res.ok) throw new Error(`EP4 ${res.status}`);
  return res.json();
}
