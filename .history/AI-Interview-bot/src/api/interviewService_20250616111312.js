// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

// export const fetchInterviewData = async () => {
//   const response = await fetch(`${API_BASE_URL}/get_interview_data`)
//   if (!response.ok) throw new Error('Failed to fetch interview data')
//   return await response.json()
// }

// export const startInterview = async () => {
//   const response = await fetch(`${API_BASE_URL}/start_interview`, {
//     method: 'POST'
//   })
//   return await response.json()
// }

// export const processAnswer = async (answer, frameData) => {
//   const response = await fetch(`${API_BASE_URL}/process_answer`, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ answer, frame: frameData })
//   })
//   return await response.json()
// }

// export const downloadReport = (reportId) => {
//   window.open(`${API_BASE_URL}/download_report/${reportId}`, '_blank')
// }

// src/api/mockInterviewService.js
export const fetchMockInterviewData = () => {
  return {
    candidate_info: {
      candidate_name: "Test Candidate",
      email: "test@example.com"
    },
    job_title: "Software Engineer",
    organization_name: "Mock Tech Inc",
    questions: [
      {
        text: "Tell us about your experience with React?",
        audio: "" // Leave empty or mock base64 audio string
      },
      {
        text: "How do you handle state management in large applications?",
        audio: ""
      },
      {
        text: "Explain your approach to testing frontend applications",
        audio: ""
      }
    ],
    report_id: "mock-report-123"
  }
}

export const processMockAnswer = async (answer) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000))
  return { status: 'processed' }
}

export const downloadMockReport = () => {
  // Create a dummy PDF or text file for download
  const blob = new Blob(["Mock Interview Report\n\nCandidate: Test Candidate\nScore: 85%"], 
    { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'mock-interview-report.txt'
  a.click()
  URL.revokeObjectURL(url)
}