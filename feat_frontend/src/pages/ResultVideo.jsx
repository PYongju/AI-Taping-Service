import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'
import { useSession } from '../context/SessionContext'
import styles from './ResultVideo.module.css'

export default function ResultVideo() {
  const navigate = useNavigate()
  const { session, updateSession } = useSession()
  const options = session.taping_options ?? []
  const [selectedId, setSelectedId] = useState(options[0]?.id ?? null)

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
    navigate('/result-3d')
  }

  return (
    <div className={styles.container}>
      <div className={styles.tabRow}>
        {options.map((opt, i) => (
          <button
            key={opt.id}
            className={selectedId === opt.id ? styles.tabActive : styles.tab}
            onClick={() => setSelectedId(opt.id)}
          >
            {opt.id}{i === 0 ? ' 추천' : ''}
          </button>
        ))}
      </div>

      {selected && (
        <div className={styles.card}>
          <div className={styles.cardHeader}>
            <span className={styles.cardTitle}>{selected.name}</span>
            {selected.id === options[0]?.id && (
              <span className={styles.badge}>추천</span>
            )}
          </div>
          <p className={styles.cardInfo}>테이프 타입: {selected.tape_type}</p>
          <p className={styles.cardInfo}>신장률: {selected.stretch_pct}%</p>
          <p className={styles.cardWhy}>{selected.why}</p>
        </div>
      )}

      <div className={styles.videoPlaceholder}>
        <span className={styles.videoText}>영상 준비 중</span>
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
