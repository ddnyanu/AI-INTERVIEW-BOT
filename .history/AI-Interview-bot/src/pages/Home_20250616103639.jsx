import React, { useState } from "react";
import Header from "../components/Header";
import SetupSection from "../components/SetupSection";
import InterviewSection from "../components/InterviewSection";
import ReportModal from "../components/ReportModal";

const Home = () => {
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewCompleted, setInterviewCompleted] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);

  const candidateData = {
    candidateName: "John Doe",
    organizationName: "Tech Corp",
    jobTitle: "Software Engineer",
    email: "john.doe@example.com",
  };

  const handleStartInterview = (settings) => {
    console.log("Interview settings:", settings);
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
    <div
      className="container-fluid"
      style={{ backgroundColor: "#393e46", minHeight: "100vh" }}
    >
      <Header {...candidateData} />

      {!interviewStarted ? (
        <SetupSection onStartInterview={handleStartInterview} />
      ) : (
        <InterviewSection
          onInterviewComplete={handleInterviewComplete}
          onViewReport={handleViewReport}
          onStartNewInterview={handleStartNewInterview}
        />
      )}

      <ReportModal show={showReportModal} onClose={handleCloseReport} />
    </div>
  );
};

export default Home;
