import React from 'react';

/**
 * Reusable step indicator component
 */
function StepIndicator({ step, active = false, completed = false }) {
  const getClassName = () => {
    const classes = ['step-number'];
    
    if (active) {
      classes.push('active');
    }
    
    if (completed) {
      classes.push('completed');
    }
    
    return classes.join(' ');
  };

  return (
    <div className={getClassName()}>
      {step}
    </div>
  );
}

export default StepIndicator;