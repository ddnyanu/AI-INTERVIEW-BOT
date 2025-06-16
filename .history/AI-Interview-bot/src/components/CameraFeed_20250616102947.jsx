import React, { useEffect, useRef } from "react";

const CameraFeed = () => {
  const videoRef = useRef(null);

  useEffect(() => {
    let mediaStream = null;

    const initCamera = async () => {
      try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 640 },
            height: { ideal: 480 },
            facingMode: "user",
          },
          audio: false,
        });

        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (err) {
        console.error("Error accessing camera:", err);
      }
    };

    initCamera();

    return () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  return (
    <div className="camera-container">
      <video
        ref={videoRef}
        className="camera-feed"
        autoPlay
        playsInline
      ></video>
    </div>
  );
};

export default CameraFeed;
