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
		tape_type: option.tape_type ?? "Guide",
		stretch_pct: option.stretch_pct ?? 0,
		why: option.why ?? option.description ?? "추천된 테이핑 방식입니다.",
		coach: option.coach ?? option.description ?? "안내에 따라 천천히 진행해주세요.",
		steps: option.steps ?? [],
		step_glb_urls: option.step_glb_urls ?? [],
		model_url: option.model_url ?? ep3.model_url ?? "",
		video_url: option.video_url ?? ep3.video_url ?? "",
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
	}, []); // eslint-disable-line react-hooks/exhaustive-deps

	async function runAnalysis() {
		if (inFlightRef.current) return;
		inFlightRef.current = true;
		setApiError(null);
		setStepIdx(0);
		setProgress(30);
		try {
			let model_id = null;
			let session_id = session.session_id;
			if (session.body_info_mode === "full") {
				const formData = new FormData();
				formData.append("session_id", session_id ?? "");
				if (session.image) {
					formData.append("image", session.image);
				}
				formData.append("privacy_opt_out", "false");
				if (session.gender && session.gender !== "skip") {
					formData.append("gender", session.gender);
				}
				const ep2 = await matchBody(formData);
				model_id = ep2.model_id ?? null;
				session_id = ep2.session_id ?? session_id;
				updateSession({
					model_id,
					session_id,
				});
			}

			setStepIdx(1);
			setProgress(60);

			const ep3 = await getTapingRecommend({
				session_id,
				model_id,
				privacy_opt_out: session.body_info_mode !== "full",
			});

			const options = ep3.options?.map((option, idx) =>
				normalizeOption(option, idx, ep3),
			);

			if (!options || options.length === 0) {
				setApiError("추천 결과를 받지 못했어요. 다시 시도해주세요.");
				return;
			}
			// RAI: disclaimer 필드 없으면 화면 표시 금지
			if (options.some((o) => !o.disclaimer)) {
				setApiError("안전 안내 정보가 누락됐어요. 다시 시도해주세요.");
				return;
			}

			setStepIdx(2);
			setProgress(100);
			updateSession({
				session_id: ep3.session_id ?? session_id,
				taping_options: options,
				model_url: ep3.model_url ?? "",
				video_url: ep3.video_url ?? "",
				registry_key: ep3.registry_key ?? options[0]?.registry_key ?? "",
			});
			setTimeout(() => navigate("/result-video"), 500);
		} catch {
			setApiError("분석 중 오류가 발생했어요. 다시 시도해주세요.");
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
								<div
									className="fill"
									style={{ width: `${progress}%` }}
								/>
							</div>
						</div>

						<div
							className="tip-card"
							style={{ width: "100%", marginTop: 8 }}
						>
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
