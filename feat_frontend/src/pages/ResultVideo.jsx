import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import "./ResultVideo.css";

const MOCK_OPTIONS = [
  {
    taping_id: "A",
    name: "기본 무릎 고정 테이핑",
    tape_type: "Y-strip",
    stretch_pct: 15,
    why: "무릎 안정성을 높이는 가장 보편적인 방식입니다.",
  },
  {
    taping_id: "B",
    name: "보강형 무릎 테이핑",
    tape_type: "I-strip",
    stretch_pct: 25,
    why: "조금 더 단단한 고정을 위한 대안 방식입니다.",
  },
];

export default function ResultVideo() {
  const navigate = useNavigate();
  const { session, updateSession } = useSession();
  const options =
    session.taping_options?.length > 0 ? session.taping_options : MOCK_OPTIONS;
  const [optIdx, setOptIdx] = useState(session.selected_option ?? 0);
  const [toast, setToast] = useState("");
  const toastTimer = useRef(null);
  const o = options[optIdx] ?? options[0];

  // 🌟 유연한 데이터 매핑 로직 적용
  const displayTitle = o.title || o.name || o.technique_name || "추천 테이핑";
  const displayWhy =
    o.why ||
    o.description ||
    o.explanation ||
    "분석된 증상에 가장 적합한 테이핑 방법입니다.";
  const displayCoach =
    o.coach ||
    o.coach_tips ||
    o.tips ||
    "안내에 따라 정확한 위치에 부착해주세요.";
  const displayTapeType = o.tape_type || o.type || "Kinesiology Tape";
  const displayStretch = o.stretch_pct ?? o.stretch ?? 0;

  function showToast(message) {
    setToast(message);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(""), 2000);
  }
  function handleOptionClick(idx) {
    if (idx > 0) {
      showToast("옵션 B는 지금 준비 중입니다.");
      return;
    }
    setOptIdx(idx);
  }
  function startGuide() {
    updateSession({ selected_option: optIdx });
    navigate("/result-3d");
  }

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => navigate("/analyzing")}>
          <svg className="ic" viewBox="0 0 24 24">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="title">추천 결과</div>
      </div>
      <div
        className="content"
        style={{
          padding: "20px 20px 24px",
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        <div>
          <div
            style={{
              font: "500 12px/1 var(--font-base)",
              color: "var(--color-primary)",
              marginBottom: 6,
            }}
          >
            {session.body_info_mode === "full"
              ? "체형에 맞는 모델을 찾았어요"
              : "평균 체형을 기준으로 찾았어요"}
          </div>
          <h2 className="t-h1" style={{ margin: 0 }}>
            무릎에 맞는 테이핑을 찾았어요
          </h2>
          <p className="t-body2" style={{ margin: "8px 0 0" }}>
            아래 추천 방법을 확인해보세요.
          </p>
        </div>
        <div className="opt-switch">
          {options.map((option, idx) => (
            <button
              key={option.taping_id || idx}
              className={`${optIdx === idx ? "active" : ""} ${idx > 0 ? "locked" : ""}`}
              onClick={() => handleOptionClick(idx)}
            >
              {idx === 0 ? (
                <>
                  <span className="star">★</span> 추천 A
                </>
              ) : (
                "추천 B"
              )}
            </button>
          ))}
        </div>
        <div className="card selected">
          <div
            style={{
              font: "700 17px/1.3 var(--font-base)",
              color: "var(--fg1)",
            }}
          >
            {displayTitle}
          </div>
          <div
            style={{
              display: "flex",
              gap: 10,
              margin: "12px 0",
              flexWrap: "wrap",
            }}
          >
            <span
              style={{
                padding: "6px 10px",
                background: "var(--bg3)",
                borderRadius: "var(--radius-full)",
                font: "600 12px/1 var(--font-base)",
                color: "var(--fg2)",
              }}
            >
              테이프{" "}
              <span style={{ color: "var(--fg1)" }}>{displayTapeType}</span>
            </span>
            <span
              style={{
                padding: "6px 10px",
                background: "var(--bg3)",
                borderRadius: "var(--radius-full)",
                font: "600 12px/1 var(--font-base)",
                color: "var(--fg2)",
              }}
            >
              stretch{" "}
              <span style={{ color: "var(--fg1)" }}>{displayStretch}%</span>
            </span>
          </div>
          <div
            style={{
              font: "400 13px/1.55 var(--font-base)",
              color: "var(--fg2)",
              whiteSpace: "pre-line",
            }}
          >
            {displayWhy}
          </div>
        </div>
        {o.video_url ? (
          <video
            className="result-video-player"
            src={o.video_url}
            controls
            playsInline
            autoPlay
            muted
          />
        ) : (
          <div className="video-placeholder">
            <svg
              className="ic ic-lg"
              viewBox="0 0 24 24"
              style={{ stroke: "var(--fg3)" }}
            >
              <polygon points="5 3 19 12 5 21 5 3" fill="var(--fg3)" />
            </svg>
            테이핑 시연 영상
          </div>
        )}
        <div className="disclaimer simple-disclaimer">
          <span className="lock">⚠️</span>지속되는 증상은 전문가에게
          확인해보세요.
        </div>
        <div
          className="t-body2"
          style={{
            padding: "12px 14px",
            background: "#fff7ed",
            borderRadius: "var(--radius-md)",
            color: "#9a3412",
            fontWeight: 500,
          }}
        >
          {displayCoach}
        </div>
      </div>
      <div className="bottombar">
        <button className="btn btn-primary" onClick={startGuide}>
          이 방법으로 시작할게요
        </button>
      </div>
      <div className={`toast ${toast ? "show" : ""}`}>{toast}</div>
    </div>
  );
}
