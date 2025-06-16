import React from "react";

function Header({ candidate_name, job_title, organization_name }) {
  return (
    <header className="bg-gray-800 py-6 px-4 shadow-lg">
      <div className="container mx-auto flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold">NEX AI Interview</h1>
          <p className="text-gray-400">Welcome, {candidate_name}</p>
        </div>
        <div className="text-right">
          <p className="font-medium">{job_title}</p>
          <p className="text-gray-400">{organization_name}</p>
        </div>
      </div>
    </header>
  );
}

export default Header;
