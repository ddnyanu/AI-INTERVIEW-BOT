import React, { useState, useEffect } from "react";

const ReportModal = ({ show, onClose, reportData }) => {
  const [loading, setLoading] = useState(true);
  const [report, setReport] = useState(null);

  useEffect(() => {
    if (show) {
      setLoading(true);
      // Simulate API call to get report
      setTimeout(() => {
        setReport({
          status: "Selected",
          status_class: "selected",
          avg_rating: 8.5,
          duration: "15:30",
          report:
            "<h4>Technical Skills</h4><p>Excellent understanding of core concepts...</p>",
        });
        setLoading(false);
      }, 1500);
    }
  }, [show]);

  const downloadPDF = () => {
    // Implement PDF download functionality
    alert("Downloading report...");
  };

  const printReport = () => {
    window.print();
  };

  if (!show) return null;

  return (
    <div
      className="modal fade show"
      style={{ display: "block", backgroundColor: "rgba(0,0,0,0.5)" }}
    >
      <div className="modal-dialog modal-lg report-modal">
        <div className="modal-content">
          <div className="modal-header report-header">
            <h5 className="modal-title">Interview Evaluation Report</h5>
            <button
              type="button"
              className="btn-close btn-close-white"
              onClick={onClose}
            ></button>
          </div>
          <div className="modal-body">
            <div className="report-content">
              {loading ? (
                <div className="text-center p-5">
                  <div
                    className="spinner-border text-primary mb-3"
                    role="status"
                    style={{ width: "3rem", height: "3rem" }}
                  >
                    <span className="visually-hidden">Loading...</span>
                  </div>
                  <h4>Generating Interview Report</h4>
                  <p className="text-muted">
                    Please wait while we analyze your interview responses...
                  </p>
                </div>
              ) : (
                <>
                  <div className="report-info mb-4">
                    <h4>Interview Summary</h4>
                    <div className="d-flex justify-content-between align-items-center">
                      <span
                        className={`final-decision decision-${report.status_class}`}
                      >
                        {report.status === "Selected"
                          ? "✅ "
                          : report.status === "On Hold"
                          ? "⏳ "
                          : "❌ "}
                        {report.status}
                      </span>
                      <span
                        className={`badge ${getRatingBadgeClass(
                          report.avg_rating
                        )}`}
                      >
                        Average Rating: {report.avg_rating.toFixed(1)}/10
                      </span>
                      <span className="badge bg-secondary">
                        Duration: {report.duration}
                      </span>
                    </div>
                  </div>
                  <div dangerouslySetInnerHTML={{ __html: report.report }} />
                </>
              )}
            </div>
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
            >
              Close
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={printReport}
            >
              <i className="fas fa-print"></i> Print Report
            </button>
            <button
              type="button"
              className="btn btn-success"
              onClick={downloadPDF}
            >
              <i className="fas fa-download"></i> Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

function getRatingBadgeClass(rating) {
  if (rating >= 7) return "rating-excellent";
  if (rating >= 5) return "rating-good";
  if (rating >= 3) return "rating-average";
  return "rating-poor";
}

export default ReportModal;
