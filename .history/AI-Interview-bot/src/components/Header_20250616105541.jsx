import React from "react";

function Header({ candidateName, organizationName, jobTitle, email }) {
  return (
    <header className="bg-gradient-to-r from-gray-800 to-gray-900 text-amber-100 shadow-lg">
      <div className="container mx-auto px-6 py-6">
        <div className="flex flex-col md:flex-row justify-between items-center">
          {/* Logo and Branding */}
          <div className="flex items-center mb-4 md:mb-0">
            <img
              src="/src/assets/botImage.png"
              alt="NEX AI Logo"
              className="h-16 mr-4"
            />
            <h1 className="text-2xl font-bold">NEX AI Interview Bot</h1>
          </div>

          {/* Candidate Information */}
          <div className="text-right">
            <h2 className="text-lg font-semibold">Welcome, {candidateName}!</h2>
            <div className="text-sm space-y-1 mt-1">
              <p>
                <span className="font-medium">Organization:</span>{" "}
                {organizationName || "N/A"}
              </p>
              <p>
                <span className="font-medium">Position:</span>{" "}
                {jobTitle || "N/A"}
              </p>
              <p>
                <span className="font-medium">Email:</span> {email || "N/A"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
