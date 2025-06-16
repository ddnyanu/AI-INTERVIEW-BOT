import React, { useState } from "react";
import CameraFeed from "./CameraFeed";

function SetupSection({ onStartInterview }) {
  // Form state
  const [formData, setFormData] = useState({
    role: "Software Engineer",
    experienceLevel: "fresher",
    yearsExperience: 3,
    resume: null,
    jobDescription: null,
  });

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Handle file uploads
  const handleFileChange = (e) => {
    const { name, files } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: files[0],
    }));
  };

  // Form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    // Here you would process the files and extract text
    // For now, we'll mock this part
    const resumeText = formData.resume ? "Extracted resume text..." : "";
    const jdText = formData.jobDescription ? "Extracted JD text..." : "";

    onStartInterview({
      role: formData.role,
      experienceLevel: formData.experienceLevel,
      yearsExperience:
        formData.experienceLevel === "experienced"
          ? formData.yearsExperience
          : 0,
      resumeText,
      jdText,
    });
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-amber-50 rounded-lg shadow-xl overflow-hidden">
        {/* Card Header */}
        <div className="bg-gray-800 text-amber-100 px-6 py-4">
          <h2 className="text-xl font-bold">Interview Setup</h2>
          <p className="text-sm opacity-80">
            Configure your interview settings
          </p>
        </div>

        {/* Card Body */}
        <div className="p-6">
          <form onSubmit={handleSubmit}>
            {/* Role Selection */}
            <div className="mb-6">
              <label className="block text-gray-700 font-medium mb-2">
                Job Role
              </label>
              <select
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-500"
                required
              >
                <option value="Software Engineer">Software Engineer</option>
                <option value="Data Scientist">Data Scientist</option>
                <option value="Product Manager">Product Manager</option>
                <option value="UX Designer">UX Designer</option>
              </select>
            </div>

            {/* Experience Level */}
            <div className="mb-6">
              <label className="block text-gray-700 font-medium mb-2">
                Experience Level
              </label>
              <div className="space-y-2">
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="experienceLevel"
                    value="fresher"
                    checked={formData.experienceLevel === "fresher"}
                    onChange={handleInputChange}
                    className="text-amber-600 focus:ring-amber-500"
                  />
                  <span>Fresher</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="experienceLevel"
                    value="experienced"
                    checked={formData.experienceLevel === "experienced"}
                    onChange={handleInputChange}
                    className="text-amber-600 focus:ring-amber-500"
                  />
                  <span>Experienced</span>
                </label>
              </div>
            </div>

            {/* Years of Experience (conditionally shown) */}
            {formData.experienceLevel === "experienced" && (
              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2">
                  Years of Experience
                </label>
                <input
                  type="number"
                  name="yearsExperience"
                  min="1"
                  max="30"
                  value={formData.yearsExperience}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
              </div>
            )}

            {/* Camera Feed */}
            <div className="mb-6">
              <label className="block text-gray-700 font-medium mb-2">
                Camera Preview
              </label>
              <CameraFeed />
              <p className="text-sm text-gray-500 mt-1">
                Ensure your face is clearly visible in well-lit conditions
              </p>
            </div>

            {/* File Uploads */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Upload Resume
                </label>
                <input
                  type="file"
                  name="resume"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx"
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-amber-50 file:text-amber-700
                    hover:file:bg-amber-100"
                />
              </div>
              <div>
                <label className="block text-gray-700 font-medium mb-2">
                  Upload Job Description
                </label>
                <input
                  type="file"
                  name="jobDescription"
                  onChange={handleFileChange}
                  accept=".pdf,.doc,.docx"
                  className="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-md file:border-0
                    file:text-sm file:font-semibold
                    file:bg-amber-50 file:text-amber-700
                    hover:file:bg-amber-100"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="w-full bg-gray-800 hover:bg-gray-700 text-amber-100 font-bold py-3 px-4 rounded-md transition duration-300 flex items-center justify-center"
            >
              <span>Start Interview</span>
              <svg
                className="w-5 h-5 ml-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M14 5l7 7m0 0l-7 7m7-7H3"
                />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default SetupSection;
