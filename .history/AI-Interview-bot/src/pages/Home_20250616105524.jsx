import React, { useState } from "react";
import Header from "../components/Header";
import SetupSection from "../components/SetupSection";
import InterviewSection from "../components/InterviewSection";
import ReportModal from "../components/ReportModal";

function Home() {
  // State management for interview flow
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewCompleted, setInterviewCompleted] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [interviewSettings, setInterviewSettings] = useState({
    role: "Software Engineer",
    experienceLevel: "fresher",
    yearsExperience: 0,
    resumeText: "",
    jdText: "",
    autoStartRecording: true,
  });

  // Mock candidate data - replace with actual API call
  const candidateData = {
    candidateName: "John Doe",
    organizationName: "Tech Corp",
    jobTitle: "Software Engineer",
    email: "john.doe@example.com",
  };

  // Handler functions
  const handleStartInterview = (settings) => {
    setInterviewSettings((prev) => ({ ...prev, ...settings }));
    setInterviewStarted(true);
  };

  const handleInterviewComplete = () => {
    setInterviewCompleted(true);
  };

  const handleViewReport = () => {
    setShowReportModal(true);
  };

  const handleStartNewInterview = () => {
    setInterviewStarted(false);
    setInterviewCompleted(false);
  };

  const handleCloseReport = () => {
    setShowReportModal(false);
  };

  return (
    <div className="bg-gray-900 min-h-screen text-gray-100">
      {/* Application Header */}
      <Header {...candidateData} />

      {/* Main Content Area */}
      <main className="container mx-auto px-4 py-8">
        {!interviewStarted ? (
          // Setup Phase
          <SetupSection onStartInterview={handleStartInterview} />
        ) : (
          // Interview Phase
          <InterviewSection
            interviewSettings={interviewSettings}
            onInterviewComplete={handleInterviewComplete}
            onViewReport={handleViewReport}
            onStartNewInterview={handleStartNewInterview}
          />
        )}
      </main>

      {/* Report Modal */}
      <ReportModal show={showReportModal} onClose={handleCloseReport} />
    </div>
  );
}

export default Home;
