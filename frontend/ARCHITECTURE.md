# Frontend Architecture

This document describes the modular architecture of the Lightspun frontend application.

## 📁 Directory Structure

```
src/
├── components/           # Shared/reusable UI components
│   └── ui/              # Basic UI building blocks
│       ├── Button.js
│       ├── FormGroup.js
│       ├── Select.js
│       ├── LoadingState.js
│       ├── ErrorState.js
│       ├── AutocompleteDropdown.js
│       ├── StepIndicator.js
│       └── index.js
├── features/            # Feature-based modules
│   └── address-form/    # Address form feature
│       ├── components/  # Feature-specific components
│       │   ├── StateSelect.js
│       │   ├── MunicipalitySelect.js
│       │   ├── AddressAutocomplete.js
│       │   ├── AddressFormSummary.js
│       │   └── index.js
│       ├── AddressForm.js  # Main feature component
│       └── index.js
├── hooks/               # Custom React hooks
│   ├── useApi.js        # API state management
│   ├── useAutocomplete.js # Autocomplete logic
│   ├── useDebounce.js   # Debounce utility
│   └── index.js
├── services/            # External service integrations
│   └── api/             # API service layer
│       ├── client.js    # Base API client
│       ├── states.js    # States API
│       ├── municipalities.js # Municipalities API
│       ├── addresses.js # Addresses API
│       └── index.js
├── utils/               # Utility functions
│   ├── validation.js    # Form validation
│   ├── formatting.js    # Display formatting
│   ├── api.js          # API utilities
│   └── index.js
├── constants/           # Application constants
│   ├── api.js          # API configuration
│   ├── ui.js           # UI constants
│   └── index.js
├── styles/              # Styling modules
│   └── components.css   # Component-specific styles
├── App.js               # Main application component
├── App.css             # Global application styles
├── index.js            # Application entry point
└── index.css           # Global reset styles
```

## 🏗️ Architecture Principles

### 1. **Feature-Based Organization**
- Related functionality grouped into feature modules
- Each feature is self-contained with its own components
- Easy to locate and modify feature-specific code

### 2. **Separation of Concerns**
- **Components**: Pure UI rendering logic
- **Hooks**: Reusable stateful logic
- **Services**: External API communication
- **Utils**: Pure helper functions
- **Constants**: Configuration and static values

### 3. **Reusability**
- Shared UI components for consistent design
- Custom hooks for common patterns
- Utility functions for repeated operations

### 4. **Maintainability**
- Clear module boundaries
- Consistent naming conventions
- Explicit dependencies through imports

## 🧩 Module Descriptions

### Components (`/components`)
Reusable UI building blocks used throughout the application.

**Key Components:**
- `Button`: Configurable button with variants and states
- `FormGroup`: Form field wrapper with label, error, and help text
- `Select`: Enhanced select dropdown with loading/error states
- `LoadingState`: Consistent loading indicators
- `ErrorState`: Error display with retry functionality
- `AutocompleteDropdown`: Dropdown list for autocomplete
- `StepIndicator`: Visual step progress indicator

### Features (`/features`)
Feature-specific modules that combine components, hooks, and logic.

**Address Form Feature:**
- Self-contained address selection functionality
- Progressive form flow (State → Municipality → Address)
- Integration with autocomplete API
- Form validation and submission

### Hooks (`/hooks`)
Custom React hooks that encapsulate reusable stateful logic.

**Key Hooks:**
- `useApi`: Generic API call management with loading/error states
- `useApiData`: API data fetching with caching
- `useAutocomplete`: Complete autocomplete functionality with keyboard navigation
- `useDebounce`: Value debouncing for performance optimization

### Services (`/services`)
External service integrations, primarily API communication.

**API Services:**
- `client`: Base HTTP client with error handling and retry logic
- `states`: State-related API operations
- `municipalities`: Municipality-related API operations  
- `addresses`: Address-related API operations with autocomplete

### Utils (`/utils`)
Pure utility functions for common operations.

**Utility Modules:**
- `validation`: Form and data validation functions
- `formatting`: Display formatting and text manipulation
- `api`: API-related helper functions and error handling

### Constants (`/constants`)
Application-wide constants and configuration values.

**Constant Modules:**
- `api`: API endpoints, defaults, and configuration
- `ui`: UI text, labels, messages, and settings

## 🔄 Data Flow

### 1. **User Interaction**
User interacts with UI components (buttons, inputs, dropdowns)

### 2. **Component State**
Components manage local UI state and call appropriate hooks

### 3. **Hook Processing** 
Hooks handle business logic, API calls, and side effects

### 4. **Service Layer**
Services make HTTP requests to backend APIs

### 5. **State Update**
Results flow back through hooks to update component state

### 6. **UI Update**
React re-renders components with new data

## 🎯 Benefits of This Architecture

### **Developer Experience**
- **Easy Navigation**: Related code is grouped together
- **Clear Separation**: Each module has a single responsibility
- **Consistent Patterns**: Similar code follows same patterns
- **Reusable Components**: Less duplication, more consistency

### **Code Quality**
- **Testability**: Pure functions and isolated modules are easy to test
- **Maintainability**: Changes are localized to specific modules
- **Scalability**: New features can be added without affecting existing code
- **Type Safety**: Clear interfaces between modules

### **Performance**
- **Code Splitting**: Features can be lazy-loaded
- **Optimization**: Hooks prevent unnecessary re-renders
- **Caching**: API data is cached and reused
- **Bundle Size**: Unused code can be eliminated

## 🚀 Usage Examples

### Adding a New Feature
```javascript
// 1. Create feature directory
features/new-feature/

// 2. Create feature components
features/new-feature/components/FeatureComponent.js

// 3. Create main feature module
features/new-feature/NewFeature.js

// 4. Export from feature index
features/new-feature/index.js

// 5. Import in App.js
import { NewFeature } from './features';
```

### Creating a Reusable Hook
```javascript
// hooks/useNewHook.js
export function useNewHook(config) {
  // Hook logic
  return { data, loading, error };
}

// Export from hooks/index.js
export { useNewHook } from './useNewHook';

// Use in components
import { useNewHook } from '../../hooks';
```

### Adding a UI Component
```javascript
// components/ui/NewComponent.js
function NewComponent({ prop1, prop2 }) {
  // Component logic
}
export default NewComponent;

// Export from components/ui/index.js
export { default as NewComponent } from './NewComponent';

// Use anywhere
import { NewComponent } from '../components/ui';
```

## 🔧 Development Guidelines

### **File Naming**
- Components: PascalCase (`StateSelect.js`)
- Hooks: camelCase with "use" prefix (`useApi.js`)
- Utils: camelCase (`validation.js`)
- Constants: camelCase (`api.js`)

### **Import Organization**
```javascript
// 1. React imports
import React, { useState } from 'react';

// 2. Third-party imports
import axios from 'axios';

// 3. Internal imports (organized by distance)
import { Button } from '../../../components/ui';
import { useApi } from '../../hooks';
import { API_ENDPOINTS } from '../../constants';
```

### **Export Patterns**
```javascript
// Individual exports
export { ComponentA } from './ComponentA';
export { ComponentB } from './ComponentB';

// Default exports for main modules
export default MainComponent;

// Re-exports in index files
export * from './submodule';
```

This modular architecture provides a scalable, maintainable foundation for the frontend application while keeping code organized and developer-friendly.