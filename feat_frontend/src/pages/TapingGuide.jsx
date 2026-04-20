import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../context/SessionContext";
import fabImg from "../assets/fab.png";
import "./TapingGuide.css";

const GUIDE_STEPS = [
	{
		title: "부위 준비",
		desc: "테이핑할 무릎 부위의 피부를 깨끗이 닦고 건조시켜주세요.",
		pose: "의자에 앉아 무릎을 90도로 구부린 자세를 유지해주세요.",
		warn: "피부에 상처나 발진이 있다면 테이핑을 멈춰주세요.",
	},
	{
		title: "앵커 고정",
		desc: "첫 번째 Y-strip의 앵커(시작점)를 무릎 위쪽에 stretch 없이 붙여주세요.",
		pose: "무릎을 살짝 구부린 상태(약 30도)로 유지해주세요.",
		warn: "앵커 부분은 절대 당기지 말고 자연스럽게 붙여주세요.",
	},
	{
		title: "본체 테이핑",
		desc: "Y-strip의 두 갈래를 무릎 바깥쪽으로 15% 당긴 채 감싸듯 붙여주세요.",
		pose: "무릎을 약 60도 구부린 자세를 유지해주세요.",
		warn: "저리거나 쥐가 나는 느낌이면 즉시 풀어주세요.",
	},
	{
		title: "마감 고정",
		desc: "반대쪽 앵커를 stretch 없이 부드럽게 마무리해주세요.",
		pose: "다시 무릎을 30도로 펴주세요.",
		warn: "끝부분이 뜨지 않도록 꾹 눌러 밀착시켜주세요.",
	},
	{
		title: "활성화",
		desc: "테이프 전체를 손바닥으로 10초간 문질러 접착력을 활성화해주세요.",
		pose: "편한 자세로 가볍게 무릎을 움직여 보세요.",
		warn: "피부색이 하얗게 변하거나 저리면 풀고 다시 해주세요.",
	},
];

const TOTAL = GUIDE_STEPS.length;

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

	const s = GUIDE_STEPS[step];

	function handlePrev() {
		if (step > 0) setStep(step - 1);
	}

	function handleNext() {
		if (step < TOTAL - 1) setStep(step + 1);
		else navigate("/complete");
	}

	function sendChatbot() {
		const text = cbInput.trim();
		if (!text) {
			setCbShake(true);
			setTimeout(() => setCbShake(false), 400);
			return;
		}
		setCbMessages((prev) => [
			...prev,
			{ role: "user", text },
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

				<div className="model-3d">
					<svg
						width="80"
						height="80"
						viewBox="0 0 24 24"
						fill="none"
						stroke="var(--fg3)"
						strokeWidth="1.5"
						strokeLinecap="round"
						strokeLinejoin="round"
					>
						<path d="M12 2l9 4v6c0 5-3.5 9.5-9 11-5.5-1.5-9-6-9-11V6l9-4z" />
						<path d="M8 12l3 3 5-6" />
					</svg>
					<div style={{ position: "relative", zIndex: 1 }}>
						🦴 3D 모델 (Three.js)
					</div>
					<div
						className="t-caption"
						style={{ position: "relative", zIndex: 1 }}
					>
						실제 구현 시 인터랙션 가능
					</div>
				</div>

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
						style={{
							color: "var(--fg2)",
							fontWeight: 600,
							marginBottom: 4,
						}}
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
			</div>

			<div className="bottombar">
				<div className="step-nav">
					<button
						className="btn btn-secondary"
						disabled={step === 0}
						onClick={handlePrev}
					>
						이전
					</button>
					<button className="btn btn-primary" onClick={handleNext}>
						{step === TOTAL - 1 ? "완료할게요" : "다음"}
					</button>
				</div>
			</div>

			{/* FAB */}
			<button
				className="fab"
				onClick={() => setChatOpen(true)}
				aria-label="챗봇 열기"
			>
				<img src={fabImg} alt="Terry chat" />
			</button>

			{/* Chatbot sheet */}
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
					<div
						style={{
							display: "flex",
							alignItems: "center",
							gap: 10,
						}}
					>
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
								style={{
									width: "100%",
									height: "100%",
									objectFit: "cover",
								}}
								alt=""
							/>
						</div>
						<div>
							<div
								style={{ font: "700 14px/1 var(--font-base)" }}
							>
								테리
							</div>
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
					{cbMessages.map((m, i) =>
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
				</div>

				<div
					style={{
						padding:
							"12px 20px calc(12px + env(safe-area-inset-bottom))",
						borderTop: "1px solid var(--gray-100)",
					}}
				>
					<div className={`chat-input ${cbShake ? "shake" : ""}`}>
						<input
							type="text"
							placeholder="메시지 입력..."
							value={cbInput}
							onChange={(e) => setCbInput(e.target.value)}
							onKeyDown={(e) =>
								e.key === "Enter" && sendChatbot()
							}
						/>
						<button className="send" onClick={sendChatbot}>
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
			</div>
		</div>
	);
}
