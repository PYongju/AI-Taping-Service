import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, MessageCircle } from 'lucide-react'
import { useSession } from '../context/SessionContext'
import ChatbotSheet from '../components/ChatbotSheet'
import styles from './Complete.module.css'

export default function Complete() {
  const navigate = useNavigate()
  const { session, resetSession } = useSession()
  const [chatOpen, setChatOpen] = useState(false)

  function handleSave() {
    const history = JSON.parse(localStorage.getItem('history') || '[]')
    history.unshift({
      date: new Date().toLocaleDateString('ko-KR'),
      body_part: session.body_part,
      option: session.selected_option?.name ?? '-',
    })
    localStorage.setItem('history', JSON.stringify(history))
  }

  function handleRestart() {
    resetSession()
    navigate('/body-part')
  }

  return (
    <div className={styles.container}>
      <div className={styles.iconWrap}>
        <CheckCircle2 size={36} strokeWidth={2} />
      </div>
      <h1 className={styles.title}>테이핑 완료!</h1>
      <p className={styles.message}>잘 하셨어요! 테이핑을 완료했습니다.</p>

      <button className={styles.btnPrimary} onClick={handleSave}>
        결과 저장
      </button>
      <button className={styles.btnSecondary} onClick={handleRestart}>
        처음부터 다시
      </button>
      <button className={styles.btnText} onClick={() => navigate('/body-part')}>
        다른 테이핑 물어보기
      </button>

      <button className={styles.fab} onClick={() => setChatOpen(true)}>
        <MessageCircle size={22} strokeWidth={2} />
      </button>

      <ChatbotSheet isOpen={chatOpen} onClose={() => setChatOpen(false)} />
    </div>
  )
}
