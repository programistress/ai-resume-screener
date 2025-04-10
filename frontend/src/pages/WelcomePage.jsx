import React, { useRef, useState } from 'react'
import UploadForm from '../components/UploadForm'
import { useNavigate } from 'react-router-dom';
import './WelcomePage.css'
import './WelcomeScreen.css'

const WelcomePage = () => {
  const targetRef = useRef(null);
  const navigate = useNavigate()
  const [error, setError] = useState('');

  //scrollung when button is pressed
  const scrollToTarget = () => {
    targetRef.current.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (file) => {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/api/resumes/upload/', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.status}`);
      }
      navigate('/upload-job');
    } catch (error) {
      console.error('Upload failed:', error);
      setError('Upload failed. Please try again.');
    }
  }

  return (
    <div className='container'>
      <div className='first__screen'>
        <div className="welcome__screen">
          <header className='welcome__header'>
              <h1 className='welcome__title'>Upgrade Your Resume with AI-Powered Optimization Technology</h1>
              <p className='welcome__desc'>Land more interviews by perfectly matching your resume to job descriptions. Our AI technology analyzes your qualifications against role requirements, providing a match score and targeted suggestions to help your application stand out.</p>
          </header>
          <div className='welcome__card'>
            <h2 className='welcome__title2'>How it works</h2>
              <ol>
                <li>Upload your resume</li>
                <li>Add desired job descriptions</li>
                <li>Get a match score and AI insights to improve your resume!</li>
              </ol>
          </div>
        </div>
        <button className='action__button' onClick={scrollToTarget}>Get started</button>
      </div>
      <div className='second__screen' ref={targetRef}>
        <div className='upload__form'>
            {error && <div className="error-message">{error}</div>}
            <UploadForm
            fileTypes={['.pdf', '.docx', '.txt']}
            onSubmit={handleSubmit}
            isFileUpload={true}
            />
            </div>
          <header className='upload__form-header'>
                <h1 className='welcome__title right'>Step 1: Upload Your Resume</h1>
                <p className='welcome__desc right'>Our system will analyze it using Natural Language Processing (NLP) to understand your experience, skills, and achievements on a deeper level.</p>
                <p className='requirements right'> File types: PDF, DOCX, TXT <br /> Max size: 10MB</p>
            </header>
      </div>

    
    </div>
  )
}

export default WelcomePage