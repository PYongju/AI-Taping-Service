import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import { getTapingRecommend } from '../api/index'
import styles from './Analyzing.module.css'

const STEPS = [
  '관절 위치 파악 중...',
  '체형 수치 계산 중...',
  '유사 모델 탐색 중...',
  '테이핑 옵션 생성 중...',
]

const MOCK_OPTIONS = [
  { id: 'A', name: 'IT band 이완 테이핑', tape_type: 'elastic', stretch_pct: 25, why: '외측 무릎 긴장 완화에 효과적' },
  { id: 'B', name: '슬개골 안정 테이핑', tape_type: 'non-elastic', stretch_pct: 0, why: '슬개골 정렬 보조' },
  { id: 'C', name: 'VMO 활성화 테이핑', tape_type: 'elastic', stretch_pct: 15, why: '내측 근육 활성화' },
]

// 애니메이션 최소 지속 시간 (ms)
const MIN_DURATION = (STEPS.length - 1) * 1000 + 800

export default function Analyzing() {
  const navigate = useNavigate()
  const { session, updateSession } = useSession()
  const [stepIndex, setStepIndex] = useState(0)
  const [error, setError] = useState(null)
  const [retryKey, setRetryKey] = useState(0)

  // 순차 텍스트 애니메이션
  useEffect(() => {
    setStepIndex(0)
    const timers = STEPS.slice(1).map((_, i) =>
      setTimeout(() => setStepIndex(i + 1), (i + 1) * 1000)
    )
    return () => timers.forEach(clearTimeout)
  }, [retryKey])

  // API 호출
  useEffect(() => {
    let cancelled = false
    setError(null)

    async function run() {
      try {
        const optionsPromise = session.session_id
          ? getTapingRecommend(session.session_id).then((r) => r.taping_options)
          : Promise.resolve(MOCK_OPTIONS)

        const [options] = await Promise.all([
          optionsPromise,
          new Promise((r) => setTimeout(r, MIN_DURATION)),
        ])

        if (cancelled) return
        updateSession({ taping_options: options })
        navigate('/result-video')
      } catch {
        if (!cancelled) setError('분석에 실패했어요. 다시 시도해주세요.')
      }
    }

    run()
    return () => { cancelled = true }
  }, [retryKey]) // eslint-disable-line react-hooks/exhaustive-deps

  if (error) {
    return (
      <div className={styles.container}>
        <p className={styles.errorText}>{error}</p>
        <button
          className={styles.btnPrimary}
          onClick={() => setRetryKey((k) => k + 1)}
        >
          다시 시도
        </button>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.stepList}>
        {STEPS.map((s, i) => (
          <p key={i} className={i <= stepIndex ? styles.stepActive : styles.stepInactive}>
            {s}
          </p>
        ))}
      </div>
    </div>
  )
}
