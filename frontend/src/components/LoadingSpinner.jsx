import './LoadingSpinner.css'

function LoadingSpinner() {
  return (
    <div className="loading">
      <div className="loading__spinner" aria-label="Loading"></div>
      <p className="loading__text">
        Analyzing reviews... this may take a moment
      </p>
    </div>
  )
}

export default LoadingSpinner
