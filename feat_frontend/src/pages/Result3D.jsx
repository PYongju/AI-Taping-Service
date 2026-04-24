import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle } from "lucide-react";
import { useSession } from "../context/SessionContext";
import Button from "../components/Button";
import "@google/model-viewer";
import "./Result3D.css";

export default function Result3D() {
  const navigate = useNavigate();
  const { session, updateSession } = useSession();

  // 데이터 안전성: 배열이 없으면 빈 배열 처리
  const options = session.taping_options ?? [];
  const [selectedIdx, setSelectedIdx] = useState(session.selected_option ?? 0);

  // 선택된 옵션이 없는 경우를 대비한 안전 장치
  const selected = options[selectedIdx] ?? options[0] ?? null;

  if (options.length === 0) {
    return (
      <div className="result-3d-error">
        <p className="caption">분석 데이터를 불러오지 못했습니다.</p>
        <Button
          variant="primary"
          size="large"
          fullWidth
          onClick={() => navigate("/input")}
        >
          다시 분석하기
        </Button>
      </div>
    );
  }

  function handleStart() {
    updateSession({ selected_option: selectedIdx });
    navigate("/taping-guide");
  }

  return (
    <div className="result-3d">
      {/* 탭 네비게이션 */}
      <div className="result-3d-tabs">
        {options.map((opt, idx) => (
          <button
            key={opt.taping_id ?? opt.registry_key ?? idx}
            className={`result-3d-tab ${selectedIdx === idx ? "active" : ""}`}
            onClick={() => setSelectedIdx(idx)}
          >
            {opt.title ??
              opt.taping_id ??
              opt.registry_key ??
              `추천 ${idx + 1}`}
          </button>
        ))}
      </div>

      {/* 3D 뷰어 섹션 */}
      <div
        className="result-3d-viewer"
        style={{
          width: "100%",
          height: "350px",
          backgroundColor: "#f5f5f5",
          borderRadius: "12px",
          overflow: "hidden",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        {selected?.model_url ? (
          <model-viewer
            // 🌟 핵심: key를 사용하여 리렌더링 시 무한 호출 및 꼬임 방지
            key={selected.model_url}
            src={selected.model_url}
            camera-controls
            auto-rotate
            shadow-intensity="1"
            style={{ width: "100%", height: "100%" }}
          ></model-viewer>
        ) : (
          <span className="caption" style={{ color: "#888" }}>
            3D 모델을 준비 중입니다...
          </span>
        )}
      </div>

      {/* 추천 이유 및 안내 사항 */}
      <p className="body result-3d-why">
        {selected?.why ??
          "현재 선택된 테이핑 방법에 대한 상세 설명이 없습니다."}
      </p>

      <div className="result-3d-disclaimer">
        <AlertTriangle size={16} strokeWidth={2} />
        <span>
          {selected?.disclaimer ??
            "이 가이드는 예방적 셀프케어 목적이며 의료 진단이 아닙니다."}
        </span>
      </div>

      {/* 시작 버튼 */}
      <Button variant="primary" size="large" fullWidth onClick={handleStart}>
        이 방법으로 시작하기
      </Button>
    </div>
  );
}
