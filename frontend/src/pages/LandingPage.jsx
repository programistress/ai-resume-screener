import { useRef } from "react";
import "./LandingPage.css";
import ResumeUploadScreen from "./ResumeUploadScreen";
import JobDescUploadScreen from "./JobDescUploadScreen";

const LandingPage = () => {
  const resumeScreenRef = useRef(null);
  const jobDescScreenRef = useRef(null);

  const scrollToResumeScreen = () => {
    resumeScreenRef.current.scrollIntoView({ behavior: "smooth" });
  };

  const scrollToJobDescScreen = () => {
    jobDescScreenRef.current.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="container">
      <div className="first__screen">
        <div className="welcome__screen">
          <header className="welcome__header">
            <h1 className="welcome__title">
              Upgrade Your Resume with AI-Powered Optimization Technology
            </h1>
            <p className="welcome__desc">
              Land more interviews by perfectly matching your resume to job
              descriptions. Our AI technology analyzes your qualifications
              against role requirements, providing a match score and targeted
              suggestions to help your application stand out.
            </p>
          </header>
          <div className="welcome__card">
            <h2 className="welcome__title2">How it works</h2>
            <ol>
              <li>Upload your resume</li>
              <li>Add desired job descriptions</li>
              <li>Get a match score and AI insights to improve your resume!</li>
            </ol>
          </div>
        </div>
        <button className="action__button" onClick={scrollToResumeScreen}>
          Get started
        </button>
      </div>
      <ResumeUploadScreen
        ref={resumeScreenRef}
        toNextStep={scrollToJobDescScreen}
      />
      <JobDescUploadScreen ref={jobDescScreenRef} />
    </div>
  );
};

export default LandingPage;
