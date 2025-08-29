import React from 'react';
import { AddressForm } from './features';
import { SUCCESS_MESSAGES, ERROR_MESSAGES } from './constants';
import { formatFullAddress } from './utils';
import './App.css';

function App() {
  const handleFormSubmit = async (formData) => {
    console.log('Form submitted with data:', formData);
    
    // Here you could send the data to your backend API
    // For now, we'll just show an alert
    const fullAddress = formatFullAddress(
      formData.streetAddress, 
      formData.municipality, 
      formData.state
    );
    
    alert(`${SUCCESS_MESSAGES.FORM_SUBMITTED}\n\nFull Address: ${fullAddress}`);
  };

  const handleFormReset = () => {
    console.log(SUCCESS_MESSAGES.FORM_RESET);
  };

  const handleFormError = (error) => {
    console.error('Form error:', error);
    alert(ERROR_MESSAGES.FORM_SUBMIT_FAILED);
  };

  return (
    <div className="App">
      <header className="App-header">
        <div className="container">
          <h1>🏠 Lightspun Address Search</h1>
          <p>Find and select addresses across US states and municipalities</p>
        </div>
      </header>

      <main className="App-main">
        <div className="container">
          <AddressForm 
            onSubmit={handleFormSubmit}
            onReset={handleFormReset}
            onError={handleFormError}
          />
        </div>
      </main>

      <footer className="App-footer">
        <div className="container">
          <p>&copy; 2024 Lightspun Address Search. Built with React and FastAPI.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;