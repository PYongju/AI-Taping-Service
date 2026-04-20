import { createContext, useContext, useState } from 'react'

const initialSession = {
  part: '무릎',
  situation: null,
  symptom: null,
  height: null,
  weight: null,
  gender: null,
  photoUploaded: false,
  session_id: null,
  model_id: null,
  glb_url: null,
  taping_options: [],
  selected_option: 'A',
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
