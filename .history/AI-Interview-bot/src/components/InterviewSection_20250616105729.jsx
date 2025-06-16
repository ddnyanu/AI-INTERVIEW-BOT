import React, { useState, useEffect, useRef } from "react";
import { getQuestion, processAnswer } from "../api/interviewService";
import CameraFeed from "./CameraFeed";
import MicButton from "./MicButton";
import ProgressBar from "./ProgressBar";
import Timer from "./Timer";

function InterviewSection({
  interviewSettings,
  onInterviewComplete,
  onViewReport,
  onStartNewInterview,
}) {
  // Interview state
  const [isRecording, setIsRecording] = useState(false);
  const [interviewInProgress, setInterviewInProgress] = useState(true);
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [currentQuestionNum, setCurrentQuestionNum] = useState(1);
  const [totalQuestions, setTotalQuestions] = useState(0);
  const [progress, setProgress] = useState(0);
  const [showCompleteMessage, setShowCompleteMessage] = useState(false);
  const videoRef = useRef(null);

  // Initialize interview
  useEffect(() => {
    const initInterview = async () => {
      try {
        // In a real app, you would call your startInterview API here
        // For now, we'll mock the response
        setTotalQuestions(5); // Mock total questions
        askQuestion();
      } catch (error) {
        console.error("Failed to start interview:", error);
      }
    };

    initInterview();
  }, []);

  // Handle getting the next question
  const askQuestion = async () => {
    if (!interviewInProgress) return;

    try {
      // Mock API call - replace with actual implementation
      const response = await getQuestion();

      if (response.status === "completed") {
        interviewComplete();
      } else if (response.status === "success") {
        setCurrentQuestionNum(response.question_number);
        updateProgress(response.question_number - 1, response.total_questions);

        // Auto-start recording if enabled
        if (interviewSettings.autoStartRecording) {
          startRecording();
        }
      }
    } catch (error) {
      console.error("Error getting question:", error);
    }
  };

  // Handle answer submission
  const submitAnswer = async () => {
    if (!currentAnswer.trim()) return;

    try {
      // Mock API call - replace with actual implementation
      const response = await processAnswer(currentAnswer.trim(), "frameData");

      if (response.status === "answer_processed") {
        setCurrentAnswer("");
        updateProgress(response.current_question, response.total_questions);

        if (response.interview_complete) {
          interviewComplete();
        } else {
          setTimeout(askQuestion, 1000);
        }
      }
    } catch (error) {
      console.error("Error processing answer:", error);
    }
  };

  // Update progress indicator
  const updateProgress = (current, total) => {
    const percent = Math.round((current / total) * 100);
    setProgress(percent);
  };

  // Handle interview completion
  const interviewComplete = () => {
    setInterviewInProgress(false);
    setShowCompleteMessage(true);
    onInterviewComplete();
  };

  // Start/stop recording
  const startRecording = () => {
    setIsRecording(true);
    // Implement speech recognition start
  };

  const stopRecording = () => {
    setIsRecording(false);
    // Implement speech recognition stop
    submitAnswer();
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-xl overflow-hidden">
        {/* Interview Header */}
        <div className="bg-gray-800 text-amber-100 px-6 py-4 flex justify-between items-center">
          <h2 className="text-xl font-bold">Voice Interview</h2>
          <div className="flex items-center space-x-4">
            <span className="text-sm bg-gray-700 px-3 py-1 rounded-full">
              Question {currentQuestionNum} of {totalQuestions}
            </span>
            <Timer totalSeconds={1800} onTimeout={interviewComplete} />
          </div>
        </div>

        {/* Interview Body */}
        <div className="p-6">
          <div className="flex flex-col items-center">
            {/* Camera Feed */}
            <div className="mb-8 w-full max-w-md">
              <CameraFeed ref={videoRef} />
            </div>

            {/* Microphone Button */}
            <div className="mb-8">
              <MicButton
                isRecording={isRecording}
                onClick={() =>
                  isRecording ? stopRecording() : startRecording()
                }
              />
            </div>

            {/* Progress Bar */}
            <div className="w-full mb-8">
              <ProgressBar progress={progress} />
            </div>

            {/* Answer Preview */}
            <div className="w-full bg-gray-50 p-4 rounded-lg mb-6 min-h-20 border border-gray-200">
              {currentAnswer || (
                <p className="text-gray-400 italic">
                  Your answer will appear here as you speak...
                </p>
              )}
            </div>

            {/* Completion Message */}
            {showCompleteMessage && (
              <div className="bg-green-50 text-green-800 p-4 rounded-lg w-full text-center mb-6">
                <p className="font-medium">
                  Interview completed! Thank you for participating.
                </p>
                <button
                  onClick={onViewReport}
                  className="mt-3 bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition duration-300 inline-flex items-center"
                >
                  <svg
                    className="w-4 h-4 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  View Performance Report
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Start New Interview Button */}
      {showCompleteMessage && (
        <button
          onClick={onStartNewInterview}
          className="fixed bottom-6 left-6 bg-gray-800 hover:bg-gray-700 text-amber-100 font-medium py-3 px-5 rounded-full shadow-lg transition duration-300 flex items-center z-50"
        >
          <svg
            className="w-5 h-5 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          Start New Interview
        </button>
      )}
    </div>
  );
}

export default InterviewSection;
