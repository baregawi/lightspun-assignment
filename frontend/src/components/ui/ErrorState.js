import React from 'react';
import Button from './Button';

/**
 * Reusable error state component
 */
function ErrorState({ 
  message, 
  onRetry, 
  retryLabel = 'Retry',
  showRetry = true 
}) {
  return (
    <div className="error-state" role="alert">
      <div className="error-message">
        {message}
      </div>
      
      {showRetry && onRetry && (
        <Button 
          variant="retry"
          onClick={onRetry}
          size="small"
        >
          {retryLabel}
        </Button>
      )}
    </div>
  );
}

export default ErrorState;