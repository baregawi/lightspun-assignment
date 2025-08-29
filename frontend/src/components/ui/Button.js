import React from 'react';

/**
 * Reusable button component
 */
function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  type = 'button',
  disabled = false,
  loading = false,
  onClick,
  ...props 
}) {
  const getClassName = () => {
    const classes = ['btn'];
    
    // Variant classes
    classes.push(`btn-${variant}`);
    
    // Size classes
    if (size !== 'medium') {
      classes.push(`btn-${size}`);
    }
    
    return classes.join(' ');
  };

  const handleClick = (event) => {
    if (!disabled && !loading && onClick) {
      onClick(event);
    }
  };

  return (
    <button
      type={type}
      className={getClassName()}
      disabled={disabled || loading}
      onClick={handleClick}
      aria-disabled={disabled || loading}
      {...props}
    >
      {loading ? 'Loading...' : children}
    </button>
  );
}

export default Button;