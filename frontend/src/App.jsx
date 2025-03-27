import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import MachineMonitoring from './pages/MachineMonitoring'
import AnomalyDetection from './pages/AnomalyDetection'
import PredictiveMaintenance from './pages/PredictiveMaintenance'
import PerformanceOptimization from './pages/PerformanceOptimization'
import Settings from './pages/Settings'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-base-200">
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
      
      <div className="flex flex-col flex-1 overflow-hidden">
        <Navbar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
        
        <main className="flex-1 overflow-y-auto p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/machine-monitoring" element={<MachineMonitoring />} />
            <Route path="/anomaly-detection" element={<AnomalyDetection />} />
            <Route path="/predictive-maintenance" element={<PredictiveMaintenance />} />
            <Route path="/performance-optimization" element={<PerformanceOptimization />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
