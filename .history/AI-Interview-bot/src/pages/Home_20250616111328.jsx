// import React, { useState, useEffect } from "react";
// import Header from "../components/Header";
// import InterviewSection from "../components/InterviewSection";
// import { fetchInterviewData } from "../api/interviewService";

// function Home() {
//   const [interviewStarted, setInterviewStarted] = useState(false);
//   const [interviewData, setInterviewData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   // Fetch interview data from backend on component mount
//   useEffect(() => {
//     const loadData = async () => {
//       try {
//         const data = await fetchInterviewData();
//         setInterviewData(data);
//       } catch (err) {
//         setError(err.message);
//       } finally {
//         setLoading(false);
//       }
//     };
//     loadData();
//   }, []);

//   if (loading)
//     return <div className="text-center py-20">Loading interview data...</div>;
//   if (error)
//     return <div className="text-center py-20 text-red-500">Error: {error}</div>;

//   return (
//     <div className="bg-gray-900 min-h-screen text-gray-100">
//       <Header {...interviewData.candidate_info} />

//       <main className="container mx-auto px-4 py-8">
//         {!interviewStarted ? (
//           <div className="max-w-md mx-auto bg-gray-800 rounded-xl shadow-md overflow-hidden p-6 text-center">
//             <h2 className="text-xl font-bold mb-4">
//               Ready for your interview?
//             </h2>
//             <p className="mb-6">Position: {interviewData.job_title}</p>
//             <button
//               onClick={() => setInterviewStarted(true)}
//               className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
//             >
//               Start Interview
//             </button>
//           </div>
//         ) : (
//           <InterviewSection
//             interviewData={interviewData}
//             onComplete={() => setInterviewStarted(false)}
//           />
//         )}
//       </main>
//     </div>
//   );
// }

// export default Home;

import React, { useState, useEffect } from "react";
import Header from "../components/Header";
import InterviewSection from "../components/InterviewSection";
import { fetchMockInterviewData } from "../api/mockInterviewService";

function Home() {
  const [interviewStarted, setInterviewStarted] = useState(false);
  const [interviewData, setInterviewData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load mock data instead of calling backend
  useEffect(() => {
    const loadData = async () => {
      const data = fetchMockInterviewData(); // Using mock service
      setInterviewData(data);
      setLoading(false);
    };
    loadData();
  }, []);

  if (loading)
    return <div className="text-center py-20">Loading mock data...</div>;

  return (
    <div className="bg-gray-900 min-h-screen text-gray-100">
      <Header {...interviewData.candidate_info} />

      <main className="container mx-auto px-4 py-8">
        {!interviewStarted ? (
          <div className="max-w-md mx-auto bg-gray-800 rounded-xl shadow-md overflow-hidden p-6 text-center">
            <h2 className="text-xl font-bold mb-4">Mock Interview Mode</h2>
            <p className="mb-2">Position: {interviewData.job_title}</p>
            <p className="mb-6 text-yellow-400">
              Using mock data - no backend required
            </p>
            <button
              onClick={() => setInterviewStarted(true)}
              className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
            >
              Start Mock Interview
            </button>
          </div>
        ) : (
          <InterviewSection
            interviewData={interviewData}
            onComplete={() => setInterviewStarted(false)}
            mockMode={true} // Pass mock mode flag
          />
        )}
      </main>
    </div>
  );
}

export default Home;
