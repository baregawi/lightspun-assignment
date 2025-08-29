/**
 * UI-related constants
 */

export const FORM_STEPS = {
  STATE: 1,
  MUNICIPALITY: 2,
  ADDRESS: 3,
};

export const FORM_LABELS = {
  STATE: 'State',
  MUNICIPALITY: 'Municipality',
  ADDRESS: 'Street Address',
  SUBMIT: 'Submit Address',
  RESET: 'Reset Form',
  RETRY: 'Retry',
};

export const LOADING_MESSAGES = {
  STATES: 'Loading states...',
  MUNICIPALITIES: 'Loading municipalities...',
  ADDRESSES: 'Searching...',
};

export const ERROR_MESSAGES = {
  STATES_LOAD_FAILED: 'Failed to load states. Please try again.',
  MUNICIPALITIES_LOAD_FAILED: 'Failed to load municipalities. Please try again.',
  ADDRESSES_LOAD_FAILED: 'Failed to load address suggestions',
  FORM_INCOMPLETE: 'Please complete all required fields',
  FORM_SUBMIT_FAILED: 'Failed to submit form. Please try again.',
};

export const SUCCESS_MESSAGES = {
  FORM_SUBMITTED: 'Address submitted successfully!',
  FORM_RESET: 'Form reset',
};

export const PLACEHOLDERS = {
  STATE_SELECT: 'Select a state...',
  MUNICIPALITY_SELECT: 'Select a municipality...',
  ADDRESS_INPUT: 'Start typing an address...',
};

export const ACCESSIBILITY = {
  REQUIRED_INDICATOR: '*',
  LOADING_ARIA: 'Loading',
  ERROR_ARIA: 'Error',
  SUCCESS_ARIA: 'Success',
};