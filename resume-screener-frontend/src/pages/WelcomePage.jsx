import React, { useState } from 'react'
import UploadForm from '../components/UploadForm'
import { useNavigate } from 'react-router-dom';

const WelcomePage = () => {

  const navigate = useNavigate()
  const [error, setError] = useState('');

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
    <div className='welcome__container'>
        <header>
            <h1>Is Your Resume Job-Ready?</h1>
            <p>Upload your resume and a job description—our AI will analyze and score your fit for the role, helping you stand out to employers.</p>
        </header>

        <div className="welcome__card">
          <h2>How it works</h2>
          <ol>
            <li>Upload your resume</li>
            <li>Add desired job descriptions</li>
            <li>Get a match score and AI insights to improve your resume!</li>
          </ol>
        </div>

        <div className='welcome__action'>
            <h1>Upload your resume to get started</h1>
            {error && <div className="error-message">{error}</div>}
            <UploadForm
            fileTypes={['.pdf', '.docx', '.txt']}
            onSubmit={handleSubmit}
            isFileUpload={true}
            />
        </div>

    </div>
  )
}

export default WelcomePage