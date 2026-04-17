import { createContext, useContext, useState } from 'react'

const initialSession = {
  body_part: null,       // "knee"
  user_text: null,       // 증상 자유입력
  session_id: null,      // EP1 응답값
  height_cm: null,       // nullable
  weight_kg: null,       // nullable
  model_id: null,        // EP2 응답값
  glb_url: null,         // EP2 응답값
  taping_options: [],    // EP3 응답값 (배열)
  selected_option: null, // 유저가 선택한 옵션
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
