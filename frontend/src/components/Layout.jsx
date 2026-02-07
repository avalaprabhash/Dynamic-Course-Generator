import React from 'react';
import { Link, useLocation, useNavigate, Outlet } from 'react-router-dom';
import { BookOpen, Home, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14">
            <Link to="/" className="flex items-center gap-3 group">
              <div className="p-1.5 bg-slate-900 rounded-lg group-hover:bg-slate-800 transition-colors">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-semibold text-slate-900">AI Course & Quiz Generator</h1>
              </div>
            </Link>
            
            <nav className="flex items-center gap-2">
              <Link 
                to="/"
                className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors ${
                  location.pathname === '/' 
                    ? 'bg-slate-100 text-slate-900' 
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <Home className="w-4 h-4" />
                <span className="font-medium">Home</span>
              </Link>
              
              {isAuthenticated() && (
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm text-slate-600 hover:bg-slate-50 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="font-medium">Logout</span>
                </button>
              )}
            </nav>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      
      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-slate-500">
              AI-Powered Course Generator
            </p>
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <span>Remember</span>
              <span>→</span>
              <span>Understand</span>
              <span>→</span>
              <span>Apply</span>
              <span>→</span>
              <span>Analyze</span>
              <span>→</span>
              <span>Evaluate</span>
              <span>→</span>
              <span>Create</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
