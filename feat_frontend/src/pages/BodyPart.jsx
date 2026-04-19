import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import styles from './BodyPart.module.css'

const PARTS = [
  { id: 'knee', label: '무릎', available: true },
  { id: 'ankle', label: '발목', available: false },
  { id: 'shoulder', label: '어깨', available: false },
  { id: 'back', label: '허리', available: false },
  { id: 'arm', label: '팔', available: false },
]

export default function BodyPart() {
  const navigate = useNavigate()
  const { updateSession } = useSession()

  function handleSelect(partId) {
    updateSession({ body_part: partId })
    navigate('/symptom-input')
  }

  return (
    <div className={styles.container}>
      <div className={styles.bubble}>어디가 불편하신가요?</div>
      {PARTS.map((part) => (
        <div key={part.id} className={styles.partRow}>
          <button
            className={part.available ? styles.btnActive : styles.btnDisabled}
            disabled={!part.available}
            onClick={() => handleSelect(part.id)}
          >
            {part.label}
          </button>
          {!part.available && <span className={styles.comingSoon}>coming soon</span>}
        </div>
      ))}
    </div>
  )
}
