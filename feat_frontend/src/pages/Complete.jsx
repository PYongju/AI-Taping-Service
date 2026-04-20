import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import doneImg from "../assets/done.png";
import "./Complete.css";

const OPTIONS = {
	A: { name: "IT band 이완 테이핑", tape: "Y-strip", stretch: 15 },
	B: { name: "무릎 안정화 테이핑", tape: "I-strip", stretch: 25 },
};

export default function Complete() {
	const navigate = useNavigate();
	const { session, resetSession } = useSession();
	const optKey = session.selected_option || "A";
	const o = OPTIONS[optKey] || OPTIONS.A;
	const now = new Date();
	const time = `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;

	const [toast, setToast] = useState("");
	const timerRef = useRef(null);

	function showToast(msg) {
		setToast(msg);
		clearTimeout(timerRef.current);
		timerRef.current = setTimeout(() => setToast(""), 2000);
	}

	function handleRestart() {
		resetSession();
		navigate("/1");
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
						테이핑을 완료했어요 🎉
					</h1>
					<p
						className="t-body2"
						style={{ margin: "12px 0 0", whiteSpace: "pre-line" }}
					>
						무릎이 저리거나 피부색이 하얗게 변하면{"\n"}풀고 다시
						해주세요.
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
						<span
							className="t-body2"
							style={{ color: "var(--fg2)" }}
						>
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
						<span
							className="t-body2"
							style={{ color: "var(--fg2)" }}
						>
							테이프
						</span>
						<span
							style={{
								font: "600 14px/1 var(--font-base)",
								color: "var(--fg1)",
							}}
						>
							{o.tape} · {o.stretch}%
						</span>
					</div>
					<div
						style={{
							display: "flex",
							justifyContent: "space-between",
							alignItems: "center",
						}}
					>
						<span
							className="t-body2"
							style={{ color: "var(--fg2)" }}
						>
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
					onClick={() => showToast("결과를 저장했어요")}
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
					onClick={() => navigate("/7")}
					style={{ marginTop: 4 }}
				>
					다른 테이핑도 해볼게요
				</button>
				<button className="btn btn-text" onClick={handleRestart}>
					처음부터 다시 볼게요
				</button>
			</div>

			<div className={`toast ${toast ? "show" : ""}`}>{toast}</div>
		</div>
	);
}
