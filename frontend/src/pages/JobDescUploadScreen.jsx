import React, { forwardRef, useState } from 'react';
import UploadForm from '../components/UploadForm';
import './JobDescUpload.css'

const JobDescUploadScreen = forwardRef((props, ref) => {
  // const [error, setError] = useState('');
  const [uploadedJobs, setUploadedJobs] = useState([]);

  const handleSubmit = async (text) => {
    if (uploadedJobs.length >= 3) {
      setError('Maximum of 3 job descriptions allowed. Please delete one to add another.');
      return;
    }
    setIsLoading(true);
    setError('');
    try {
      const response = await api.post('/jobs/upload/', {
        raw_text: text
      });
      if (response.data && response.data.id) {
        // Add the new job description to our list
        setUploadedJobs([
          ...uploadedJobs,
          {
            id: response.data.id,
            text: response.data.raw_text,
            uploadedAt: new Date()
          }
        ]);
      }
    } catch (error) {
      console.error('Upload failed:', err);
      setError('Failed to upload job description. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }


  return (
    <div className='job-desc-screen' ref={ref}>
      <div className='job-desc-container'>
        <header className='job-desc-header'>
          <h1 className='job-desc-title'>Step 2: Add Job Descriptions</h1>
          <p className='job-desc-subtitle'>Paste the job posting you're interested in applying for</p>
          <p className='job-desc-info'>Our AI will analyze the job requirements and match them with your resume to provide tailored recommendations.</p>
        </header>

        <div className='job-desc-form'>
          {/* {error && <div className="error-message">{error}</div>} */}
          <UploadForm
            isFileUpload={false}
            onSubmit={handleSubmit}
          />
        </div>
      </div>
    </div>
  )
})

export default JobDescUploadScreen