import { useState, useRef, useEffect, Suspense } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import fabImg from "../assets/fab.png";
import "./TapingGuide.css";

import { Canvas, useThree } from "@react-three/fiber";
import { OrbitControls, useGLTF, Stage } from "@react-three/drei";
import * as THREE from "three";

// 🌟 테이프 모델 로드 및 포커스 제어 컴포넌트
function TapeModel({ url, onLoaded }) {
  const { scene } = useGLTF(url);
  useEffect(() => {
    if (scene) onLoaded(scene);
  }, [scene, onLoaded]);
  return <primitive object={scene} />;
}

// 🌟 전체 모델 컨테이너
function ModelContainer({ bodyUrl, tapeUrl }) {
  const { camera, controls } = useThree();
  const body = useGLTF(bodyUrl);
  const [tapeLoaded, setTapeLoaded] = useState(false);

  const handleTapeLoaded = (tapeScene) => {
    if (controls && tapeScene) {
      const box = new THREE.Box3().setFromObject(tapeScene);
      const center = box.getCenter(new THREE.Vector3());
      controls.target.copy(center);
      camera.position.set(center.x + 20, center.y, center.z + 10);
      controls.update();
      setTapeLoaded(true);
    }
  };

  useEffect(() => {
    if (body.scene && controls && !tapeUrl) {
      const box = new THREE.Box3().setFromObject(body.scene);
      const center = box.getCenter(new THREE.Vector3());
      controls.target.copy(center);
      camera.position.set(center.x, center.y, center.z + 5);
      controls.update();
    }
  }, [body.scene, controls, tapeUrl, camera]);

  return (
    <group>
      <primitive object={body.scene} />
      {tapeUrl && <TapeModel url={tapeUrl} onLoaded={handleTapeLoaded} />}
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
  const selectedIdx = session?.selected_option ?? 0;
  const selected = recommendations[selectedIdx];

  // 🌟 [수정 로직] LLM이 반환한 중복 단계를 더 강력하게 제거합니다.
  const rawSteps = selected?.steps || [];
  const steps = rawSteps.filter((item, index, self) => {
    // 공백을 제거한 내용이 이전 단계와 완벽히 일치하면 제거합니다.
    const currentClean = item.instruction.trim().replace(/\s+/g, "");
    return (
      index ===
      self.findIndex(
        (t) => t.instruction.trim().replace(/\s+/g, "") === currentClean,
      )
    );
  });

  const TOTAL = steps.length;
  const currentStepData = steps[step] || {};

  const bodyModelUrl =
    session.glb_url ||
    "https://tapingdata1.blob.core.windows.net/models/body_privacy/JerryPing_BODY.glb";
  const tapeModelUrl = selected?.model_url;

  // 🌟 [중복 방지] 제목이나 내용에서 "Step X" 문구 걷어내기
  const rawTitle = currentStepData.title || "";
  const stepTitle = /^(Step\s*\d+|\d+단계)/i.test(rawTitle.trim())
    ? ""
    : rawTitle;

  const rawInstruction =
    currentStepData.instruction || "상세 데이터를 불러오는 중입니다.";
  const stepInstruction = rawInstruction
    .replace(/^(Step\s*\d+\s*[:\s-]*|\d+단계\s*[:\s-]*)/i, "")
    .trim();

  const poseText =
    currentStepData.pose || "편안한 자세를 취하고 화면의 안내를 따라주세요.";
  const warnText =
    currentStepData.warn ||
    "통증이나 불편함이 느껴지면 즉시 테이핑을 중단하세요.";

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

  async function sendChatbot() {
    if (!cbInput.trim()) {
      setCbShake(true);
      setTimeout(() => setCbShake(false), 400);
      return;
    }
    const userMsg = cbInput;
    setCbInput("");
    setCbMessages((prev) => [
      ...prev,
      { role: "user", text: userMsg },
      { role: "typing" },
    ]);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/taping/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: session.session_id,
          current_step: step + 1,
          instruction: stepInstruction,
          message: userMsg,
        }),
      });
      const data = await res.json();
      setCbMessages((prev) => [
        ...prev.filter((m) => m.role !== "typing"),
        { role: "bot", text: data.reply },
      ]);
    } catch {
      setCbMessages((prev) => [
        ...prev.filter((m) => m.role !== "typing"),
        { role: "bot", text: "테리가 잠시 자리를 비웠어요!" },
      ]);
    }
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

      <div className="content" style={{ padding: "20px 20px 100px 20px" }}>
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
              <Stage
                preset="soft"
                intensity={1}
                environment="city"
                adjustCamera={false}
                center={false}
              >
                <ModelContainer bodyUrl={bodyModelUrl} tapeUrl={tapeModelUrl} />
              </Stage>
              <OrbitControls makeDefault />
            </Suspense>
          </Canvas>
        </div>

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
          {stepTitle && (
            <h2 className="t-h2" style={{ margin: "0 0 12px" }}>
              {stepTitle}
            </h2>
          )}
          <p className="t-body2" style={{ margin: 0, lineHeight: 1.6 }}>
            {stepInstruction}
          </p>
        </div>

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
            {poseText}
          </div>
        </div>

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
          <span style={{ lineHeight: 1.5 }}>{warnText}</span>
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
