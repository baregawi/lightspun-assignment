# Lightspun Frontend

A React-based frontend application for the Lightspun Address Search system.

## Features

- **Multi-step Address Selection**: Progressive form that guides users through selecting:
  1. US State from dropdown
  2. Municipality within selected state  
  3. Street address with intelligent autocomplete

- **Smart Autocomplete**: Real-time address suggestions with fuzzy search capabilities
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Error Handling**: Graceful error handling with retry mechanisms
- **Keyboard Navigation**: Full keyboard support for accessibility

## Technology Stack

- **React 18**: Modern React with hooks and functional components
- **Vanilla CSS**: Custom responsive styling without external UI libraries
- **Fetch API**: Native browser API for HTTP requests
- **ESLint**: Code linting and formatting

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn
- Lightspun backend API running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Environment Variables

Create a `.env` file in the frontend directory if you need to customize the API URL:

```env
REACT_APP_API_URL=http://localhost:8000
```

## API Integration

The frontend integrates with the following backend APIs:

- `GET /states` - Fetch all US states
- `GET /states/{state_code}/municipalities` - Fetch municipalities in a state  
- `GET /addresses/autocomplete?q={query}&limit={limit}` - Address autocomplete

## Component Architecture

```
src/
├── components/
│   ├── StateSelect.js           # State selection dropdown
│   ├── MunicipalitySelect.js    # Municipality selection dropdown  
│   ├── AddressAutocomplete.js   # Address input with autocomplete
│   └── AddressForm.js           # Main form orchestrator
├── services/
│   └── api.js                   # API service functions
├── App.js                       # Main application component
├── App.css                      # Application styles
├── index.js                     # React root
└── index.css                    # Global styles
```

## Features in Detail

### Progressive Form Flow

1. **State Selection**: Loads all US states on component mount
2. **Municipality Selection**: Appears after state selection, loads municipalities for selected state
3. **Address Input**: Appears after municipality selection, provides autocomplete suggestions

### Autocomplete Features

- **Debounced Search**: 300ms delay to prevent excessive API calls
- **Keyboard Navigation**: Arrow keys, Enter, and Escape support
- **Click Outside**: Closes dropdown when clicking outside
- **Loading States**: Shows loading indicator during API calls
- **Error Handling**: Displays error messages and retry options

### Responsive Design

- **Mobile-first**: Designed for mobile devices first
- **Flexible Layout**: Adapts to different screen sizes
- **Touch-friendly**: Large touch targets for mobile interaction

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production  
- `npm test` - Launches the test runner
- `npm eject` - Ejects from Create React App (irreversible)

## Building for Production

```bash
npm run build
```

Builds the app for production to the `build` folder. The build is minified and optimized for best performance.

## Browser Support

- Chrome (latest)
- Firefox (latest) 
- Safari (latest)
- Edge (latest)

## Performance Considerations

- **Debounced API calls** prevent excessive requests during typing
- **Conditional rendering** only shows components when needed
- **Memoization** could be added for further optimization
- **Code splitting** could be implemented for larger applications

## Accessibility

- **Semantic HTML**: Proper form labels and structure
- **Keyboard Navigation**: Full keyboard support
- **ARIA Labels**: Screen reader friendly
- **Focus Management**: Logical focus flow
- **Color Contrast**: Meets WCAG guidelines

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the Lightspun assignment.