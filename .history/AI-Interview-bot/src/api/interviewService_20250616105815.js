// src/api/interviewService.js

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

// Start a new interview
export const startInterview = async (data) => {
  const response = await fetch(`${API_BASE_URL}/start_interview`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  return await response.json()
}

// Get the next question
export const getQuestion = async () => {
  const response = await fetch(`${API_BASE_URL}/get_question`)
  return await response.json()
}

// Process the candidate's answer
export const processAnswer = async (answer, frameData) => {
  const response = await fetch(`${API_BASE_URL}/process_answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      answer,
      frame: frameData
    }),
  })
  return await response.json()
}

// Generate the final report
export const generateReport = async () => {
  const response = await fetch(`${API_BASE_URL}/generate_report`)
  return await response.json()
}

// Download report PDF
export const downloadReport = (filename) => {
  return `${API_BASE_URL}/download_report/${filename}`
}