import React from "react";

const InterviewInvitation = ({ data }) => {
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">
        Welcome to the Interview, {data?.user_name}
      </h1>

      <div className="space-y-4">
        <p>
          <strong>Organization:</strong> {data?.organization_name || "N/A"}
        </p>
        <p>
          <strong>Job ID:</strong> {data?.job_id || "N/A"}
        </p>
        <p>
          <strong>Status:</strong> {data?.status || "N/A"}
        </p>
        <p>
          <strong>Email:</strong> {data?.email || "N/A"}
        </p>
        <p>
          <strong>Phone:</strong> {data?.phone_number || "N/A"}
        </p>
        <p>
          <strong>Match Score:</strong> {data?.match_score || "N/A"}%
        </p>
      </div>
    </div>
  );
};

export default InterviewInvitation;
