import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle } from "lucide-react";
import { useSession } from "../context/SessionContext";
import Button from "../components/Button";
import "./Result3D.css";

export default function Result3D() {
	const navigate = useNavigate();
	const { session, updateSession } = useSession();
	const options = session.taping_options ?? [];
	const [selectedIdx, setSelectedIdx] = useState(session.selected_option ?? 0);
	const selected = options[selectedIdx] ?? options[0] ?? null;

	if (options.length === 0) {
		return (
			<div className="result-3d-error">
				<p className="caption">분석 데이터가 없어요.</p>
				<Button
					variant="primary"
					size="large"
					fullWidth
					onClick={() => navigate("/result-video")}
				>
					다시 분석할게요
				</Button>
			</div>
		);
	}

	function handleStart() {
		updateSession({ selected_option: selectedIdx });
		navigate("/taping-guide");
	}

	return (
		<div className="result-3d">
			<div className="result-3d-tabs">
				{options.map((opt, idx) => (
					<button
						key={opt.id}
						className={`result-3d-tab ${selectedIdx === idx ? "active" : ""}`}
						onClick={() => setSelectedIdx(idx)}
					>
						{opt.id}
					</button>
				))}
			</div>

			<div className="result-3d-viewer">
				<span className="caption">
					3D 모델 로딩 중 (호진 에셋 연결 예정)
				</span>
			</div>

			<p className="body result-3d-why">{selected?.why}</p>

			<div className="result-3d-disclaimer">
				<AlertTriangle size={16} strokeWidth={2} />
				<span>
					이 가이드는 예방적 셀프케어 목적이며 의료 진단이 아닙니다
				</span>
			</div>

			<Button
				variant="primary"
				size="large"
				fullWidth
				onClick={handleStart}
			>
				이 방법으로 시작하기
			</Button>
		</div>
	);
}
