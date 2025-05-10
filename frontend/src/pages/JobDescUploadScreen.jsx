import React, { forwardRef, useState, useEffect } from "react";
import UploadForm from "../components/UploadForm";
import "./JobDescUpload.css";
import api from "../services/api";

const JobDescUploadScreen = forwardRef((props, ref) => {
  const [error, setError] = useState("");
  const [uploadedJobs, setUploadedJobs] = useState([]);
  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // on component mount load jobs from localStorage
  useEffect(() => {
    const storedJobs = localStorage.getItem("jobDescData");

    if (storedJobs) {
      try {
        const parsedJobs = JSON.parse(storedJobs);
        setUploadedJobs(parsedJobs);
      } catch (err) {
        console.error("Error parsing stored jobs:", err);
        setUploadedJobs([]);
      }
    }

    setIsInitialLoad(false);
  }, []);

  // whenever uploadedJobs changes but not on initial load)
  useEffect(() => {
    if (!isInitialLoad) {
      localStorage.setItem("jobDescData", JSON.stringify(uploadedJobs));
    }
  }, [uploadedJobs, isInitialLoad]);

  const handleSubmit = async (text) => {
    if (uploadedJobs.length >= 3) {
      setError(
        "Maximum of 3 job descriptions allowed. Please delete one to add another."
      );
      return;
    }
    setError("");
    try {
      const response = await api.post("/jobs/upload/", {
        raw_text: text,
      });
      if (response.data && response.data.id) {
        setUploadedJobs([
          ...uploadedJobs,
          {
            id: response.data.id,
            text: response.data.raw_text,
            uploadedAt: new Date().toISOString(),
          },
        ]);
      }
    } catch (err) {
      console.error("Upload failed:", err);
      setError("Failed to upload job description. Please try again.");
    }
  };

  const handleDelete = async (jobId) => {
    try {
      await api.delete(`/job-descriptions/${jobId}/`);
      setUploadedJobs(uploadedJobs.filter((job) => job.id !== jobId));
    } catch (err) {
      console.error("Delete failed:", err);
      setError("Failed to delete job description. Please try again.");
    }
  };

  return (
    <div className="job-desc-screen" ref={ref}>
      <div className="job-desc-container">
        <header className="job-desc-header">
          <h1 className="job-desc-title">Step 2: Add Job Descriptions</h1>
          <p className="job-desc-subtitle">
            Paste the job posting you're interested in applying for
          </p>
          <p className="job-desc-info">
            Our AI will analyze the job requirements and match them with your
            resume to provide tailored recommendations.
          </p>
          {uploadedJobs.length > 0 && (
            <div className="uploaded-jobs-section">
              <h3 className="uploaded-jobs-title">
                Uploaded Job Descriptions ({uploadedJobs.length}/3)
              </h3>
              <ul className="uploaded-jobs-list">
                {uploadedJobs.map((job) => (
                  <li key={job.id} className="uploaded-job-item">
                    <div className="uploaded-job-text">{job.text}</div>
                    <button
                      className="delete-job-btn"
                      onClick={() => handleDelete(job.id)}
                    >
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </header>

        <div className="job-desc-form">
          {error && <div className="error-message">{error}</div>}
          <UploadForm isFileUpload={false} onSubmit={handleSubmit} />
        </div>
      </div>
      <button className="action__button" >
        Next Step
      </button>
    </div>
  );
});

export default JobDescUploadScreen;
