import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';
import ROISelector from './pages/ROISelector';
import Dashboard from './pages/Dashboard';
import Performance from './pages/Performance';
import Log from './pages/Log';
import Login from './pages/Login';
import Snapshot from './pages/Snapshot';
import Settings from './pages/Settings';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="/login" element={<Login />} />
      
      <Route element={<ProtectedRoute />}>
        <Route path="/roi" element={<ROISelector />} />
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/performance" element={<Performance />} />
          <Route path="/snapshot" element={<Snapshot />} />
          <Route path="/log" element={<Log />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Route>
    </Routes>
  );
}

export default App;
