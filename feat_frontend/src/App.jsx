import { BrowserRouter, Routes, Route } from "react-router-dom";
import { SessionProvider } from "./context/SessionContext";

import Splash from "./pages/Splash";
import BodyPart from "./pages/BodyPart";
import SymptomInput from "./pages/SymptomInput";
import BodyInfo from "./pages/BodyInfo";
import PhotoGuide from "./pages/PhotoGuide";
import PhotoUpload from "./pages/PhotoUpload";
import Analyzing from "./pages/Analyzing";
import ResultVideo from "./pages/ResultVideo";
import Result3D from "./pages/Result3D";
import TapingGuide from "./pages/TapingGuide";
import Complete from "./pages/Complete";
import History from "./pages/History";

export default function App() {
	return (
		<SessionProvider>
			<BrowserRouter>
				<Routes>
					<Route path="/" element={<Splash />} />
					<Route path="/1" element={<BodyPart />} />
					<Route path="/2" element={<SymptomInput />} />
					<Route path="/3" element={<BodyInfo />} />
					<Route path="/4" element={<PhotoGuide />} />
					<Route path="/5" element={<PhotoUpload />} />
					<Route path="/6" element={<Analyzing />} />
					<Route path="/7" element={<ResultVideo />} />
					<Route path="/8" element={<Result3D />} />
					<Route path="/9" element={<TapingGuide />} />
					<Route path="/10" element={<Complete />} />
					<Route path="/11" element={<History />} />
				</Routes>
			</BrowserRouter>
		</SessionProvider>
	);
}
