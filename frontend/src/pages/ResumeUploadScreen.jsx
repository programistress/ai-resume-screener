import { forwardRef, useEffect, useState } from "react";
import "./ResumeUploadScreen.css";
import UploadForm from "../components/UploadForm";
import api from "../services/api";

// accepts a ref as an argument
const ResumeUploadScreen = forwardRef((props, ref) => {
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [resumeData, setResumeData] = useState(null);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const { toNextStep } = props; //destructuring assignment

  //load resume from localStorage on mount
  useEffect(() => {
    const storedResume = localStorage.getItem("resumeData");

    if (storedResume) {
      try {
        setResumeData(JSON.parse(storedResume));
      } catch (error) {
        console.error("Error parsing stored resume:", error);
      }
    }

    setIsInitialLoad(false);
  }, []);

  // save changes to localStorage
  useEffect(() => {
    if (!isInitialLoad && resumeData) {
      localStorage.setItem("resumeData", JSON.stringify(resumeData));
    }
  }, [resumeData, isInitialLoad]);

  const deleteOldResumeFromDatabase = async (resumeId) => {
    try {
      await api.delete(`/resumes/${resumeId}/`);
      console.log(`Old resume with ID ${resumeId} deleted successfully`);
      return true;
    } catch (error) {
      console.error("Failed to delete old resume:", error);
      return false;
    }
  };

  // deleting the resume by id - from local storage and db
  const handleDelete = async () => {
    // if there is no resume = clear the storage
    if (!resumeData || !resumeData.id) {
      localStorage.removeItem("resumeData");
      setResumeData(null);
      setSuccess("");
      return;
    }

    try {
      setError("");
      // delete from database
      await api.delete(`/resumes/${resumeData.id}/`);
      // if successful, clear localStorage and state
      localStorage.removeItem("resumeData");
      setResumeData(null);
      setSuccess("Resume deleted successfully!");
      console.log("Resume deleted successfully");
    } catch (error) {
      console.error("Delete failed:", error);
      setError(
        `Failed to delete resume: ${
          error.response?.data?.message || error.message || "Unknown error"
        }`
      );
    }
  };

  const handleSubmit = async (file) => {
    if (!file) {
      setError("Please select a file before submitting");
      return;
    }

    setError("");

    if (resumeData && resumeData.id) {
      console.log("Found existing resume, deleting it first...");
      const deleteSuccess = await deleteOldResumeFromDatabase(resumeData.id);

      if (deleteSuccess) {
        console.log("Old resume deleted successfully");
      } else {
        console.log(
          "Failed to delete old resume, but continuing with new upload"
        );
        setError("old resume delete failed")
      }
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await api.post("resumes/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      // axios automatically parses JSON and puts it in response.data
      const data = response.data;

      const newResumeData = {
        id: data.id,
        filename: file.name,
        uploadedAt: new Date().toISOString(),
        extractedText:
          data.extracted_text?.substring(0, 100) || "Text extracted",
      };
      localStorage.setItem("resumeData", JSON.stringify(newResumeData));
      setResumeData(newResumeData);

      localStorage.setItem(
        "resumeData",
        JSON.stringify({
          id: data.id,
          filename: file.name,
          uploadedAt: new Date().toISOString(),
          extractedText:
            data.extracted_text?.substring(0, 100) || "Text extracted",
        })
      );

      console.log("Resume uploaded successfully:", data);
      setSuccess("Resume uploaded successfully!");
    } catch (error) {
      console.error("Upload failed:", error);

      // more detailed error handling
      const errorMessage =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        "Upload failed. Please try again.";

      setError(errorMessage);
    }
  };

  // auto-hide success message after 2 seconds
  useEffect(() => {
    let timer;
    if (success) {
      timer = setTimeout(() => {
        setSuccess("");
      }, 2000);
    }
    return () => clearTimeout(timer);
  }, [success]);

  return (
    <div className="second__screen" ref={ref}>
      {success && <div className="success-message-floating">{success}</div>}
      <div className="row">
        <div className="upload__form">
          {error && <div className="error-message">{error}</div>}
          {resumeData && (
            <div className="resume-info-container">
              <p className="file-info">File: {resumeData.filename}</p>
              <button onClick={handleDelete} className="delete-resume-button">
                <span className="delete-icon">×</span>
                Remove
              </button>
            </div>
          )}
          <UploadForm onSubmit={handleSubmit} isFileUpload={true} />
        </div>
        <header className="upload__form-header">
          <h1 className="welcome__title right">Step 1: Upload Your Resume</h1>
          <p className="welcome__desc right">
            Our system will analyze it using Natural Language Processing (NLP)
            to understand your experience, skills, and achievements on a deeper
            level.
          </p>
          <p className="requirements right">
            {" "}
            File types supported: PDF, DOCX, TXT <br /> Max size: 10MB
          </p>
        </header>
      </div>
      <button className="action__button" onClick={toNextStep}>
        Next Step
      </button>
    </div>
  );
});

export default ResumeUploadScreen;
