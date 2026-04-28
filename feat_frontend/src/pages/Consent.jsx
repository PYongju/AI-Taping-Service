import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import DualCTAButton from "../components/DualCTAButton";
import "./Consent.css";

export default function Consent() {
  const navigate = useNavigate();
  const { updateSession } = useSession();

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => navigate("/symptom-input")}>
          <svg className="ic" viewBox="0 0 24 24">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="title">체형 매칭</div>
      </div>

      <div className="content chat-pane">
        <div className="bubble-bot">
          증상을 확인했어요.{"\n"}체형에 맞게 안내드릴게요.
        </div>
        <div className="bubble-bot">
          키, 몸무게, 성별, 전신 사진을{"\n"}알면 더 잘 맞는 방법을 찾을 수
          있어요.
        </div>
        <div className="disclaimer" style={{ marginTop: 12 }}>
          <span className="lock">
            <svg className="ic ic-sm" viewBox="0 0 24 24">
              <rect x="3" y="11" width="18" height="11" rx="2" />
              <path d="M7 11V7a5 5 0 0 1 10 0v4" />
            </svg>
          </span>
          입력하신 정보는 체형 매칭에만 써요. 분석 후 바로 삭제해요.
        </div>
      </div>

      <div className="bottombar">
        <DualCTAButton
          primaryLabel="정보 입력하고 시작할게요"
          secondaryLabel="정보 없이 시작할게요"
          onPrimary={() => {
            updateSession({ body_info_mode: "full" });
            navigate("/body-info");
          }}
          onSecondary={() => {
            updateSession({ body_info_mode: null });
            navigate("/analyzing");
          }}
        />
        <div
          className="t-caption"
          style={{ textAlign: "center", marginTop: 8 }}
        >
          건너뛰면 평균 기준으로 안내돼요
        </div>
      </div>
    </div>
  );
}
