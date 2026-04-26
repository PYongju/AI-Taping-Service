import { useNavigate } from "react-router-dom";
import myLogo from "../assets/logo.png";
import "./Splash.css";

export default function Splash() {
  const navigate = useNavigate();

  // 저장된 기록이 있는지 확인
  const history = JSON.parse(localStorage.getItem("history") || "[]");
  const isReturning = history.length > 0;

  function handleStart() {
    if (isReturning) {
      // 🌟 가장 최근 것 하나만 보는 대신, 목록을 보고 고를 수 있게 히스토리로 보냅니다.
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
            새로운 테이핑 시작하기
          </button>
        )}
      </div>
    </div>
  );
}
