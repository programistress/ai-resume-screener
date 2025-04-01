import React from 'react'

const WelcomePage = () => {
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
            {/* <UploadForm /> */}
        </div>

    </div>
  )
}

export default WelcomePage