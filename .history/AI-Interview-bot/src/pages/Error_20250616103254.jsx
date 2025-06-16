import React from "react";
import { Link } from "react-router-dom";

const Error = ({ message = "Something went wrong" }) => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-fef3f2 text-b91c1c">
      <div className="bg-fff0f0 p-8 border border-fca5a5 rounded-lg shadow-lg text-center">
        <h1 className="text-4xl mb-4">⚠️ Error</h1>
        <p className="text-xl mb-6">{message}</p>
        <Link to="/" className="text-991b1b hover:underline">
          🔙 Back to Home
        </Link>
      </div>
    </div>
  );
};

export default Error;
