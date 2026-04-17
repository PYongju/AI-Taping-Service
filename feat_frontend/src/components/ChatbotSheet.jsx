import { useState } from 'react'
import styles from './ChatbotSheet.module.css'

const BOT_REPLY = '죄송해요, 현재 연결 중입니다. 잠시 후 다시 시도해주세요.'

export default function ChatbotSheet({ isOpen, onClose }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')

  function handleSend() {
    if (!input.trim()) return
    const userMsg = { role: 'user', text: input.trim() }
    const botMsg = { role: 'bot', text: BOT_REPLY }
    setMessages((prev) => [...prev, userMsg, botMsg])
    setInput('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!isOpen) return null

  return (
    <>
      <div className={styles.backdrop} onClick={onClose} />
      <div className={styles.sheet}>
        <div className={styles.handle} />
        <div className={styles.messages}>
          {messages.length === 0 && (
            <p className={styles.empty}>무엇이든 물어보세요!</p>
          )}
          {messages.map((m, i) => (
            <div
              key={i}
              className={m.role === 'user' ? styles.userBubble : styles.botBubble}
            >
              {m.text}
            </div>
          ))}
        </div>
        <div className={styles.inputRow}>
          <input
            className={styles.input}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="메시지를 입력하세요"
          />
          <button className={styles.sendBtn} onClick={handleSend}>
            전송
          </button>
        </div>
      </div>
    </>
  )
}
