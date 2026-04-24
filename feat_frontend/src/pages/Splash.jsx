import { useNavigate } from "react-router-dom";
import myLogo from "../assets/logo.png";
import "./Splash.css";

export default function Splash() {
  const navigate = useNavigate();

  const history = JSON.parse(localStorage.getItem("history") || "[]");
  const isReturning = history.length > 0;

  function handleStart() {
    if (isReturning) {
      navigate("/history");
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
        <div className="splash-badge">
          <svg className="ic ic-sm" viewBox="0 0 24 24">
            <path d="M12 2L3 7v5c0 5.5 3.84 10.74 9 12 5.16-1.26 9-6.5 9-12V7l-9-5z" />
          </svg>
          AI Hub · 실제 체형 데이터 기반
        </div>
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
