import { Route, Routes } from 'react-router-dom'
import MainLayout from './layout'
import ConfigurationPage from './pages/configuration-page'
import GenerateTaskPage from './pages/generate-task-page'
import HomePage from './pages/home-page'
import TrainingPage from './pages/training-page'

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/configuration" element={<ConfigurationPage />} />
        <Route path="/generate" element={<GenerateTaskPage />} />
        <Route path="/training" element={<TrainingPage />} />
      </Route>
    </Routes>
  )
}
