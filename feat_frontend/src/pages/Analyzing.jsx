import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
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

export default function Analyzing() {
	const navigate = useNavigate();
	const [stepIdx, setStepIdx] = useState(0);
	const [tipIdx, setTipIdx] = useState(0);
	const [progress, setProgress] = useState(30);
	const timerRef = useRef(null);

	useEffect(() => {
		setProgress(30);
		let i = 0;
		timerRef.current = setInterval(() => {
			i++;
			if (i >= STEPS.length) {
				clearInterval(timerRef.current);
				setProgress(100);
				setTimeout(() => navigate("/result-video"), 500);
				return;
			}
			setStepIdx(i);
			setTipIdx(i % TIPS.length);
			setProgress(30 + i * 30);
		}, 2200);
		return () => clearInterval(timerRef.current);
	}, []); // eslint-disable-line react-hooks/exhaustive-deps

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
						{TIPS[tipIdx]}
					</div>
				</div>
			</div>
		</div>
	);
}
