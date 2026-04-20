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
            <Route path="/1" element={<BodyPart />} />
            <Route path="/2" element={<SymptomInput />} />
            <Route path="/consent" element={<Consent />} />
            <Route path="/3" element={<BodyInfo />} />
            <Route path="/6" element={<Analyzing />} />
            <Route path="/7" element={<ResultVideo />} />
            <Route path="/9" element={<TapingGuide />} />
            <Route path="/10" element={<Complete />} />
            {/* Legacy redirects */}
            <Route path="/4" element={<Navigate to="/3" replace />} />
            <Route path="/5" element={<Navigate to="/3" replace />} />
            <Route path="/8" element={<Navigate to="/7" replace />} />
            <Route path="/11" element={<Navigate to="/" replace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
        <div className="home-ind" />
      </BrowserRouter>
    </SessionProvider>
  );
}
