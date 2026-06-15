import { useCallback, useState } from 'react'

export default function UploadDropzone({ collectionId, onUpload, isUploading }) {
  const [isDragging, setIsDragging] = useState(false)
  const [progress, setProgress] = useState(null)
  const [uploadError, setUploadError] = useState(null)

  const handleFile = useCallback(
    async (file) => {
      if (!file) return
      if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        setUploadError('Only PDF files are accepted.')
        return
      }

      setUploadError(null)
      setProgress(0)

      try {
        await onUpload(file, (evt) => {
          if (evt.total) setProgress(Math.round((evt.loaded / evt.total) * 100))
        })
        setProgress(null)
      } catch (err) {
        setUploadError(err.response?.data?.error?.message || 'Upload failed.')
        setProgress(null)
      }
    },
    [onUpload],
  )

  function handleDrop(e) {
    e.preventDefault()
    setIsDragging(false)
    handleFile(e.dataTransfer.files[0])
  }

  function handleInputChange(e) {
    handleFile(e.target.files[0])
    e.target.value = ''
  }

  return (
    <div>
      <label
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={`flex flex-col items-center justify-center gap-3 border-2 border-dashed rounded-xl p-8 cursor-pointer transition-colors ${
          isDragging
            ? 'border-indigo-500 bg-indigo-500/5'
            : 'border-gray-700 hover:border-gray-500 bg-gray-900/50'
        }`}
      >
        <input
          type="file"
          accept=".pdf,application/pdf"
          className="hidden"
          onChange={handleInputChange}
          disabled={isUploading}
        />
        <span className="text-3xl">📎</span>
        <div className="text-center">
          <p className="text-sm font-medium text-gray-300">
            {isUploading ? 'Uploading…' : 'Drop a PDF here or click to browse'}
          </p>
          <p className="text-xs text-gray-500 mt-1">PDF only · max 50 MB</p>
        </div>
      </label>

      {progress !== null && (
        <div className="mt-3">
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>Uploading</span>
            <span>{progress}%</span>
          </div>
          <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-indigo-500 transition-all duration-200"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
      )}

      {uploadError && (
        <p className="text-red-400 text-xs mt-2">{uploadError}</p>
      )}
    </div>
  )
}
