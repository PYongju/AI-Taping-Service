import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import { saveSession } from "../api/index";
import doneImg from "../assets/done.png";
import "./Complete.css";

const MOCK_OPTIONS = [
  {
    taping_id: "A",
    name: "기본 무릎 고정 테이핑",
    tape_type: "Y-strip",
    stretch_pct: 15,
  },
  {
    taping_id: "B",
    name: "보강형 무릎 테이핑",
    tape_type: "I-strip",
    stretch_pct: 25,
  },
];

export default function Complete() {
  const navigate = useNavigate();
  const { session, resetSession } = useSession();

  const options =
    session.taping_options.length > 0 ? session.taping_options : MOCK_OPTIONS;
  const o = options[session.selected_option ?? 0] ?? options[0];
  const now = new Date();
  const time = `${now.getHours().toString().padStart(2, "0")}:${now
    .getMinutes()
    .toString()
    .padStart(2, "0")}`;

  const [toast, setToast] = useState("");
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const timerRef = useRef(null);

  function showToast(msg) {
    setToast(msg);
    clearTimeout(timerRef.current);
    timerRef.current = setTimeout(() => setToast(""), 2000);
  }

  async function handleSave() {
    if (saving || saved) return;
    setSaving(true);
    const historyEntry = {
      date: new Date().toLocaleDateString("ko-KR"),
      body_part: session.part ?? "knee",
      option: o.name,
    };
    try {
      await saveSession({
        session_id: session.session_id,
        taping_id: o.taping_id,
      });
      setSaved(true);
      showToast("결과를 저장했어요");
    } catch {
      showToast("서버 저장에 실패했어요. 기기에는 저장할게요.");
    } finally {
      const prev = JSON.parse(localStorage.getItem("history") || "[]");
      localStorage.setItem("history", JSON.stringify([historyEntry, ...prev]));
      setSaving(false);
    }
  }

  function handleRestart() {
    resetSession();
    navigate("/body-part");
  }

  return (
    <div className="page">
      <div
        className="content"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "32px 24px",
          textAlign: "center",
          gap: 24,
        }}
      >
        <img
          src={doneImg}
          alt=""
          style={{ width: 180, height: 180, objectFit: "contain" }}
        />

        <div>
          <h1 className="t-h1" style={{ margin: 0 }}>
            테이핑을 완료했어요
          </h1>
          <p
            className="t-body2"
            style={{ margin: "12px 0 0", whiteSpace: "pre-line" }}
          >
            무릎을 돌리거나 걸을 때 느낌이 어떤지
            {"\n"}
            잠깐 체크해보세요
          </p>
        </div>

        <div
          style={{
            width: "100%",
            background: "var(--bg2)",
            borderRadius: "var(--radius-lg)",
            padding: 16,
            display: "flex",
            flexDirection: "column",
            gap: 10,
            textAlign: "left",
          }}
        >
          <div
            className="t-caption"
            style={{ color: "var(--fg2)", fontWeight: 600 }}
          >
            오늘의 테이핑
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span className="t-body2" style={{ color: "var(--fg2)" }}>
              기법
            </span>
            <span
              style={{
                font: "600 14px/1 var(--font-base)",
                color: "var(--fg1)",
              }}
            >
              {o.name}
            </span>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span className="t-body2" style={{ color: "var(--fg2)" }}>
              테이프
            </span>
            <span
              style={{
                font: "600 14px/1 var(--font-base)",
                color: "var(--fg1)",
              }}
            >
              {o.tape_type} / {o.stretch_pct}%
            </span>
          </div>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span className="t-body2" style={{ color: "var(--fg2)" }}>
              시각
            </span>
            <span
              style={{
                font: "600 14px/1 var(--font-base)",
                color: "var(--fg1)",
              }}
            >
              {time}
            </span>
          </div>
        </div>
      </div>

      <div
        className="bottombar"
        style={{ display: "flex", flexDirection: "column", gap: 8 }}
      >
        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={saving || saved}
        >
          결과 저장할게요
        </button>

        <div style={{ display: "flex", gap: 8 }}>
          <button
            className="btn btn-secondary"
            onClick={() => showToast("이미지로 저장했어요")}
          >
            이미지 저장
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => showToast("링크를 복사했어요")}
          >
            링크 공유
          </button>
        </div>
        <button
          className="btn btn-secondary"
          onClick={() => navigate("/result-video")}
          style={{ marginTop: 4 }}
        >
          다른 테이핑도 볼게요
        </button>
        <button className="btn btn-text" onClick={handleRestart}>
          처음부터 다시 볼게요
        </button>
        <p className="complete-note">
          📚 재구성된 가이드예요 · 원문은 사용하지 않았어요.
        </p>
      </div>

      <div className={`toast ${toast ? "show" : ""}`}>{toast}</div>
    </div>
  );
}
