import { useNavigate } from "react-router-dom";
import myLogo from "../assets/logo.png";
import "./Splash.css";

export default function Splash() {
	const navigate = useNavigate();

	return (
		<div className="page splash-page">
			<div className="content splash-content">
				<img src={myLogo} alt="TerryPiQ" className="splash-logo" />
				<div className="splash-brand">TERRYPIQ</div>
				<h1 className="t-h1 splash-headline">
					이제, 나도 선수들처럼{"\n"}나만을 위한 맞춤 테이핑
				</h1>
				<div className="splash-badge">
					<svg className="ic ic-sm" viewBox="0 0 24 24">
						<path d="M12 2L3 7v5c0 5.5 3.84 10.74 9 12 5.16-1.26 9-6.5 9-12V7l-9-5z" />
					</svg>
					AI Hub · 한국인 실제 체형 데이터 기반
				</div>
			</div>
			<div className="bottombar">
				<button
					className="btn btn-primary"
					onClick={() => navigate("/body-part")}
				>
					맞춤 테이핑 시작할게요
				</button>
			</div>
		</div>
	);
}
