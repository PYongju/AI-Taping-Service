import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useSession } from '../context/SessionContext'
import styles from './BodyInfo.module.css'

export default function BodyInfo() {
  const navigate = useNavigate()
  const { updateSession } = useSession()
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')

  function handleSubmit() {
    updateSession({
      height_cm: height ? Number(height) : null,
      weight_kg: weight ? Number(weight) : null,
    })
    navigate('/photo-guide')
  }

  function handleSkip() {
    updateSession({ height_cm: null, weight_kg: null })
    navigate('/photo-guide')
  }

  return (
    <div className={styles.container}>
      <div className={styles.bubble}>
        더 정확한 가이드를 드리기 위해 정보를 입력해주세요!
      </div>

      <div className={styles.field}>
        <label className={styles.label}>키</label>
        <div className={styles.inputRow}>
          <input
            type="number"
            className={styles.input}
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            placeholder="170"
          />
          <span className={styles.unit}>cm</span>
        </div>
      </div>

      <div className={styles.field}>
        <label className={styles.label}>몸무게</label>
        <div className={styles.inputRow}>
          <input
            type="number"
            className={styles.input}
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            placeholder="65"
          />
          <span className={styles.unit}>kg</span>
        </div>
      </div>

      <button className={styles.btnPrimary} onClick={handleSubmit}>
        입력 완료
      </button>
      <button className={styles.btnText} onClick={handleSkip}>
        건너뛰기
      </button>
      <p className={styles.skipNote}>
        사진 없이도 시작할 수 있어요. 다만 3D 모델링 수치는 일반값으로 제공돼요.
      </p>
    </div>
  )
}
