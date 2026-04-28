import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import styles from "./History.module.css";

export default function History() {
  const navigate = useNavigate();
  const { updateSession, resetSession } = useSession();
  const history = JSON.parse(localStorage.getItem("history") || "[]");

  function handleYes() {
    if (history.length > 0) {
      const last = history[0]; // 가장 최근 기록 가져오기

      // 🌟 저장된 상세 데이터를 현재 세션에 다시 주입하여 복구
      updateSession({
        session_id: last.id,
        glb_url: last.glb_url, // 바디 모델 복구
        taping_options: [
          {
            name: last.option_name,
            title: last.option_name,
            why: last.why,
            coach: last.coach,
            model_url: last.model_url, // 테이프 모델 복구
            video_url: last.video_url, // 영상 URL 복구
            steps: last.steps, // 가이드 단계 복구
            tape_type: last.tape_type,
            stretch_pct: last.stretch_pct,
          },
        ],
        selected_option: 0,
        part: last.body_part,
      });

      // 복구 후 바로 결과 화면으로 이동
      navigate("/result-video");
    } else {
      navigate("/body-part");
    }
  }

  function handleNo() {
    resetSession();
    navigate("/body-part");
  }

  function handleNewStart() {
    resetSession();
    navigate("/body-part");
  }

  return (
    <div className={styles.container}>
      <h2 className={styles.header}>이전 기록</h2>

      {history.length === 0 ? (
        <p className={styles.empty}>아직 기록이 없어요</p>
      ) : (
        <div className={styles.list}>
          {history.map((item, i) => (
            <div key={i} className={styles.card}>
              <p className={styles.date}>{item.date}</p>
              <p className={styles.info}>
                {item.body_part} · {item.option_name || item.option}
              </p>
            </div>
          ))}
        </div>
      )}

      <div className={styles.bubble}>이전과 같은 부위인가요?</div>

      <div className={styles.btnRow}>
        <button className={styles.btnYes} onClick={handleYes}>
          네, 같아요
        </button>
        <button className={styles.btnNo} onClick={handleNo}>
          아니요, 달라요
        </button>
      </div>

      <button className={styles.btnPrimary} onClick={handleNewStart}>
        새로 시작하기
      </button>
    </div>
  );
}
