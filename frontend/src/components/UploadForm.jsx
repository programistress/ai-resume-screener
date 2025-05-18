import { useState } from 'react'

// component for uploading a resume file or a text
// args are is it a file or text, and the submit saves the data to our database if it is within norms
const UploadForm = ({ isFileUpload, onSubmit }) => {
    const [file, setFile] = useState(null)
    const [text, setText] = useState('')
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const fileTypes = [".pdf", ".docx", ".txt"]


    // set file to null if user cancelled the selection and updates file state when changed
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0]

        if (!selectedFile) {
            setFile(null)
            return
        }

        const file_extension = selectedFile.name.split('.').pop().toLowerCase();
        if (!fileTypes.includes(`.${file_extension}`)) {
            setError(`Sorry, we only accept files of ${fileTypes.join(',')} formats`)
            setFile(null)
            return
        }

        setFile(selectedFile)  // updating file state when valid
        setError('')  // clear any previous errors
    }

    const handleTextChange = (e) => {
        setText(e.target.value)
        setError('')
    }

    //submits thew data into our arg onSubmit function if its valid and makes the button show loading
    const handleSubmit = async (e) => {
        e.preventDefault()

        if (isFileUpload && !file) {
            setError('Please select a valid file')
        }

        if (!isFileUpload && !text.trim()) {
            setError('Please enter your job description')
        }

        setIsLoading(true)

        try {
            await onSubmit(isFileUpload ? file : text)

            if (isFileUpload) {
                setFile(null)
            } else {
                setText('')
            }
        } catch (err) {
            setError('Error submitting form. Please try again.');
            console.error(err);
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className='upload-form__container'>
            {error && <div className="error__message">{error}</div>}
            <form onSubmit={handleSubmit}>
                {isFileUpload ? (
                    <div className='file-input__container'>
                        <input
                            type='file'
                            onChange={handleFileChange}
                            accept={fileTypes.join(',')} //types of files that our application accepts
                            id='file-upload'
                        />
                        <label htmlFor="file-upload" className="file-upload__label">
                            {file ? 'Choose a different file' : 'Choose a file'}
                        </label>
                        {file && <div className="file-name">{file.name}</div>}
                        {/* maybe add a little file preview later */}
                    </div>
                ) : (
                    <textarea
                        value={text}
                        onChange={handleTextChange}
                        placeholder='Paste your job description here...'
                        rows={15}
                        className='upload__form-textarea'
                    />
                )}
                <button
                    type='submit'
                    className='submit__button'
                    disabled={isLoading}
                >
                    {isLoading ? 'Processing...' : 'Submit'}
                </button>
            </form>
        </div>
    )
}

export default UploadForm