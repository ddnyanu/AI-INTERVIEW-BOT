import React, { useState } from "react";
import CameraFeed from "./CameraFeed";

const SetupSection = ({ onStartInterview }) => {
  const [experienceLevel, setExperienceLevel] = useState("fresher");
  const [yearsExperience, setYearsExperience] = useState(3);

  const handleSubmit = (e) => {
    e.preventDefault();
    onStartInterview({
      experienceLevel,
      yearsExperience: experienceLevel === "experienced" ? yearsExperience : 0,
    });
  };

  return (
    <div className="row setup-section">
      <div className="col-md-6 offset-md-3">
        <div className="card" style={{ backgroundColor: "#dfd0b8" }}>
          <div className="card-header">
            <h3>Interview Setup</h3>
          </div>
          <div className="card-body">
            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label className="form-label">Experience Level</label>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="experienceLevel"
                    id="fresher"
                    value="fresher"
                    checked={experienceLevel === "fresher"}
                    onChange={() => setExperienceLevel("fresher")}
                  />
                  <label className="form-check-label" htmlFor="fresher">
                    Fresher
                  </label>
                </div>
                <div className="form-check">
                  <input
                    className="form-check-input"
                    type="radio"
                    name="experienceLevel"
                    id="experienced"
                    value="experienced"
                    checked={experienceLevel === "experienced"}
                    onChange={() => setExperienceLevel("experienced")}
                  />
                  <label className="form-check-label" htmlFor="experienced">
                    Experienced
                  </label>
                </div>
              </div>

              {experienceLevel === "experienced" && (
                <div className="mb-3 experience-fields" id="experienceFields">
                  <label htmlFor="yearsExperience" className="form-label">
                    Years of Experience
                  </label>
                  <input
                    type="number"
                    className="form-control"
                    id="yearsExperience"
                    min="1"
                    max="30"
                    value={yearsExperience}
                    onChange={(e) =>
                      setYearsExperience(parseInt(e.target.value))
                    }
                  />
                </div>
              )}

              <CameraFeed />

              <button
                type="submit"
                id="startInterviewBtn"
                className="btn btn-lg w-100"
                style={{ backgroundColor: "#222831", color: "#dfd0b8" }}
              >
                <i className="fas fa-play"></i> Start Interview
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SetupSection;
