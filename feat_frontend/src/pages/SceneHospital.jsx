import { useNavigate, useLocation } from "react-router-dom";
import "./SceneHospital.css";

export default function SceneHospital() {
	const navigate = useNavigate();
	const { state } = useLocation();

	// SymptomInput에서 navigate('/hospital', { state: { keyword } }) 로 전달
	const keyword = state?.keyword ?? "";

	return (
		<div className="page hospital-page">
			<div className="topbar">
				<button className="back" onClick={() => navigate(-1)}>
					<svg className="ic" viewBox="0 0 24 24">
						<path d="M19 12H5M12 19l-7-7 7-7" />
					</svg>
				</button>
				<div className="title">증상 확인</div>
			</div>

			<div className="content hospital-content">
				<div className="hospital-icon" aria-hidden="true">🏥</div>

				<h1 className="t-h1 hospital-heading">
					전문가 확인이 필요해 보여요
				</h1>

				{keyword && (
					<div className="hospital-keyword">
						<span>입력하신 증상</span>
						<strong>"{keyword}"</strong>
					</div>
				)}

				<p className="t-body2 hospital-desc">
					급성 부상이 의심돼요.{"\n"}
					테이핑 전에 가까운 병원이나{"\n"}
					응급실을 먼저 방문해보세요.
				</p>

				<div className="hospital-disclaimer">
					이 서비스는 예방을 위한 가이드예요.{"\n"}
					지속되는 증상은 전문가에게 확인해보세요.
				</div>
			</div>

			<div
				className="bottombar"
				style={{ display: "flex", flexDirection: "column", gap: 8 }}
			>
				<button
					className="btn btn-secondary"
					onClick={() => navigate("/consent")}
				>
					그래도 계속 진행할게요
				</button>
				<button
					className="btn btn-text"
					onClick={() => navigate("/body-part")}
				>
					처음부터 다시 해볼게요
				</button>
			</div>
		</div>
	);
}
