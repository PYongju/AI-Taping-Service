import { useState, useRef, useEffect, Suspense } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import fabImg from "../assets/fab.png";
import "./TapingGuide.css";

import { Canvas, useThree } from "@react-three/fiber";
import { OrbitControls, useGLTF, Stage } from "@react-three/drei";
import * as THREE from "three";

function ModelContainer({ bodyUrl, tapeUrl }) {
  const { camera, controls } = useThree();
  const body = useGLTF(bodyUrl);
  const tape = tapeUrl ? useGLTF(tapeUrl) : null;

  useEffect(() => {
    if (body.scene && controls) {
      const box = new THREE.Box3().setFromObject(body.scene);
      const center = box.getCenter(new THREE.Vector3());
      controls.target.copy(center);
      camera.position.set(center.x, center.y, center.z + 5);
      controls.update();
    }
  }, [body.scene, controls]);

  return (
    <group>
      <primitive object={body.scene} />
      {tape && <primitive object={tape.scene} />}
    </group>
  );
}

export default function TapingGuide() {
  const navigate = useNavigate();
  const { session } = useSession();

  const [step, setStep] = useState(0);
  const [chatOpen, setChatOpen] = useState(false);
  const [cbMessages, setCbMessages] = useState([
    { role: "bot", text: "이 단계에서 궁금한 점을 물어보세요!" },
  ]);
  const [cbInput, setCbInput] = useState("");
  const [cbShake, setCbShake] = useState(false);
  const scrollRef = useRef(null);

  const recommendations =
    session?.taping_recommendations || session?.taping_options || [];
  const selected = recommendations[session?.selected_option ?? 0];
  const steps = selected?.steps || [];
  const TOTAL = steps.length || 1;

  const bodyModelUrl =
    session.glb_url ||
    "https://tapingdata1.blob.core.windows.net/models/body_privacy/JerryPing_Onlybody.glb";
  const tapeModelUrl =
    selected?.model_url ||
    (selected?.technique_code
      ? `https://.../models/knee/JerryPing_${selected.technique_code}.glb`
      : null);

  const currentStepData = steps[step] || {
    title: selected?.title || "테이핑 가이드",
    instruction: selected?.why || "상세 데이터를 불러오는 중입니다.",
    pose: "화면의 안내 자세를 유지해 주세요.",
    warn: "통증이 느껴지면 즉시 중단하세요.",
  };

  useEffect(() => {
    if (scrollRef.current)
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [cbMessages]);

  function handlePrev() {
    if (step > 0) setStep(step - 1);
  }
  function handleNext() {
    if (step < TOTAL - 1) setStep(step + 1);
    else navigate("/complete");
  }

  function sendChatbot() {
    if (!cbInput.trim()) {
      setCbShake(true);
      setTimeout(() => setCbShake(false), 400);
      return;
    }
    setCbMessages((prev) => [
      ...prev,
      { role: "user", text: cbInput },
      { role: "typing" },
    ]);
    setCbInput("");
    setTimeout(() => {
      setCbMessages((prev) => [
        ...prev.filter((m) => m.role !== "typing"),
        { role: "bot", text: "궁금한 점을 물어보세요!" },
      ]);
    }, 1200);
  }

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => navigate("/result-video")}>
          <svg className="ic" viewBox="0 0 24 24">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="title">테이핑 가이드</div>
      </div>

      {/* 🌟 수정 포인트: 패딩을 조절하고 내부 요소들에 margin-bottom(mb)을 추가했습니다. */}
      <div className="content" style={{ padding: "20px 20px 100px 20px" }}>
        {/* 점 인디케이터 영역 */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            marginBottom: "20px",
          }}
        >
          <div className="dots">
            {Array.from({ length: TOTAL }).map((_, i) => (
              <span
                key={i}
                className={`dot ${i < step ? "done" : i === step ? "active" : ""}`}
              />
            ))}
          </div>
          <div
            className="t-caption"
            style={{ color: "var(--fg2)", fontWeight: 600 }}
          >
            {step + 1}/{TOTAL} 단계
          </div>
        </div>

        {/* 3D 모델 영역 */}
        <div
          className="model-3d-container"
          style={{
            width: "100%",
            height: "300px",
            backgroundColor: "#f8f9fa",
            borderRadius: "16px",
            overflow: "hidden",
            marginBottom: "24px",
          }}
        >
          <Canvas style={{ touchAction: "none" }}>
            <Suspense fallback={null}>
              <Stage preset="soft" intensity={1} environment="city">
                <ModelContainer bodyUrl={bodyModelUrl} tapeUrl={tapeModelUrl} />
              </Stage>
              <OrbitControls makeDefault />
            </Suspense>
          </Canvas>
        </div>

        {/* 본문 설명 영역 */}
        <div style={{ marginBottom: "24px" }}>
          <div
            style={{
              font: "600 13px/1 var(--font-base)",
              color: "var(--color-primary)",
              marginBottom: 8,
            }}
          >
            STEP {step + 1}
          </div>
          <h2 className="t-h2" style={{ margin: "0 0 12px" }}>
            {currentStepData.title}
          </h2>
          <p className="t-body2" style={{ margin: 0, lineHeight: 1.6 }}>
            {currentStepData.instruction}
          </p>
        </div>

        {/* 자세 안내 박스 */}
        <div
          style={{
            padding: "16px",
            background: "var(--bg2)",
            borderRadius: "var(--radius-md)",
            marginBottom: "20px",
          }}
        >
          <div
            className="t-caption"
            style={{ color: "var(--fg2)", fontWeight: 600, marginBottom: 8 }}
          >
            자세 안내
          </div>
          <div
            className="t-body2"
            style={{ color: "var(--fg2)", lineHeight: 1.5 }}
          >
            {currentStepData.pose}
          </div>
        </div>

        {/* 경고 박스 */}
        <div
          className="warning"
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: "10px",
            padding: "16px",
            backgroundColor: "var(--bg-warning)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <span className="w-ic" style={{ marginTop: "2px" }}>
            <svg
              className="ic ic-sm"
              viewBox="0 0 24 24"
              style={{ stroke: "var(--color-warning)" }}
            >
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </span>
          <span style={{ lineHeight: 1.5 }}>{currentStepData.warn}</span>
        </div>
      </div>

      <div className="bottombar">
        <div className="step-nav">
          <button
            className="btn btn-secondary"
            disabled={step === 0}
            onClick={handlePrev}
          >
            이전 단계로
          </button>
          <button className="btn btn-primary" onClick={handleNext}>
            {step === TOTAL - 1 ? "완료할게요" : "다음 단계로"}
          </button>
        </div>
      </div>

      {/* 챗봇 섹션 (변경 없음) */}
      <button className="fab" onClick={() => setChatOpen(true)}>
        <img src={fabImg} alt="Terry chat" />
      </button>
      <div
        className={`scrim ${chatOpen ? "show" : ""}`}
        onClick={() => setChatOpen(false)}
      />
      <div className={`sheet ${chatOpen ? "show" : ""}`}>
        <div className="handle" />
        <div
          style={{
            padding: "0 20px 8px",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: "50%",
                background: "#1E1E1E",
                overflow: "hidden",
                border: "1.5px solid #fff",
              }}
            >
              <img
                src={fabImg}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            </div>
            <div>
              <div style={{ font: "700 14px/1 var(--font-base)" }}>테리</div>
            </div>
          </div>
          <button
            style={{ border: "none", background: "none", fontSize: 20 }}
            onClick={() => setChatOpen(false)}
          >
            ✕
          </button>
        </div>
        <div
          ref={scrollRef}
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "16px 20px",
            display: "flex",
            flexDirection: "column",
            gap: 10,
            minHeight: 200,
          }}
        >
          {cbMessages.map((m, i) => (
            <div
              key={i}
              className={m.role === "typing" ? "typing" : `bubble-${m.role}`}
            >
              {m.role === "typing" ? "..." : m.text}
            </div>
          ))}
        </div>
        <div
          style={{
            padding: "12px 20px",
            borderTop: "1px solid var(--gray-100)",
          }}
        >
          <div className={`chat-input ${cbShake ? "shake" : ""}`}>
            <input
              type="text"
              placeholder="메시지 입력..."
              value={cbInput}
              onChange={(e) => setCbInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendChatbot()}
            />
            <button className="send" onClick={sendChatbot}>
              🚀
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
