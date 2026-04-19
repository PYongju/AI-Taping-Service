const BASE_URL = import.meta.env.VITE_API_BASE_URL

/**
 * EP1: 증상 분석
 * @param {string} body_part - 신체 부위 (예: "knee")
 * @param {string} user_text - 증상 자유입력
 * @returns {Promise<{ session_id: string }>}
 */
export async function analyzeSymptoms(body_part, user_text) {
  // TODO: implement
  // POST ${BASE_URL}/api/symptoms/analyze
  // body: { body_part, user_text }
  throw new Error('analyzeSymptoms is not implemented yet')
}

/**
 * EP2: 신체 매칭 (사진 업로드)
 * @param {FormData} formData - multipart form data (신장, 체중, 사진 포함)
 * @returns {Promise<{ model_id: string, glb_url: string }>}
 */
export async function matchBody(formData) {
  // TODO: implement
  // POST ${BASE_URL}/api/body/match
  // body: formData (multipart/form-data)
  throw new Error('matchBody is not implemented yet')
}

/**
 * EP3: 테이핑 추천
 * @param {string} session_id - analyzeSymptoms 응답값
 * @returns {Promise<{ taping_options: Array }>}
 */
export async function getTapingRecommend(session_id) {
  // TODO: implement
  // POST ${BASE_URL}/api/taping/recommend
  // body: { session_id }
  throw new Error('getTapingRecommend is not implemented yet')
}
