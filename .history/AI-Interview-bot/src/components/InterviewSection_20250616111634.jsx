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

// import React, { useState, useEffect } from "react";
// import { processMockAnswer, downloadMockReport } from "../api/InterviewService";
// import CameraFeed from "./CameraFeed";
// import MicButton from "./MicButton";

// function InterviewSection({ interviewData, onComplete, mockMode = false }) {
//   const [currentQuestion, setCurrentQuestion] = useState(0);
//   const [isRecording, setIsRecording] = useState(false);
//   const [answer, setAnswer] = useState("");
//   const [status, setStatus] = useState("starting");

//   // Mock interview flow
//   useEffect(() => {
//     setStatus("in_progress");
//   }, []);

//   const completeInterview = async () => {
//     setStatus("completed");
//     if (mockMode) {
//       downloadMockReport(); // Use mock download
//     } else {
//       // This would be your real download function
//       // downloadReport(interviewData.report_id)
//     }
//     onComplete();
//   };

//   const handleRecordingComplete = async () => {
//     setIsRecording(false);
//     setStatus("processing");

//     try {
//       // Use mock processing in mock mode
//       if (mockMode) {
//         await processMockAnswer(answer);
//       } else {
//         // await processAnswer(answer, 'frame_data_here')
//       }

//       setAnswer("");

//       // Move to next question or complete
//       if (currentQuestion + 1 < interviewData.questions.length) {
//         setCurrentQuestion((prev) => prev + 1);
//         setStatus("in_progress");
//       } else {
//         completeInterview();
//       }
//     } catch (error) {
//       setStatus("error");
//     }
//   };

//   // Mock speech recognition
//   const mockSpeechRecognition = () => {
//     if (!isRecording) return;

//     const mockResponses = [
//       "I have 3 years of experience with React",
//       "I use Redux for state management",
//       "I prefer Jest and React Testing Library",
//     ];

//     let i = 0;
//     const interval = setInterval(() => {
//       if (i < mockResponses[currentQuestion].length) {
//         setAnswer((prev) => prev + mockResponses[currentQuestion][i]);
//         i++;
//       } else {
//         clearInterval(interval);
//         handleRecordingComplete();
//       }
//     }, 50);

//     return () => clearInterval(interval);
//   };

//   useEffect(() => {
//     if (mockMode && isRecording) {
//       return mockSpeechRecognition();
//     }
//   }, [isRecording, mockMode, currentQuestion]);

//   return (
//     <div className="max-w-2xl mx-auto bg-gray-800 rounded-xl p-6">
//       {status === "starting" && <div>Preparing interview...</div>}
//       {status === "loading" && <div>Loading question...</div>}
//       {status === "error" && <div className="text-red-500">Error occurred</div>}

//       {status === "in_progress" && (
//         <>
//           <div className="text-center mb-6">
//             <h3 className="text-lg font-medium">
//               Question {currentQuestion + 1} of {interviewData.questions.length}
//             </h3>
//             <p className="mt-2">
//               {interviewData.questions[currentQuestion]?.text}
//             </p>
//             {mockMode && (
//               <p className="text-sm text-yellow-400 mt-2">
//                 Mock mode: Click mic to simulate answer
//               </p>
//             )}
//           </div>

//           {mockMode ? (
//             <div className="bg-black rounded-lg w-full h-48 flex items-center justify-center mb-4">
//               <p className="text-gray-500">[Mock Camera Feed]</p>
//             </div>
//           ) : (
//             <CameraFeed />
//           )}

//           <div className="mt-6 flex flex-col items-center">
//             <MicButton
//               isRecording={isRecording}
//               onStart={() => setIsRecording(true)}
//               onStop={handleRecordingComplete}
//               disabled={status !== "in_progress"}
//             />

//             <div className="mt-4 w-full bg-gray-700 p-4 rounded-lg min-h-20">
//               {answer || (
//                 <span className="text-gray-400">
//                   Your answer will appear here...
//                 </span>
//               )}
//             </div>
//           </div>
//         </>
//       )}

//       {status === "completed" && (
//         <div className="text-center py-10">
//           <h3 className="text-xl font-bold mb-4">Interview Completed!</h3>
//           <p className="mb-4">
//             {mockMode
//               ? "Mock report downloaded (check your downloads)"
//               : "Your report has been downloaded"}
//           </p>
//           <button
//             onClick={() => window.location.reload()}
//             className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded"
//           >
//             Restart Interview
//           </button>
//         </div>
//       )}
//     </div>
//   );
// }

// export default InterviewSection;
