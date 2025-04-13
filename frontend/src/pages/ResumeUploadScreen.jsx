import React, { forwardRef, useState } from 'react'
import UploadForm from '../components/UploadForm'

const ResumeUploadScreen = forwardRef((props, ref) => {
  const [error, setError] = useState('');
  const { onNextStep } = props;

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
    //   navigate('/upload-job');
    } catch (error) {
      console.error('Upload failed:', error);
      setError('Upload failed. Please try again.');
    }
  }

  return (
    <>
     <div className='second__screen' ref={ref}>
        <div className='row'>
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
       <button className='action__button' onClick={onNextStep}>Next Step</button>
      </div>
    </>
  )
})

export default ResumeUploadScreen