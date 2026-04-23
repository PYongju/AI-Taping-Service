import { useNavigate, useLocation } from "react-router-dom";
import careImage from "../assets/care.png";
import "./SceneHospital.css";

const RICE_ITEMS = [
	{ icon: "🛌", key: "Rest", label: "무리하지 말고 쉬어주세요" },
	{ icon: "🧊", key: "Ice", label: "얼음으로 찜질해주세요" },
	{ icon: "💎", key: "Comp.", label: "가볍게 압박해주세요" },
	{ icon: "🦵", key: "Elev.", label: "다친 부위를 심장보다 높게 올려주세요" },
];

export default function SceneHospital() {
	const navigate = useNavigate();
	const { state } = useLocation();

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
				<img
					className="hospital-care-img"
					src={careImage}
					alt=""
					aria-hidden="true"
				/>

				<h1 className="t-h1 hospital-heading">
					지금 테이핑보다 먼저
					<br />
					할 일이 있어요
				</h1>

				{keyword && (
					<div className="hospital-keyword">
						<span>입력하신 증상</span>
						<strong>"{keyword}"</strong>
					</div>
				)}

				<section className="rice-card" aria-label="RICE 응급 처치 안내">
					<div className="rice-title">응급처치 가이드</div>
					{RICE_ITEMS.map((item) => (
						<div className="rice-row" key={item.key}>
							<span className="rice-icon">{item.icon}</span>
							<span className="rice-key">{item.key}</span>
							<span className="rice-dash">-</span>
							<span className="rice-label">{item.label}</span>
						</div>
					))}
				</section>

				<p className="t-body2 hospital-desc">
					먼저 병원에서 확인해보시는 걸 꼭 권해드려요.
				</p>
				<p className="hospital-sub">괜찮아지면 언제든지 다시 찾아오세요!</p>
				<p className="hospital-note">ⓘ 이 안내는 의료진단이 아니에요.</p>
			</div>

			<div className="bottombar hospital-actions">
				<button className="btn btn-primary" onClick={() => navigate("/")}>
					나중에 다시 올게요
				</button>
				<button className="btn btn-secondary" onClick={() => navigate("/consent")}>
					그래도 계속 진행할게요
				</button>
			</div>
		</div>
	);
}
