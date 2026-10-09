import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './tokens.css'
import './style.css'
import './fixture.css'
import './chat.css'
import './theme.css'
import './dashboard.css'

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
