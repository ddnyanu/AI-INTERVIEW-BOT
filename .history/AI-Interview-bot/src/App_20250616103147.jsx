import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Error from "./pages/Error";
import InterviewInvitation from "./pages/InterviewInvitation";
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/error" element={<Error />} />
        <Route path="/invitation" element={<InterviewInvitation />} />
      </Routes>
    </Router>
  );
}

export default App;
