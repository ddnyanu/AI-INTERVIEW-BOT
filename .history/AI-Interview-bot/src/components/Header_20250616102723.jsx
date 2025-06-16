import React from "react";

function Header() {
  return (
    <div className="container-fluid">
      <div className="row header">
        <div className="col-md-8 d-flex flex-column justify-content-center text-left">
          <h1 style={{ display: "flex", alignItems: "center" }}>
            <img
              src="/src/assets/botImage.png"
              alt="Bot Logo"
              style={{ height: "80px", marginRight: "10px" }}
            />
            NEX AI Interview Bot
          </h1>
        </div>
        <div className="col-md-4 d-flex flex-column justify-content-center align-items-end pr-4">
          <h5 className="mb-0 text-right">
            Welcome, {candidateName}!<br />
            <strong>
              Organization Name: &nbsp;{organizationName || "N/A"}
            </strong>
            <br />
            <strong>Job Title: &nbsp;{jobTitle || "N/A"}</strong>
            <br />
            <strong>Email: &nbsp;{email || "N/A"}</strong>
          </h5>
        </div>
      </div>
    </div>
  );
}

export default Header;
