import React, { useEffect } from "react";

const Timer = ({ totalSeconds, onTimeout }) => {
  useEffect(() => {
    const timerDisplay = document.createElement("div");
    timerDisplay.id = "interviewTimer";
    timerDisplay.style.position = "fixed";
    timerDisplay.style.top = "10px";
    timerDisplay.style.right = "10px";
    timerDisplay.style.backgroundColor = "#E52437";
    timerDisplay.style.color = "white";
    timerDisplay.style.padding = "10px 15px";
    timerDisplay.style.borderRadius = "8px";
    timerDisplay.style.zIndex = "1000";
    document.body.appendChild(timerDisplay);

    let secondsLeft = totalSeconds;
    const updateTimer = () => {
      const minutes = Math.floor(secondsLeft / 60);
      const seconds = secondsLeft % 60;
      timerDisplay.textContent = `⏱️ ${minutes}:${
        seconds < 10 ? "0" : ""
      }${seconds} remaining`;

      if (secondsLeft <= 0) {
        clearInterval(timerInterval);
        onTimeout();
      }

      secondsLeft--;
    };

    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);

    return () => {
      clearInterval(timerInterval);
      document.getElementById("interviewTimer")?.remove();
    };
  }, [totalSeconds, onTimeout]);

  return null;
};

export default Timer;
