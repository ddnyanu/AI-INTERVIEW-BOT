import React from "react";
import { Link } from "react-router-dom";

function Error({ message = "Something went wrong. Please try again." }) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-red-50">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-lg text-center">
        <div className="text-red-500 mb-6">
          <svg
            className="w-16 h-16 mx-auto"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          Oops! Error Occurred
        </h1>
        <p className="text-gray-600 mb-6">{message}</p>
        <Link
          to="/"
          className="inline-block bg-gray-800 hover:bg-gray-700 text-white font-medium py-2 px-6 rounded-lg transition duration-300"
        >
          Return to Home
        </Link>
      </div>
    </div>
  );
}

export default Error;
