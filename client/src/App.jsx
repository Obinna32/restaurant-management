import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<div className="p-8">Registration Page (Coming Soon)</div>} />
          
          {/* Default Home route */}
          <Route path="/" element={<div className="p-8">Restaurant Home Page</div>} />
          
          {/* Role Protected Routes Examples */}
          <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin" element={<div className="p-8">Admin Dashboard</div>} />
          </Route>
          
          <Route element={<ProtectedRoute allowedRoles={['CHEF', 'ADMIN']} />}>
            <Route path="/kitchen" element={<div className="p-8">Kitchen Display System</div>} />
          </Route>
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;