import React from 'react';
import { formatFullAddress } from '../../../utils';

/**
 * Address form summary component
 */
function AddressFormSummary({ selectedState, selectedMunicipality, streetAddress }) {
  if (!selectedState || !selectedMunicipality || !streetAddress) {
    return null;
  }

  const fullAddress = formatFullAddress(streetAddress, selectedMunicipality, selectedState);

  return (
    <div className="form-summary">
      <h4>Selected Address:</h4>
      <div className="address-details">
        <div><strong>Street:</strong> {streetAddress}</div>
        <div><strong>Municipality:</strong> {selectedMunicipality.name} {selectedMunicipality.type && `(${selectedMunicipality.type})`}</div>
        <div><strong>State:</strong> {selectedState.name} ({selectedState.code})</div>
        <div><strong>Full Address:</strong> {fullAddress}</div>
      </div>
    </div>
  );
}

export default AddressFormSummary;