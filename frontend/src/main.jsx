import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Note: StrictMode is intentionally omitted here. It double-invokes effects
// in development, which would start the camera scanner twice on the same
// DOM node and throw errors from html5-qrcode. Safe to omit for this app's
// scope.
createRoot(document.getElementById('root')).render(<App />)
