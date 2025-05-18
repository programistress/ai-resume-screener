import { forwardRef, useEffect, useState } from "react";
import UploadForm from "../components/UploadForm";
import api from "../services/api";

const ResumeUploadScreen = forwardRef((props, ref) => {
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { toNextStep } = props;

  //checks localStorage when component loads
  useEffect(() => {
    const resumeData = localStorage.getItem("resumeData");
    if (resumeData) {
      const parsedData = JSON.parse(resumeData);
      setSuccess(`Resume uploaded: ${parsedData.filename}`);
    }
  }, []);

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
          {success && <div className="success-message">{success}</div>}
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
