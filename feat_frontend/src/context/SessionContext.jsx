import { createContext, useContext, useState } from 'react'

/**
 * @typedef {Object} TapingOption
 * @property {string} id
 * @property {string} name
 * @property {string} tape
 * @property {number} stretch
 * @property {string} why
 * @property {string[]} step_glb_urls
 * @property {string} video_url
 * @property {string} disclaimer
 */

const initialSession = {
  // Scene 1 inputs
  part: '무릎',
  situation: null,
  symptom: null,

  // Scene 2/3 inputs
  body_info_mode: null, // null | 'full'
  height: null,
  weight: null,
  gender: null,
  photoUploaded: false,

  // EP1 response
  session_id: null,

  // EP2 response
  model_id: null,

  // EP3 response — TapingOption[]
  taping_options: [],

  // Scene 5 선택 인덱스 (number | null)
  selected_option: null,
}

const SessionContext = createContext(null)

export function SessionProvider({ children }) {
  const [session, setSession] = useState(initialSession)

  function updateSession(partial) {
    setSession((prev) => ({ ...prev, ...partial }))
  }

  function resetSession() {
    setSession(initialSession)
  }

  return (
    <SessionContext.Provider value={{ session, updateSession, resetSession }}>
      {children}
    </SessionContext.Provider>
  )
}

export function useSession() {
  const ctx = useContext(SessionContext)
  if (!ctx) throw new Error('useSession must be used within SessionProvider')
  return ctx
}
