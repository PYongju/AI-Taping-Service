import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import { matchBody, getTapingRecommend } from "../api/index";
import loadingImg from "../assets/loading.png";
import "./Analyzing.css";

const STEPS = [
  "체형 계산 중이에요",
  "테이핑 방법을 찾고 있어요",
  "곧 결과를 보여드릴게요",
];
const TIPS = [
  "테이핑은 근육이 이완된 상태에서 붙이면 더 잘 붙어요.",
  "땀이나 물기가 있다면 마른 수건으로 닦은 뒤 붙여주세요.",
  "보통 2–3일 유지되지만, 가려움이 있으면 바로 풀어주세요.",
];
const DEFAULT_DISCLAIMER =
  "이 서비스는 예방을 위한 가이드예요. 지속되는 증상은 전문가에게 확인해보세요.";

function normalizeOption(option, idx, ep3) {
  const registryKey =
    option.registry_key ?? ep3.registry_key ?? option.taping_id ?? `${idx + 1}`;
  return {
    ...option,
    taping_id: registryKey,
    registry_key: registryKey,
    name: option.name ?? option.title ?? "추천 테이핑",
    title: option.title ?? option.name ?? "추천 테이핑",
    model_url:
      option.mesh_file ??
      option.combined_glb_url ??
      option.model_url ??
      ep3.model_url ??
      "",
    video_url:
      option.guide_video_url ?? option.video_url ?? ep3.video_url ?? "",
    body_url: option.body_url ?? ep3.glb_url ?? ep3.current_body_url ?? "",
    disclaimer: option.disclaimer ?? ep3.disclaimer ?? DEFAULT_DISCLAIMER,
  };
}

export default function Analyzing() {
  const navigate = useNavigate();
  const { session, updateSession } = useSession();
  const [stepIdx, setStepIdx] = useState(0);
  const [progress, setProgress] = useState(30);
  const [apiError, setApiError] = useState(null);
  const calledRef = useRef(false);
  const inFlightRef = useRef(false);

  useEffect(() => {
    if (calledRef.current) return;
    calledRef.current = true;
    runAnalysis();
  }, []);

  async function runAnalysis() {
    if (inFlightRef.current) return;
    inFlightRef.current = true;
    setApiError(null);
    setStepIdx(0);
    setProgress(30);

    try {
      let model_id = session.model_id || "JerryPing_KT_KNEE_GENERAL";
      let session_id = session.session_id;

      const hasValidModel =
        session.model_id && !session.model_id.includes("JerryPing");

      // 🌟 [수정 포인트] 여기서도 성별이 비어있으면 "none"으로 처리
      const userGender = session.gender || session.sex || "none";

      if (
        session.body_info_mode === "full" &&
        session.height_cm &&
        session.weight_kg &&
        !hasValidModel
      ) {
        const formData = new FormData();
        formData.append("session_id", session_id ?? "");
        formData.append("height_cm", session.height_cm);
        formData.append("weight_kg", session.weight_kg);
        formData.append("image", session.image || "");

        formData.append("sex", userGender);

        try {
          const ep2 = await matchBody(formData);
          model_id = ep2.model_id ?? model_id;
          session_id = ep2.session_id ?? session_id;

          if (ep2.glb_url) {
            updateSession({ glb_url: ep2.glb_url, sex: userGender });
          }
        } catch (cvError) {
          console.warn("CV 분석 실패, 기본 모델 사용");
        }
      }

      updateSession({ model_id, session_id, sex: userGender });
      setStepIdx(1);
      setProgress(60);

      const ep3 = await getTapingRecommend({ session_id, model_id });
      const rawOptions = ep3.options || [];
      const options = rawOptions.map((opt, idx) =>
        normalizeOption(opt, idx, ep3),
      );

      if (!options || options.length === 0) throw new Error("결과 없음");

      setStepIdx(2);
      setProgress(100);

      updateSession({
        taping_options: options,
        selected_option: 0,
        glb_url: ep3.glb_url || session.glb_url,
      });

      setTimeout(() => navigate("/result-video"), 500);
    } catch (error) {
      console.error(error);
      setApiError("분석 데이터를 불러오지 못했습니다.");
    } finally {
      inFlightRef.current = false;
    }
  }

  return (
    <div className="page analyzing-page">
      <div
        className="content"
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          padding: "24px 20px 20px",
          gap: 24,
        }}
      >
        <img
          src={loadingImg}
          alt=""
          style={{
            width: 180,
            height: 180,
            objectFit: "contain",
            marginTop: 16,
          }}
        />
        {apiError ? (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 16,
              textAlign: "center",
            }}
          >
            <div className="t-h1" style={{ fontWeight: 700 }}>
              분석에 실패했어요
            </div>
            <div className="t-body2" style={{ color: "var(--fg2)" }}>
              {apiError}
            </div>
            <button className="btn btn-primary" onClick={runAnalysis}>
              다시 시도할게요
            </button>
          </div>
        ) : (
          <>
            <div style={{ textAlign: "center" }}>
              <div className="t-h1" style={{ fontWeight: 700 }}>
                {STEPS[stepIdx]}
              </div>
              <div className="t-body2" style={{ marginTop: 8 }}>
                잠시만 기다려주세요...
              </div>
            </div>
            <div style={{ width: "100%", maxWidth: 280 }}>
              <div className="pbar">
                <div className="fill" style={{ width: `${progress}%` }} />
              </div>
            </div>
            <div className="tip-card" style={{ width: "100%", marginTop: 8 }}>
              <div className="tag">TIP</div>
              <div
                className="t-body2"
                style={{ color: "var(--fg2)", fontWeight: 500 }}
              >
                {TIPS[stepIdx % TIPS.length]}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
