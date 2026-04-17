import { useNavigate } from 'react-router-dom'
import { Check, X, Lock } from 'lucide-react'
import styles from './PhotoGuide.module.css'

export default function PhotoGuide() {
  const navigate = useNavigate()

  return (
    <div className={styles.container}>
      <p className={styles.title}>
        {'더 정확하게 매칭할게요!\n전신사진을 올려 도와주세요.'}
      </p>

      <div className={styles.guideRow}>
        <div className={styles.guideBox}>
          <p className={styles.guideLabelGood}>
            <Check size={14} strokeWidth={2.5} />
            Good
          </p>
          <ul>
            <li>전신이 들어오게</li>
            <li>몸에 붙는 옷</li>
            <li>단색 벽 앞</li>
          </ul>
        </div>
        <div className={styles.guideBox}>
          <p className={styles.guideLabelBad}>
            <X size={14} strokeWidth={2.5} />
            Bad
          </p>
          <ul>
            <li>반신 촬영</li>
            <li>헐렁한 옷</li>
            <li>복잡한 배경</li>
          </ul>
        </div>
      </div>

      <p className={styles.privacy}>
        <Lock size={13} strokeWidth={2} />
        사진은 분석 후 즉시 삭제됩니다
      </p>

      <button className={styles.btnPrimary} onClick={() => navigate('/photo-upload')}>
        사진 업로드
      </button>
      <button className={styles.btnText} onClick={() => navigate('/analyzing')}>
        건너뛰기
      </button>
    </div>
  )
}
