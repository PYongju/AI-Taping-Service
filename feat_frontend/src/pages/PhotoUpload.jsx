import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Camera } from 'lucide-react'
import { useSession } from '../context/SessionContext'
import { matchBody } from '../api/index'
import styles from './PhotoUpload.module.css'

export default function PhotoUpload() {
  const navigate = useNavigate()
  const { session, updateSession } = useSession()
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  function handleFileChange(e) {
    const f = e.target.files[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setError(null)
  }

  async function handleAnalyze() {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const formData = new FormData()
      formData.append('image', file)
      formData.append('session_id', session.session_id ?? '')
      if (session.height_cm != null) formData.append('height_cm', session.height_cm)
      if (session.weight_kg != null) formData.append('weight_kg', session.weight_kg)
      const result = await matchBody(formData)
      updateSession({ model_id: result.model_id, glb_url: result.glb_url })
      navigate('/analyzing')
    } catch {
      setError('업로드에 실패했어요. 다시 시도해주세요.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className={styles.hiddenInput}
        onChange={handleFileChange}
      />

      <button className={styles.btnUpload} onClick={() => inputRef.current.click()}>
        <Camera size={18} strokeWidth={2} />
        {file ? '사진 다시 선택' : '사진 선택하기'}
      </button>

      {preview && (
        <img src={preview} alt="미리보기" className={styles.preview} />
      )}

      {error && <p className={styles.error}>{error}</p>}

      <button
        className={styles.btnPrimary}
        onClick={handleAnalyze}
        disabled={!file || loading}
      >
        {loading ? '분석 중...' : '분석 시작'}
      </button>
    </div>
  )
}
