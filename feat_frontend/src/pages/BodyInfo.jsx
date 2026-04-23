import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import goodGuideImage from "../assets/good.png";
import badGuideImage from "../assets/bad.png";
import "./BodyInfo.css";

export default function BodyInfo() {
  const navigate = useNavigate();
  const { updateSession } = useSession();

  const [tab, setTab] = useState(1);
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [gender, setGender] = useState(null);
  const [heightErr, setHeightErr] = useState(false);
  const [weightErr, setWeightErr] = useState(false);
  const [photoUploaded, setPhotoUploaded] = useState(false);
  const [photoPreviewUrl, setPhotoPreviewUrl] = useState("");
  const [toast, setToast] = useState("");
  const toastTimer = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      if (photoPreviewUrl) URL.revokeObjectURL(photoPreviewUrl);
    };
  }, [photoPreviewUrl]);

  function showToast(msg) {
    setToast(msg);
    clearTimeout(toastTimer.current);
    toastTimer.current = setTimeout(() => setToast(""), 2000);
  }

  function validateStep1() {
    const h = parseFloat(height);
    const w = parseFloat(weight);
    let ok = true;
    if (!h || h < 100 || h > 230) {
      setHeightErr(true);
      ok = false;
    } else {
      setHeightErr(false);
    }
    if (!w || w < 30 || w > 200) {
      setWeightErr(true);
      ok = false;
    } else {
      setWeightErr(false);
    }
    if (!ok) showToast("입력값을 확인해주세요");
    return ok;
  }

  function handleNext() {
    if (tab === 1) {
      if (!validateStep1()) return;
      updateSession({
        height_cm: parseFloat(height),
        weight_kg: parseFloat(weight),
        gender: gender === "skip" ? null : gender,
      });
      setTab(2);
    } else if (tab === 2) {
      setTab(3);
    } else {
      if (!photoUploaded) {
        showToast("사진을 올려주세요");
        return;
      }
      navigate("/analyzing");
    }
  }

  return (
    <div className="page">
      <div className="topbar">
        <button
          className="back"
          onClick={() => (tab > 1 ? setTab(tab - 1) : navigate("/consent"))}
        >
          <svg className="ic" viewBox="0 0 24 24">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </button>
        <div className="title">체형 정보</div>
      </div>

      <div className="content" style={{ padding: "20px 20px 24px" }}>
        <div className="step-tabs">
          <button
            className={tab === 1 ? "active" : ""}
            onClick={() => setTab(1)}
          >
            1. 기본정보
          </button>
          <button
            className={tab === 2 ? "active" : ""}
            disabled={tab < 2}
            onClick={() => tab >= 2 && setTab(2)}
          >
            2. 촬영가이드
          </button>
          <button
            className={tab === 3 ? "active" : ""}
            disabled={tab < 3}
            onClick={() => tab >= 3 && setTab(3)}
          >
            3. 사진업로드
          </button>
        </div>

        {tab === 1 && (
          <div>
            <h2 className="t-h2" style={{ margin: "0 0 4px" }}>
              기본 정보를 알려주세요
            </h2>
            <p className="t-body2" style={{ margin: "0 0 20px" }}>
              체형 매칭에만 써요. 분석 후 바로 삭제해요.
            </p>

            <div className="field">
              <label htmlFor="inp-height">키 (cm)</label>
              <input
                id="inp-height"
                type="number"
                inputMode="numeric"
                placeholder="예) 170"
                value={height}
                onChange={(e) => {
                  setHeight(e.target.value);
                  setHeightErr(false);
                }}
                className={heightErr ? "err" : ""}
              />
              <div className="err-msg">키를 100–230 사이로 입력해주세요</div>
            </div>

            <div className="field">
              <label htmlFor="inp-weight">몸무게 (kg)</label>
              <input
                id="inp-weight"
                type="number"
                inputMode="numeric"
                placeholder="예) 65"
                value={weight}
                onChange={(e) => {
                  setWeight(e.target.value);
                  setWeightErr(false);
                }}
                className={weightErr ? "err" : ""}
              />
              <div className="err-msg">몸무게를 30–200 사이로 입력해주세요</div>
            </div>

            <div className="field">
              <label>성별</label>
              <div className="seg">
                {[
                  ["male", "남성"],
                  ["female", "여성"],
                  ["skip", "선택 안 할게요"],
                ].map(([val, label]) => (
                  <button
                    key={val}
                    type="button"
                    className={gender === val ? "selected" : ""}
                    onClick={() => setGender(val)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {tab === 2 && (
          <div>
            <h2 className="t-h2" style={{ margin: "0 0 4px" }}>
              사진 촬영 가이드
            </h2>
            <p className="t-body2" style={{ margin: "0 0 16px" }}>
              정확한 체형 매칭을 위해 아래 조건으로 찍어주세요.
            </p>

            <div className="photo-guide-grid">
              <div className="guide-example good">
                <img src={goodGuideImage} alt="좋은 촬영 예시" />
                <div className="guide-label good">Good</div>
              </div>
              <div className="guide-example bad">
                <img src={badGuideImage} alt="나쁜 촬영 예시" />
                <div className="guide-label bad">Bad</div>
              </div>
            </div>

            <div
              style={{
                paddingTop: 12,
                borderTop: "1px solid var(--gray-100)",
              }}
            >
              <div className="guide-row">
                <span className="mark">✓</span>
                <div className="t-body2" style={{ color: "var(--fg2)" }}>
                  몸에 붙는 옷 · 벽 앞 정면
                </div>
              </div>
              <div className="guide-row">
                <span className="mark">✓</span>
                <div className="t-body2" style={{ color: "var(--fg2)" }}>
                  전신이 모두 보이도록 멀리서
                </div>
              </div>
              <div className="guide-row">
                <span className="mark">✓</span>
                <div className="t-body2" style={{ color: "var(--fg2)" }}>
                  두 팔은 몸에서 살짝 띄워 편안하게
                </div>
              </div>
              <div className="guide-row bad">
                <span className="mark">✕</span>
                <div className="t-body2" style={{ color: "var(--fg2)" }}>
                  각도 기울임 / 다리 가림 / 어두운 조명
                </div>
              </div>
            </div>

            <div className="disclaimer" style={{ marginTop: 16 }}>
              <span className="lock">
                <svg className="ic ic-sm" viewBox="0 0 24 24">
                  <rect x="3" y="11" width="18" height="11" rx="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </span>
              사진은 분석 후 바로 삭제해요.
            </div>
          </div>
        )}

        {tab === 3 && (
          <div>
            <h2 className="t-h2" style={{ margin: "0 0 4px" }}>
              정면 전신 사진을 올려주세요
            </h2>
            <p className="t-body2" style={{ margin: "0 0 16px" }}>
              체형에 맞는 모델을 찾는 데 사용돼요.
            </p>

            <div
              className="upload-box"
              onClick={() => !photoUploaded && fileInputRef.current?.click()}
            >
              <input
                type="file"
                accept="image/jpeg,image/png"
                ref={fileInputRef}
                style={{ display: "none" }}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;

                  const isValidType =
                    file.type === "image/jpeg" || file.type === "image/png";
                  if (!isValidType) {
                    showToast("JPEG 또는 PNG 파일만 올려주세요");
                    return;
                  }

                  const isValidSize = file.size <= 10 * 1024 * 1024;
                  if (!isValidSize) {
                    showToast("10MB 이하 파일만 올려주세요");
                    return;
                  }

                  if (photoPreviewUrl) URL.revokeObjectURL(photoPreviewUrl);
                  setPhotoPreviewUrl(URL.createObjectURL(file));
                  updateSession({ image: file });
                  setPhotoUploaded(true);
                }}
              />

              {!photoUploaded ? (
                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: 10,
                  }}
                >
                  <svg
                    width="40"
                    height="40"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="var(--color-primary)"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                    <circle cx="12" cy="13" r="4" />
                  </svg>
                  <div
                    className="t-body2"
                    style={{
                      color: "var(--color-primary)",
                      fontWeight: 600,
                    }}
                  >
                    사진 올리기
                  </div>
                  <div className="t-caption">탭해서 앨범 또는 촬영</div>
                </div>
              ) : (
                <>
                  <img
                    className="upload-preview"
                    src={photoPreviewUrl}
                    alt="업로드한 체형 사진 미리보기"
                  />
                  <button
                    className="reupload"
                    onClick={(e) => {
                      e.stopPropagation();
                      setPhotoUploaded(false);
                      if (photoPreviewUrl) {
                        URL.revokeObjectURL(photoPreviewUrl);
                        setPhotoPreviewUrl("");
                      }
                      updateSession({ image: null });
                      if (fileInputRef.current) {
                        fileInputRef.current.value = "";
                      }
                    }}
                  >
                    <svg className="ic ic-sm" viewBox="0 0 24 24">
                      <path d="M1 4v6h6M23 20v-6h-6" />
                      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
                    </svg>
                    다시 올리기
                  </button>
                </>
              )}
            </div>

            <div className="disclaimer" style={{ marginTop: 16 }}>
              <span className="lock">
                <svg className="ic ic-sm" viewBox="0 0 24 24">
                  <rect x="3" y="11" width="18" height="11" rx="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
              </span>
              사진은 분석 후 바로 삭제해요.
            </div>
          </div>
        )}
      </div>

      <div className="bottombar">
        <button className="btn btn-primary" onClick={handleNext}>
          {tab === 3 ? "분석 시작할게요" : "다음으로 넘어갈게요"}
        </button>
      </div>

      <div className={`toast ${toast ? "show" : ""}`}>{toast}</div>
    </div>
  );
}
