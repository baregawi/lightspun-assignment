import React from 'react';

/**
 * Reusable loading state component
 */
function LoadingState({ message = 'Loading...', inline = false }) {
  const className = inline ? 'loading-inline' : 'loading-state';
  
  return (
    <div className={className} role="status" aria-live="polite">
      {message}
    </div>
  );
}

export default LoadingState;