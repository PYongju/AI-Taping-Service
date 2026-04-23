import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import styles from "./History.module.css";

export default function History() {
  const navigate = useNavigate();
  const { resetSession } = useSession();
  const history = JSON.parse(localStorage.getItem("history") || "[]");

  function handleYes() {
    navigate("/result-3d");
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
                {item.body_part} · {item.option}
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
