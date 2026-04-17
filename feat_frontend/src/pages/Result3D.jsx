import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'
import { useSession } from '../context/SessionContext'
import styles from './Result3D.module.css'

export default function Result3D() {
  const navigate = useNavigate()
  const { session, updateSession } = useSession()
  const options = session.taping_options ?? []
  const [selectedId, setSelectedId] = useState(
    session.selected_option?.id ?? options[0]?.id ?? null
  )

  const selected = options.find((o) => o.id === selectedId) ?? options[0] ?? null

  if (options.length === 0) {
    return (
      <div className={styles.container}>
        <p style={{ color: 'var(--color-caption)' }}>분석 데이터가 없습니다.</p>
        <button className={styles.btnPrimary} onClick={() => navigate('/analyzing')}>
          다시 분석하기
        </button>
      </div>
    )
  }

  function handleStart() {
    updateSession({ selected_option: selected })
    navigate('/guide/1')
  }

  return (
    <div className={styles.container}>
      <div className={styles.tabRow}>
        {options.map((opt) => (
          <button
            key={opt.id}
            className={selectedId === opt.id ? styles.tabActive : styles.tab}
            onClick={() => setSelectedId(opt.id)}
          >
            {opt.id}
          </button>
        ))}
      </div>

      <div className={styles.viewer}>
        <span className={styles.viewerText}>
          3D 모델 로딩 중 (호진 에셋 연결 예정)
        </span>
      </div>

      <p className={styles.coachText}>{selected?.why}</p>

      <p className={styles.disclaimer}>
        <AlertTriangle size={14} strokeWidth={2} style={{ flexShrink: 0, marginTop: 1 }} />
        이 가이드는 예방적 셀프케어 목적이며 의료 진단이 아닙니다
      </p>

      <button className={styles.btnPrimary} onClick={handleStart}>
        이 방법으로 시작하기
      </button>
    </div>
  )
}
