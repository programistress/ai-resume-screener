import React, { forwardRef } from 'react';
import useState from 'react'
import UploadForm from '../components/UploadForm';
import './JobDescUpload.css'

const JobDescUploadScreen = forwardRef((props, ref) => {
    // const [error, setError] = useState('');

    const handleSubmit = () => {

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