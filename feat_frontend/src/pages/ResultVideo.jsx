import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import "./ResultVideo.css";

const OPTIONS = {
	A: {
		name: "IT band 이완 테이핑",
		tape: "Y-strip",
		stretch: 15,
		why: "러닝 후 외측 긴장에 가장 일반적인 예방 테이핑이에요.",
		coach: "💡 테이핑 전 부위를 깨끗이 닦고, 털이 있다면 면도 후 붙여주세요.",
	},
	B: {
		name: "무릎 안정화 테이핑",
		tape: "I-strip",
		stretch: 25,
		why: "무릎 전반적 안정감 보강에 도움이 될 수 있어요.",
		coach: "💡 stretch 25%는 조금 당긴 상태로 붙이는 거예요.",
	},
};

export default function ResultVideo() {
	const navigate = useNavigate();
	const { updateSession } = useSession();
	const [opt, setOpt] = useState("A");

	const o = OPTIONS[opt];

	function startGuide() {
		updateSession({ selected_option: opt });
		navigate("/result-3d");
	}

	return (
		<div className="page">
			<div className="topbar">
				<button className="back" onClick={() => navigate("/analyzing")}>
					<svg className="ic" viewBox="0 0 24 24">
						<path d="M19 12H5M12 19l-7-7 7-7" />
					</svg>
				</button>
				<div className="title">추천 결과</div>
			</div>

			<div
				className="content"
				style={{
					padding: "20px 20px 24px",
					display: "flex",
					flexDirection: "column",
					gap: 16,
				}}
			>
				<div>
					<div
						style={{
							font: "500 12px/1 var(--font-base)",
							color: "var(--color-primary)",
							marginBottom: 6,
						}}
					>
						체형에 맞는 모델을 찾았어요
					</div>
					<h2 className="t-h1" style={{ margin: 0 }}>
						IT band 긴장 가능성이 있어요
					</h2>
					<p className="t-body2" style={{ margin: "8px 0 0" }}>
						아래 두 가지 방법이 도움이 될 수 있어요.
					</p>
				</div>

				<div className="opt-switch">
					<button
						className={opt === "A" ? "active" : ""}
						onClick={() => setOpt("A")}
					>
						<span className="star">★</span> 추천 A
					</button>
					<button
						className={opt === "B" ? "active" : ""}
						onClick={() => setOpt("B")}
					>
						옵션 B
					</button>
				</div>

				<div className="card selected">
					{opt === "A" && (
						<div className="badge-rec" style={{ marginBottom: 8 }}>
							많이 선택해요
						</div>
					)}
					<div
						style={{
							font: "700 17px/1.3 var(--font-base)",
							color: "var(--fg1)",
						}}
					>
						{o.name}
					</div>
					<div
						style={{
							display: "flex",
							gap: 10,
							margin: "12px 0",
							flexWrap: "wrap",
						}}
					>
						<span
							style={{
								padding: "6px 10px",
								background: "var(--bg3)",
								borderRadius: "var(--radius-full)",
								font: "600 12px/1 var(--font-base)",
								color: "var(--fg2)",
							}}
						>
							테이프:{" "}
							<span style={{ color: "var(--fg1)" }}>
								{o.tape}
							</span>
						</span>
						<span
							style={{
								padding: "6px 10px",
								background: "var(--bg3)",
								borderRadius: "var(--radius-full)",
								font: "600 12px/1 var(--font-base)",
								color: "var(--fg2)",
							}}
						>
							stretch:{" "}
							<span style={{ color: "var(--fg1)" }}>
								{o.stretch}%
							</span>
						</span>
					</div>
					<div
						style={{
							font: "400 13px/1.55 var(--font-base)",
							color: "var(--fg2)",
						}}
					>
						{o.why}
					</div>
				</div>

				<div className="video-placeholder">
					<svg
						className="ic ic-lg"
						viewBox="0 0 24 24"
						style={{ stroke: "var(--fg3)" }}
					>
						<polygon
							points="5 3 19 12 5 21 5 3"
							fill="var(--fg3)"
						/>
					</svg>
					테이핑 시연 영상
				</div>

				<div className="disclaimer">
					<span className="lock">
						<svg className="ic ic-sm" viewBox="0 0 24 24">
							<path d="M12 9v4M12 17h.01" />
							<circle cx="12" cy="12" r="10" />
						</svg>
					</span>
					이 서비스는 예방을 위한 가이드예요. 지속되는 증상은
					전문가에게 확인해보세요.
				</div>

				<div
					className="t-body2"
					style={{
						padding: "12px 14px",
						background: "#fff7ed",
						borderRadius: "var(--radius-md)",
						color: "#9a3412",
						fontWeight: 500,
					}}
				>
					{o.coach}
				</div>
			</div>

			<div className="bottombar">
				<button className="btn btn-primary" onClick={startGuide}>
					이 방법으로 시작할게요
				</button>
			</div>
		</div>
	);
}
