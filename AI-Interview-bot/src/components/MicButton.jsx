// import React from "react";

// const MicButton = ({ isRecording, onClick }) => {
//   return (
//     <button
//       id="micButton"
//       className={`mic-button ${isRecording ? "recording" : ""}`}
//       onClick={onClick}
//     >
//       <i
//         className={`fas ${
//           isRecording ? "fa-microphone-slash" : "fa-microphone"
//         }`}
//       ></i>
//     </button>
//   );
// };

// export default MicButton;
import React from "react";

function MicButton({ isRecording, onStart, onStop, disabled = false }) {
  const handleClick = () => {
    if (disabled) return;
    isRecording ? onStop() : onStart();
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className={`w-20 h-20 rounded-full flex items-center justify-center transition-all
        ${
          isRecording
            ? "bg-red-600 animate-pulse shadow-lg shadow-red-600/30"
            : "bg-gray-700 hover:bg-gray-600"
        }
        ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
      `}
    >
      {isRecording ? (
        <span className="text-white text-2xl">■</span>
      ) : (
        <span className="text-white text-2xl">🎤</span>
      )}
    </button>
  );
}

export default MicButton;
