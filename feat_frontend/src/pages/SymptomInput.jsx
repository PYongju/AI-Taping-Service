import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import { analyzeSymptoms } from "../api/index";
import "./SymptomInput.css";

const SITUATIONS = [
  { val: "before_exercise", label: "운동 전에" },
  { val: "during_exercise", label: "운동 중에" },
  { val: "after_exercise", label: "운동 후에" },
  { val: "daily", label: "일상에서" },
  { val: "other", label: "기타" },
];

const ACUTE_KEYWORD_PATTERNS = [
  /붓|부었|부어|부은|부음|부종|퉁퉁| swelling/i,
  /못\s*걷|걷기\s*힘|디디기\s*힘|체중.?실|발을\s*못/i,
  /삐었|삐끗|접질|접지르|꺾였|꺾임|염좌/i,
  /넘어|넘어짐|넘어졌|떨어|부딪|충돌/i,
  /골절|금.?간|뼈.?부러|부러진|파열/i,
  /극심|심한\s*통증|참기\s*힘|응급|피.?남|출혈|열감/i,
];

function hasAcuteKeyword(text) {
  return ACUTE_KEYWORD_PATTERNS.some((pattern) => pattern.test(text));
}

const SYMPTOM_CHIPS = [
  { val: "stiff", label: "뻐근하고 뻣뻣해요" },
  { val: "front_pain", label: "무릎 앞쪽이 불편해요" },
  { val: "outer_pain", label: "무릎 바깥쪽이 불편해요" },
  { val: "instability", label: "불안정한 느낌이에요" },
  { val: "prevention", label: "예방 목적이에요" },
  { val: "custom", label: "직접 설명할게요" },
];

export default function SymptomInput() {
  const navigate = useNavigate();
  const { session, updateSession } = useSession();

  const [step, setStep] = useState(1);
  const [situation, setSituation] = useState(null);
  const [situationLabel, setSituationLabel] = useState(null);
  const [inputText, setInputText] = useState("");
  const [shakeInput, setShakeInput] = useState(false);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState(false);
  const [lastPayload, setLastPayload] = useState(null);

  const chatRef = useRef(null);
  const inputRef = useRef(null);
  const inFlightRef = useRef(false); // useState 대신 ref로 이중 진입 차단

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight;
    }
  }, [messages, apiError]);

  useEffect(() => {
    if (step === 2 && situation === "other") {
      inputRef.current?.focus();
    }
  }, [step, situation]);

  function pickSituation(sit) {
    setSituation(sit.val);
    setSituationLabel(sit.label);
  }

  function goToSymptom() {
    updateSession({ situation });
    setStep(2);
  }

  function pickSymptomChip(chip) {
    if (inFlightRef.current) return;

    if (chip.val === "custom") {
      inputRef.current?.focus();
      return;
    }

    if (hasAcuteKeyword(chip.label)) {
      callEP1({
        symptom_type: chip.val,
        user_text: null,
        appendUserMsg: true,
        nextRoute: "hospital",
        hospitalKeyword: chip.label,
      });
      return;
    }

    callEP1({
      symptom_type: chip.val,
      user_text: null,
      appendUserMsg: true,
    });
  }

  function handleSendInput() {
    if (inFlightRef.current) return;

    const msg = inputText.trim();

    if (!msg) {
      setShakeInput(true);
      setTimeout(() => setShakeInput(false), 400);
      return;
    }

    if (hasAcuteKeyword(msg)) {
      callEP1({
        symptom_type: "custom",
        user_text: msg,
        appendUserMsg: true,
        nextRoute: "hospital",
        hospitalKeyword: msg,
      });
      return;
    }

    callEP1({
      symptom_type: "custom",
      user_text: msg,
      appendUserMsg: true,
    });
  }

  async function callEP1({
    symptom_type,
    user_text,
    appendUserMsg = true,
    nextRoute = "consent",
    hospitalKeyword = null,
  }) {
    if (inFlightRef.current) return;
    inFlightRef.current = true; // 렌더 없이 즉시 잠금

    const displayText =
      user_text ??
      SYMPTOM_CHIPS.find((c) => c.val === symptom_type)?.label ??
      symptom_type;

    setApiError(false);
    setLoading(true);
    setLastPayload({ symptom_type, user_text, nextRoute, hospitalKeyword });

    setMessages((prev) => [
      ...prev,
      ...(appendUserMsg ? [{ role: "user", text: displayText }] : []),
      { role: "typing" },
    ]);

    if (appendUserMsg) {
      setInputText("");
    }

    try {
      const result = await analyzeSymptoms({
        body_part: session.part,
        situation,
        symptom_type,
        user_text,
      });

      updateSession({
        session_id: result.session_id,
        symptom: displayText,
      });

      setMessages((prev) => prev.filter((m) => m.role !== "typing"));
      if (nextRoute === "hospital") {
        navigate("/hospital", { state: { keyword: hospitalKeyword ?? displayText } });
      } else {
        navigate("/consent");
      }
    } catch (error) {
      setMessages((prev) => prev.filter((m) => m.role !== "typing"));
      setApiError(true);
    } finally {
      inFlightRef.current = false; // 잠금 해제
      setLoading(false);
    }
  }

  function handleRetry() {
    if (!lastPayload || inFlightRef.current) return;

    callEP1({
      ...lastPayload,
      appendUserMsg: false,
    });
  }

  return (
    <div className="page">
      <div className="topbar">
        <button
          className="back"
          onClick={() => (step === 1 ? navigate("/body-part") : setStep(1))}
        >
          <svg className="ic" viewBox="0 0 24 24">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="title">증상 입력</div>
      </div>

      {step === 1 ? (
        <>
          <div className="content chat-pane">
            <div className="bubble-bot">
              {`${session.part || "무릎"}이 불편하시군요.\n언제 불편하세요?`}
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 8,
                marginTop: 12,
              }}
            >
              {SITUATIONS.map((sit) => (
                <button
                  key={sit.val}
                  className={`chip ${situation === sit.val ? "selected" : ""}`}
                  onClick={() => pickSituation(sit)}
                >
                  {sit.label}
                </button>
              ))}
            </div>

            {situationLabel && (
              <>
                <div className="bubble-user">{situationLabel}</div>
                <div className="bubble-bot">
                  알겠어요. 다음 단계로 넘어갈까요?
                </div>
              </>
            )}
          </div>

          <div className="bottombar">
            <button
              className="btn btn-primary"
              disabled={!situation}
              onClick={goToSymptom}
            >
              다음으로 넘어갈게요
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="content chat-pane" ref={chatRef}>
            <div className="bubble-bot">어떤 느낌인지 알려주세요</div>

            <div className="symptom-chips">
              {SYMPTOM_CHIPS.map((chip) => (
                <button
                  key={chip.val}
                  className="chip"
                  disabled={loading}
                  onClick={() => pickSymptomChip(chip)}
                >
                  {chip.label}
                </button>
              ))}
            </div>

            {messages.map((m, i) =>
              m.role === "typing" ? (
                <div key={i} className="typing">
                  <span />
                  <span />
                  <span />
                </div>
              ) : (
                <div key={i} className={`bubble-${m.role}`}>
                  {m.text}
                </div>
              ),
            )}

            {apiError && (
              <div className="error-inline">
                <span>연결이 끊겼어요</span>
                <button className="btn-retry" onClick={handleRetry}>
                  다시 시도해볼게요
                </button>
              </div>
            )}
          </div>

          <div className="bottombar">
            <div className={`chat-input ${shakeInput ? "shake" : ""}`}>
              <input
                ref={inputRef}
                type="text"
                placeholder="자세히 입력해주세요"
                value={inputText}
                disabled={loading}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendInput()}
              />
              <button
                className="send"
                disabled={loading}
                onClick={handleSendInput}
              >
                <svg
                  className="ic ic-sm"
                  viewBox="0 0 24 24"
                  style={{ stroke: "#fff" }}
                >
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon
                    points="22 2 15 22 11 13 2 9 22 2"
                    fill="#fff"
                    stroke="#fff"
                  />
                </svg>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
