import { useState, useRef, useEffect, Suspense } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import fabImg from "../assets/fab.png";
import "./TapingGuide.css";

// 🌟 신규 뷰어 라이브러리 (성능 및 자동화 전용)
import { Canvas } from "@react-three/fiber";
import {
  OrbitControls,
  Center,
  useGLTF,
  Environment,
  Stage,
  Html,
} from "@react-three/drei";

/**
 * 하드코딩된 테이핑 모델 URL
 */
const HARDCODED_TAPE_URL =
  "https://tapingdata1.blob.core.windows.net/models/knee/3148M_KT_KNEE_LATERAL.glb";
const BODY_MODEL_URL =
  "https://tapingdata1.blob.core.windows.net/models/body/3148M_BD_B.glb";

/**
 * 3D 모델 컴포넌트
 */
function ModelContainer({ tapeUrl }) {
  const { camera, controls } = useThree(); // R3F의 내부 상태 가져오기
  const body = useGLTF(BODY_MODEL_URL);
  const tape = useGLTF(tapeUrl);

  useEffect(() => {
    if (tape.scene && controls) {
      // 1. 테이핑 모델의 경계 상자 계산
      const box = new THREE.Box3().setFromObject(tape.scene);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());

      // 2. 카메라의 초점(Target)을 테이핑 모델의 중심으로 변경
      controls.target.copy(center);

      // 3. 카메라 위치를 적절히 당기기 (모델 크기에 맞춰 거리 조절)
      const maxDim = Math.max(size.x, size.y, size.z);
      const distance = maxDim * 3; // 숫자가 작을수록 더 가까이 확대됩니다.
      camera.position.set(center.x, center.y, center.z + distance);

      controls.update();
    }
  }, [tape, camera, controls]);

  return (
    <group>
      <primitive object={body.scene} />
      <primitive object={tape.scene} />
    </group>
  );
}

/**
 * 로딩 중 표시될 UI
 */
function Loader() {
  return (
    <Html center>
      <div
        style={{
          background: "rgba(255,255,255,0.9)",
          padding: "12px 24px",
          borderRadius: "30px",
          fontSize: "13px",
          fontWeight: "700",
          color: "var(--color-primary)",
          boxShadow: "0 4px 20px rgba(0,0,0,0.12)",
          whiteSpace: "nowrap",
        }}
      >
        테리 가이드 불러오는 중...
      </div>
    </Html>
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

  const currentOption = session.taping_options?.[session.selected_option || 0];
  const activeSteps = currentOption?.steps || [];
  const TOTAL = activeSteps.length || 1;
  const s = activeSteps[step] || {
    title: "가이드 준비 중",
    desc: "-",
    pose: "-",
    warn: "-",
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
        {
          role: "bot",
          text: "테이핑을 붙일 때 근육을 늘린 상태에서 붙이는 것이 중요해요!",
        },
      ]);
    }, 1200);
  }

  return (
    <div className="page" style={{ position: "relative" }}>
      <div className="topbar">
        <button className="back" onClick={() => navigate("/result-video")}>
          <svg className="ic" viewBox="0 0 24 24">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="title">테이핑 가이드</div>
      </div>

      <div
        className="content"
        style={{
          padding: "16px 20px 20px",
          display: "flex",
          flexDirection: "column",
          gap: 16,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
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

        {/* 🌟 3D 뷰어 영역: 카메라 자동 정렬 적용 */}
        <div
          className="model-3d-container"
          style={{
            width: "100%",
            height: "300px",
            backgroundColor: "#f8f9fa",
            borderRadius: "16px",
            overflow: "hidden",
          }}
        >
          <Canvas shadows camera={{ position: [0, 0, 4], fov: 40 }}>
            <Suspense fallback={<Loader />}>
              {/* Stage는 조명, 그림자, 그리고 모델이 화면에 꽉 차도록 카메라를 자동 조정해줍니다. */}
              <Stage
                environment="city"
                intensity={0.5}
                contactShadow={{ opacity: 0.2, blur: 2 }}
                adjustCamera={1.2}
              >
                <Center>
                  <ModelContainer tapeUrl={HARDCODED_TAPE_URL} />
                </Center>
              </Stage>
              <OrbitControls makeDefault minDistance={1} maxDistance={8} />
            </Suspense>
          </Canvas>
        </div>

        <div>
          <div
            style={{
              font: "600 13px/1 var(--font-base)",
              color: "var(--color-primary)",
              marginBottom: 6,
            }}
          >
            STEP {step + 1}
          </div>
          <h2 className="t-h2" style={{ margin: "0 0 8px" }}>
            {s.title}
          </h2>
          <p className="t-body2" style={{ margin: 0 }}>
            {s.desc}
          </p>
        </div>

        <div
          style={{
            padding: "12px 14px",
            background: "var(--bg2)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <div
            className="t-caption"
            style={{ color: "var(--fg2)", fontWeight: 600, marginBottom: 4 }}
          >
            자세 안내
          </div>
          <div className="t-body2" style={{ color: "var(--fg2)" }}>
            {s.pose}
          </div>
        </div>

        <div className="warning">
          <span className="w-ic">
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
          <span>{s.warn}</span>
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
                alt=""
              />
            </div>
            <div>
              <div style={{ font: "700 14px/1 var(--font-base)" }}>테리</div>
              <div className="t-caption" style={{ marginTop: 3 }}>
                궁금한 걸 물어보세요
              </div>
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
              {m.role === "typing" ? (
                <>
                  <span />
                  <span />
                  <span />
                </>
              ) : (
                m.text
              )}
            </div>
          ))}
        </div>
        <div
          style={{
            padding: "12px 20px calc(12px + env(safe-area-inset-bottom))",
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
