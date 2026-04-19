import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { PersonStanding } from "lucide-react";
import styles from "./Splash.module.css";
import myLogo from "../assets/logo.png";

export default function Splash() {
	const navigate = useNavigate();

	useEffect(() => {
		if (import.meta.env.DEV) return; // 개발 환경에서는 막기

		const history = JSON.parse(localStorage.getItem("history") || "[]");

		if (history.length > 0) {
			navigate("/history", { replace: true });
		}
	}, [navigate]);

	function handleStart() {
		localStorage.setItem("visited", "true");
		navigate("/body-part");
	}

	function handleGuestStart() {
		navigate("/body-part");
	}

	return (
		<div className={styles.container}>
			<div className={styles.logoSection}>
				<span className={styles.logoLabel}>
					<img src={myLogo} alt="로고" className={styles.logoImage} />
				</span>
				<h1 className={styles.logoText}>TERRYPIQ</h1>
			</div>

			<p className={styles.headline}>
				{"이제, 나도 선수들처럼\n나만을 위한 맞춤 테이핑"}
			</p>

			<hr className={styles.divider} />

			<p className={styles.trust}>
				{"한국인 실제 체형 반영\n10,000개 빅데이터 기반"}
			</p>

			<div className={styles.spacer} />

			<div className={styles.buttonGroup}>
				<button className={styles.btnPrimary} onClick={handleStart}>
					맞춤 테이핑 시작하기
				</button>
				<button
					className={styles.btnSecondary}
					onClick={handleGuestStart}
				>
					정보 제공 없이 시작하기
				</button>
			</div>
		</div>
	);
}
