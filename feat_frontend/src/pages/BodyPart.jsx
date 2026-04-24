import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import "./BodyPart.css";

const PARTS = [
	{ label: "무릎", available: true },
	{ label: "발목", available: false },
	{ label: "어깨", available: false },
	{ label: "허리", available: false },
	{ label: "팔꿈치", available: false },
	{ label: "손목", available: false },
];

export default function BodyPart() {
	const navigate = useNavigate();
	const { updateSession } = useSession();
	const [toast, setToast] = useState("");
	const [toastTimer, setToastTimer] = useState(null);

	function showToast(msg) {
		setToast(msg);
		if (toastTimer) clearTimeout(toastTimer);
		const t = setTimeout(() => setToast(""), 2000);
		setToastTimer(t);
	}

	function pickPart(part) {
		if (!part.available) {
			showToast("지금은 무릎만 쓸 수 있어요");
			return;
		}
		updateSession({ part: part.label });
	}

	function handleNext() {
		updateSession({ part: "무릎" });
		navigate("/symptom-input");
	}

	return (
		<div className="page">
			<div className="topbar">
				<button className="back" onClick={() => navigate("/")}>
					<svg className="ic" viewBox="0 0 24 24">
						<path d="M19 12H5M12 19l-7-7 7-7" />
					</svg>
				</button>
				<div className="title">증상 입력</div>
			</div>

			<div className="content chat-pane">
				<div className="bubble-bot">어디가 불편하세요?</div>
				<div className="part-grid">
					{PARTS.map((part) => (
						<button
							key={part.label}
							className={`chip ${part.available ? "selected" : "locked"}`}
							onClick={() => pickPart(part)}
							style={{ justifyContent: "center" }}
						>
							{part.label}
							{part.available ? (
								<span style={{ color: "var(--color-success)" }}>
									✓
								</span>
							) : (
								<span>🔒</span>
							)}
						</button>
					))}
				</div>
			</div>

			<div
				className="bottombar"
				style={{ display: "flex", flexDirection: "column", gap: 8 }}
			>
				<button className="btn btn-primary" onClick={handleNext}>
					다음으로 넘어갈게요
				</button>
			</div>

			<div className={`toast ${toast ? "show" : ""}`}>{toast}</div>
		</div>
	);
}
