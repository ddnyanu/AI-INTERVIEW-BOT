import React from "react";

const MicButton = ({ isRecording, onClick }) => {
  return (
    <button
      id="micButton"
      className={`mic-button ${isRecording ? "recording" : ""}`}
      onClick={onClick}
    >
      <i
        className={`fas ${
          isRecording ? "fa-microphone-slash" : "fa-microphone"
        }`}
      ></i>
    </button>
  );
};

export default MicButton;
