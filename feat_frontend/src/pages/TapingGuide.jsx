import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { MessageCircle, AlertTriangle } from 'lucide-react'
import ChatbotSheet from '../components/ChatbotSheet'
import styles from './TapingGuide.module.css'

const STEP_TITLES = {
  1: '고정 테이프 — 시작점을 잡아줍니다',
  2: '지지 테이프 — 무릎 양쪽 인대를 받쳐줍니다',
  3: '8자 테이프 — 무릎이 꺾이는 걸 막아줍니다',
  4: '무릎 테이프 — 슬개골을 고정합니다',
  5: '마무리 테이프 — 전체를 단단히 잡아줍니다',
}

export default function TapingGuide() {
  const { step } = useParams()
  const navigate = useNavigate()
  const stepNum = Number(step)
  const [chatOpen, setChatOpen] = useState(false)

  function handlePrev() {
    if (stepNum === 1) navigate('/result-3d')
    else navigate(`/guide/${stepNum - 1}`)
  }

  function handleNext() {
    if (stepNum === 5) navigate('/complete')
    else navigate(`/guide/${stepNum + 1}`)
  }

  return (
    <div className={styles.container}>
      <div className={styles.progressHeader}>
        <span className={styles.progressLabel}>{stepNum} / 5 단계</span>
        <div className={styles.progressBar}>
          <div
            className={styles.progressFill}
            style={{ width: `${(stepNum / 5) * 100}%` }}
          />
        </div>
      </div>

      <div className={styles.viewer}>
        <span className={styles.viewerText}>3D 뷰어 (연결 예정)</span>
      </div>

      <h2 className={styles.stepTitle}>{STEP_TITLES[stepNum]}</h2>

      <p className={styles.warning}>
        <AlertTriangle size={14} strokeWidth={2} style={{ flexShrink: 0, marginTop: 1 }} />
        무릎이 저리거나 피부색이 하얗게 변하면 풀고 다시 하세요
      </p>

      <div className={styles.navRow}>
        <button className={styles.btnSecondary} onClick={handlePrev}>
          이전
        </button>
        <button className={styles.btnPrimary} onClick={handleNext}>
          {stepNum === 5 ? '완료' : '다음'}
        </button>
      </div>

      <button className={styles.fab} onClick={() => setChatOpen(true)}>
        <MessageCircle size={22} strokeWidth={2} />
      </button>

      <ChatbotSheet isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  )
}
