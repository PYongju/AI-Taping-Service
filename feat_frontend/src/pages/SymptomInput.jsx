import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { analyzeSymptoms } from '../api/index'
import styles from './SymptomInput.module.css'

export default function SymptomInput() {
  const navigate = useNavigate()
  const { session, updateSession } = useSession()
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit() {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeSymptoms(session.body_part, text.trim())
      updateSession({ user_text: text.trim(), session_id: result.session_id })
      navigate('/body-info')
    } catch {
      setError('분석에 실패했어요. 다시 시도해주세요.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.bubble}>좀 더 자세히 알려주시겠어요?</div>
      <textarea
        className={styles.textarea}
        placeholder="예) 달리기 후 바깥쪽이 뻣뻣해요"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={5}
      />
      <p className={styles.hint}>
        AI가 증상을 분석해 가장 적합한 테이핑 방법을 찾을게요
      </p>
      {error && <p className={styles.error}>{error}</p>}
      <button
        className={styles.btnPrimary}
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
      >
        {loading ? '분석 중...' : '전송'}
      </button>
    </div>
  )
}
