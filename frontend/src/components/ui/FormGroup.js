import React from 'react';
import { ACCESSIBILITY } from '../../constants';

/**
 * Reusable form group component
 */
function FormGroup({ 
  label, 
  required = false, 
  error, 
  helpText, 
  children,
  id 
}) {
  return (
    <div className="form-group">
      {label && (
        <label htmlFor={id}>
          {label}
          {required && <span className="required">{ACCESSIBILITY.REQUIRED_INDICATOR}</span>}
        </label>
      )}
      
      {children}
      
      {error && (
        <div className="error-message" role="alert">
          {error}
        </div>
      )}
      
      {helpText && !error && (
        <small className="form-text">
          {helpText}
        </small>
      )}
    </div>
  );
}

export default FormGroup;