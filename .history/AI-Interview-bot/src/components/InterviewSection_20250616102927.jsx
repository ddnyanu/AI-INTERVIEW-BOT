import React, { useState, useEffect } from "react";
import CameraFeed from "./CameraFeed";
import MicButton from "./MicButton";
import ProgressBar from "./ProgressBar";
import Timer from "./Timer";

const InterviewSection = ({
  onInterviewComplete,
  onViewReport,
  onStartNewInterview,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [interviewInProgress, setInterviewInProgress] = useState(true);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [currentQuestionNum, setCurrentQuestionNum] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(10);
  const [progress, setProgress] = useState(0);
  const [showCompleteMessage, setShowCompleteMessage] = useState(false);

  // This would be replaced with actual API calls
  const askQuestion = () => {
    // Simulate API call to get question
    setTimeout(() => {
      if (currentQuestionNum < totalQuestions) {
        setCurrentQuestionNum((prev) => prev + 1);
        setProgress((currentQuestionNum / totalQuestions) * 100);
      } else {
        setInterviewInProgress(false);
        setShowCompleteMessage(true);
        onInterviewComplete();
      }
    }, 2000);
  };

  const startRecording = () => {
    setIsRecording(true);
    // Start speech recognition here
  };

  const stopRecording = () => {
    setIsRecording(false);
    // Stop speech recognition here
  };

  const processAnswer = () => {
    // Process the answer and move to next question
    askQuestion();
    setCurrentAnswer("");
  };

  return (
    <div className="row interview-section">
      <div className="col-md-8 offset-md-2">
        <div className="card">
          <div className="card-header d-flex justify-content-between align-items-center">
            <h3>Voice Interview</h3>
            <div id="progressText">
              Question <span id="currentQuestionNum">{currentQuestionNum}</span>{" "}
              of <span id="totalQuestions">{totalQuestions}</span>
            </div>
          </div>
          <div className="card-body">
            <div className="interview-container">
              <CameraFeed />

              <div className="d-flex justify-content-center mb-3">
                <MicButton
                  isRecording={isRecording}
                  onClick={() =>
                    isRecording ? stopRecording() : startRecording()
                  }
                />
              </div>

              <ProgressBar progress={progress} />

              {showCompleteMessage && (
                <div
                  id="interviewCompleteMessage"
                  className="interview-complete-message"
                >
                  Interview completed! Thank you for participating.
                  <button
                    id="viewReportBtn"
                    className="btn btn-outline-success btn-sm ms-3"
                    onClick={onViewReport}
                  >
                    <i className="fas fa-chart-bar"></i> View Performance Report
                  </button>
                </div>
              )}
            </div>

            <div
              id="answerPreview"
              className="answer-preview mt-3 p-2 bg-light rounded"
              style={{ minHeight: "60px", fontStyle: "italic" }}
            >
              {currentAnswer}
            </div>
          </div>
        </div>
      </div>

      <button
        id="startNewInterviewBtn"
        className="start-new-btn"
        style={{ display: showCompleteMessage ? "block" : "none" }}
        onClick={onStartNewInterview}
      >
        <i className="fas fa-redo"></i> Start New Interview
      </button>

      {interviewInProgress && (
        <Timer
          totalSeconds={1800}
          onTimeout={() => {
            setInterviewInProgress(false);
            setShowCompleteMessage(true);
            onInterviewComplete();
          }}
        />
      )}
    </div>
  );
};

export default InterviewSection;
