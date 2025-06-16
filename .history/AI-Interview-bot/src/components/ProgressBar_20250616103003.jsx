import React from "react";

const ProgressBar = ({ progress }) => {
  return (
    <div className="progress-container">
      <div className="progress-text" id="progressTextDisplay">
        {Math.round(progress)}% Complete
      </div>
      <div className="progress">
        <div
          id="progressBar"
          className="progress-bar bg-success"
          role="progressbar"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
    </div>
  );
};

export default ProgressBar;
