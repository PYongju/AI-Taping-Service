import { useNavigate } from "react-router-dom";
import { Check, X, Lock } from "lucide-react";
import Button from "../components/Button";
import Card from "../components/Card";
import "./PhotoGuide.css";

export default function PhotoGuide() {
	const navigate = useNavigate();

	return (
		<div className="photo-guide">
			<div className="photo-guide-header">
				<h1 className="heading-lg">더 정확하게 매칭할게요!</h1>
				<p className="body photo-guide-subtitle">
					전신사진을 올려 도와주세요.
				</p>
			</div>

			<div className="photo-guide-content">
				<div className="photo-guide-grid">
					<Card variant="outlined" className="photo-guide-card">
						<p className="photo-guide-label good">
							<Check size={16} strokeWidth={2.5} />
							Good
						</p>
						<ul className="photo-guide-list">
							<li>전신이 들어오게</li>
							<li>몸에 붙는 옷</li>
							<li>단색 벽 앞</li>
						</ul>
					</Card>

					<Card variant="outlined" className="photo-guide-card">
						<p className="photo-guide-label bad">
							<X size={16} strokeWidth={2.5} />
							Bad
						</p>
						<ul className="photo-guide-list">
							<li>반신 촬영</li>
							<li>헐렁한 옷</li>
							<li>복잡한 배경</li>
						</ul>
					</Card>
				</div>

				<div className="photo-guide-privacy">
					<Lock size={14} strokeWidth={2} />
					<span>사진은 분석 후 즉시 삭제됩니다</span>
				</div>
			</div>

			<div className="photo-guide-footer">
				<Button
					variant="primary"
					size="large"
					fullWidth
					onClick={() => navigate("/5")}
				>
					사진 업로드
				</Button>
				<Button
					variant="secondary"
					size="large"
					fullWidth
					onClick={() => navigate("/6")}
				>
					건너뛰기
				</Button>
			</div>
		</div>
	);
}
