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
        setSuccess(`Resume uploaded`);
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

  return (
    <div className="second__screen" ref={ref}>
      <div className="row">
        <div className="upload__form">
          {error && <div className="error-message">{error}</div>}
          {success && (
            <div className="success-message">
              {success}
              {resumeData && (
                <>
                  <p>File: {resumeData.filename}</p>
                  <button onClick={handleDelete} className="delete-button">
                    Delete Resume
                  </button>
                </>
              )}
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
