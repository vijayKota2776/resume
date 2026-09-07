import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { LogOut, User, FileText, Briefcase } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const Layout = () => {
  const token = localStorage.getItem('token');
  const navigate = useNavigate();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Top Navbar */}
      <nav className="bg-white shadow-sm border-b px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-indigo-600">ResumeTailor</h1>
        <button 
          onClick={handleLogout}
          className="flex items-center text-gray-600 hover:text-red-600 transition-colors"
        >
          <LogOut className="w-5 h-5 mr-2" />
          Logout
        </button>
      </nav>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r hidden md:block">
          <div className="p-4 space-y-2">
            <Link to="/dashboard" className="flex items-center p-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors">
              <Briefcase className="w-5 h-5 mr-3" />
              Dashboard
            </Link>
            <Link to="/profile" className="flex items-center p-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors">
              <User className="w-5 h-5 mr-3" />
              My Profile
            </Link>
            <Link to="/tailor" className="flex items-center p-3 text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors">
              <FileText className="w-5 h-5 mr-3" />
              Tailor Resume
            </Link>
          </div>
        </aside>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
