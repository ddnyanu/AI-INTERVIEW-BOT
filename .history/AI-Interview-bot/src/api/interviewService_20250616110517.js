const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

export const fetchInterviewData = async () => {
  const response = await fetch(`${API_BASE_URL}/get_interview_data`)
  if (!response.ok) throw new Error('Failed to fetch interview data')
  return await response.json()
}

export const startInterview = async () => {
  const response = await fetch(`${API_BASE_URL}/start_interview`, {
    method: 'POST'
  })
  return await response.json()
}

export const processAnswer = async (answer, frameData) => {
  const response = await fetch(`${API_BASE_URL}/process_answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answer, frame: frameData })
  })
  return await response.json()
}

export const downloadReport = (reportId) => {
  window.open(`${API_BASE_URL}/download_report/${reportId}`, '_blank')
}