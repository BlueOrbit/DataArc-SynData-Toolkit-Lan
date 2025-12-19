import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import InitialSetupGuard from './components/initial-setup-guard'
import { ThemeProvider } from './contexts/theme-context'
import './styles'
import App from './app.tsx'

const rootElement = document.getElementById('root')
if (!rootElement) throw new Error('Root element not found')
createRoot(rootElement).render(
  <BrowserRouter>
    <ThemeProvider>
      <InitialSetupGuard>
        <App />
      </InitialSetupGuard>
    </ThemeProvider>
  </BrowserRouter>,
)
