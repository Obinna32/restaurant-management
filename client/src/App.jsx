import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Login from './pages/Login';
import ProtectedRoute from './components/ProtectedRoute';
import Menu from './components/Menu';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          {/* Navigation Bar */}
          <nav className="bg-white shadow-sm border-b border-gray-100">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16 items-center">
                <Link to="/" className="text-2xl font-bold text-amber-600">
                  RestoSuite
                </Link>
                <div className="flex space-x-6 items-center">
                  <Link to="/menu" className="text-gray-700 hover:text-amber-600 font-medium">
                    Menu
                  </Link>
                  <Link to="/login" className="text-gray-700 hover:text-amber-600 font-medium">
                    Login
                  </Link>
                </div>
              </div>
            </div>
          </nav>

          {/* Application Routes */}
          <Routes>
            <Route path="/" element={<Menu />} />
            <Route path="/menu" element={<Menu />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<div className="p-8">Registration Page (Coming Soon)</div>} />

            {/* Role Protected Routes */}
            <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
              <Route path="/admin" element={<div className="p-8">Admin Dashboard</div>} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={['CHEF', 'ADMIN']} />}>
              <Route path="/kitchen" element={<div className="p-8">Kitchen Display System</div>} />
            </Route>
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;