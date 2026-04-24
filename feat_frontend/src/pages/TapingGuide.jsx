import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import fabImg from "../assets/fab.png";
import "./TapingGuide.css";

import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

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

  const mountRef = useRef(null);
  const scrollRef = useRef(null);
  const animationIdRef = useRef(null);

  const currentOption = session.taping_options?.[session.selected_option || 0];
  const activeSteps = currentOption?.steps || [];
  const TOTAL = activeSteps.length || 1;
  const s = activeSteps[step] || {
    title: "가이드 준비 중",
    desc: "-",
    pose: "-",
    warn: "-",
  };
  const tapeModelUrl = currentOption?.mesh_file || currentOption?.model_url;

  useEffect(() => {
    if (!mountRef.current) return;
    mountRef.current.innerHTML = "";

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#e0e0e0");
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    camera.position.set(0, 1, 3);
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
    });
    renderer.setSize(
      mountRef.current.clientWidth,
      mountRef.current.clientHeight,
    );
    mountRef.current.appendChild(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    scene.add(new THREE.AmbientLight(0xffffff, 1.2));
    scene.add(new THREE.DirectionalLight(0xffffff, 0.6));

    const loader = new GLTFLoader();
    const prefix = (session.model_id || "JerryPing").split("_")[0];
    const bodyUrl = `https://tapingdata1.blob.core.windows.net/models/body_privacy/JerryPing_BODY.glb`;

    // 🌟 안전한 분리 로딩: 바디 로드 후 테이핑 모델 로드
    loader.load(
      bodyUrl,
      (gltf) => {
        scene.add(gltf.scene);
        if (tapeModelUrl) {
          setTimeout(() => {
            loader.load(
              tapeModelUrl,
              (tape) => scene.add(tape.scene),
              null,
              (e) => console.error("테이핑 로드 에러:", e),
            );
          }, 500); // 0.5초 대기하여 메인 스레드 확보
        }
      },
      null,
      (e) => console.error("바디 로드 에러:", e),
    );

    const animate = () => {
      animationIdRef.current = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(animationIdRef.current);
      renderer.dispose();
      mountRef.current.innerHTML = "";
    };
  }, [tapeModelUrl, session.model_id]);

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
        { role: "bot", text: "이 단계에서 궁금한 점을 물어보세요!" },
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
        <div
          className="model-3d-container"
          ref={mountRef}
          style={{
            width: "100%",
            height: "280px",
            backgroundColor: "#f5f5f5",
            borderRadius: "12px",
            overflow: "hidden",
          }}
        />
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
        <div className="disclaimer">
          <span className="lock">
            <svg className="ic ic-sm" viewBox="0 0 24 24">
              <path d="M12 9v4M12 17h.01" />
              <circle cx="12" cy="12" r="10" />
            </svg>
          </span>
          {currentOption?.disclaimer || "이 서비스는 예방을 위한 가이드예요."}
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
      <button
        className="fab"
        onClick={() => setChatOpen(true)}
        aria-label="챗봇 열기"
      >
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
            style={{
              border: "none",
              background: "var(--bg3)",
              width: 32,
              height: 32,
              borderRadius: "50%",
              color: "var(--fg2)",
              fontSize: 14,
            }}
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
