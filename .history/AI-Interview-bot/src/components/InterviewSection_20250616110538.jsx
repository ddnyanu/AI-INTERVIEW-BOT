import React, { useState, useEffect } from "react";
import { processAnswer, downloadReport } from "../api/interviewService";
import CameraFeed from "./CameraFeed";
import MicButton from "./MicButton";

function InterviewSection({ interviewData, onComplete }) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("starting");

  // Start interview when component mounts
  useEffect(() => {
    const start = async () => {
      try {
        setStatus("loading");
        // Get first question from backend
        await loadNextQuestion();
        setStatus("in_progress");
      } catch (error) {
        setStatus("error");
      }
    };
    start();
  }, []);

  const loadNextQuestion = async () => {
    // In a real app, this would come from backend
    const nextQuestion = interviewData.questions[currentQuestion];
    if (!nextQuestion) {
      completeInterview();
      return;
    }
    // Play question audio (implementation depends on your backend)
    playQuestionAudio(nextQuestion.audio);
  };

  const completeInterview = async () => {
    setStatus("completed");
    // Automatically download report
    downloadReport(interviewData.report_id);
    onComplete();
  };

  const handleRecordingComplete = async () => {
    setIsRecording(false);
    setStatus("processing");

    try {
      await processAnswer(answer, "frame_data_here");
      setAnswer("");
      setCurrentQuestion((prev) => prev + 1);
      await loadNextQuestion();
      setStatus("in_progress");
    } catch (error) {
      setStatus("error");
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-gray-800 rounded-xl p-6">
      {status === "loading" && <div>Loading interview...</div>}
      {status === "error" && <div className="text-red-500">Error occurred</div>}

      {status === "in_progress" && (
        <>
          <div className="text-center mb-6">
            <h3 className="text-lg font-medium">
              Question {currentQuestion + 1} of {interviewData.questions.length}
            </h3>
            <p className="mt-2">
              {interviewData.questions[currentQuestion]?.text}
            </p>
          </div>

          <CameraFeed />

          <div className="mt-6 flex flex-col items-center">
            <MicButton
              isRecording={isRecording}
              onStart={() => setIsRecording(true)}
              onStop={handleRecordingComplete}
            />

            <div className="mt-4 w-full bg-gray-700 p-4 rounded-lg min-h-20">
              {answer || (
                <span className="text-gray-400">
                  Your answer will appear here...
                </span>
              )}
            </div>
          </div>
        </>
      )}

      {status === "completed" && (
        <div className="text-center py-10">
          <h3 className="text-xl font-bold mb-4">Interview Completed!</h3>
          <p>Your report has been downloaded automatically.</p>
        </div>
      )}
    </div>
  );
}

export default InterviewSection;
