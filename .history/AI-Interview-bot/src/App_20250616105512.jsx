import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Error from "./pages/Error";
import InterviewInvitation from "./pages/InterviewInvitation";

function App() {
  return (
    <Router>
      <div className="font-sans bg-gray-100 min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/error" element={<Error />} />
          <Route path="/invitation" element={<InterviewInvitation />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
