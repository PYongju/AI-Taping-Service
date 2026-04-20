import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SessionProvider } from "./context/SessionContext";
import "./App.css";

import Splash from "./pages/Splash";
import BodyPart from "./pages/BodyPart";
import SymptomInput from "./pages/SymptomInput";
import Consent from "./pages/Consent";
import BodyInfo from "./pages/BodyInfo";
import Analyzing from "./pages/Analyzing";
import ResultVideo from "./pages/ResultVideo";
import TapingGuide from "./pages/TapingGuide";
import Complete from "./pages/Complete";

export default function App() {
	return (
		<SessionProvider>
			<BrowserRouter>
				<div className="scene-wrap">
					<Routes>
						<Route path="/" element={<Splash />} />
						<Route path="/body-part" element={<BodyPart />} />
						<Route
							path="/symptom-input"
							element={<SymptomInput />}
						/>
						<Route path="/consent" element={<Consent />} />
						<Route path="/body-info" element={<BodyInfo />} />
						<Route path="/analyzing" element={<Analyzing />} />
						<Route path="/result-video" element={<ResultVideo />} />
						<Route path="/result-3d" element={<TapingGuide />} />
						<Route path="/complete" element={<Complete />} />
						{/* Legacy redirects
						<Route
							path="/4"
							element={<Navigate to="/3" replace />}
						/>
						<Route
							path="/5"
							element={<Navigate to="/3" replace />}
						/>
						<Route
							path="/8"
							element={<Navigate to="/7" replace />}
						/>
						<Route
							path="/11"
							element={<Navigate to="/" replace />}
						/> */}
						<Route path="*" element={<Navigate to="/" replace />} />
					</Routes>
				</div>
				<div className="home-ind" />
			</BrowserRouter>
		</SessionProvider>
	);
}
