import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext"; // 🌟 추가
import myLogo from "../assets/logo.png";
import "./Splash.css";

export default function Splash() {
  const navigate = useNavigate();
  const { updateSession } = useSession(); // 🌟 추가

  const history = JSON.parse(localStorage.getItem("history") || "[]");
  const isReturning = history.length > 0;

  function handleStart() {
    if (isReturning) {
      // 🌟 [핵심] 가장 최근에 저장한 데이터를 세션에 다시 주입합니다.
      const last = history[0];
      updateSession({
        session_id: last.id,
        glb_url: last.glb_url, // 바디 모델 복구
        taping_options: [
          {
            name: last.option_name,
            model_url: last.model_url, // 테이프 모델 복구
            video_url: last.video_url, // 영상 복구
            steps: last.steps, // 가이드 단계 복구
          },
        ],
        selected_option: 0,
        part: last.body_part,
      });
      // 데이터 주입 후 바로 가이드 화면으로 이동
      navigate("/result-3d");
    } else {
      navigate("/body-part");
    }
  }

  return (
    <div className="page splash-page">
      <div className="content splash-content">
        <img src={myLogo} alt="TerryPiQ" className="splash-logo" />
        <div className="splash-brand">TERRYPIQ</div>
        <h1 className="t-h1 splash-headline">
          이제, 운동 후 무심코 넘기던
          {"\n"}
          나만을 위한 맞춤 테이핑
        </h1>
      </div>
      <div
        className="bottombar"
        style={{ display: "flex", flexDirection: "column", gap: 8 }}
      >
        <button className="btn btn-primary" onClick={handleStart}>
          {isReturning ? "이어서 시작할게요" : "맞춤 테이핑 시작할게요"}
        </button>
        {isReturning && (
          <button
            className="btn btn-text"
            onClick={() => navigate("/body-part")}
          >
            새로 시작할게요
          </button>
        )}
        <p className="splash-note">
          🧪 맞춤 테이핑을 안내하는 학술 프로젝트예요.
        </p>
      </div>
    </div>
  );
}
