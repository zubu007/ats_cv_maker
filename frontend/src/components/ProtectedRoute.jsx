import { useEffect, useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';

import { apiRequest } from '../auth/api';

export default function ProtectedRoute({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;

    async function loadUser() {
      try {
        const data = await apiRequest('/api/v1/auth/me');
        if (mounted) {
          setUser(data);
        }
      } catch {
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadUser();

    return () => {
      mounted = false;
    };
  }, [location.pathname]);

  const handleLogout = async () => {
    try {
      await apiRequest('/api/v1/auth/logout', { method: 'POST' });
    } finally {
      navigate('/auth', { replace: true });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-300">
        Checking session...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth" state={{ from: location.pathname }} replace />;
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-white/10 bg-black/20 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm text-slate-300">
            <Link to="/" className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/50">
              Home
            </Link>
            <Link
              to="/cover-letter"
              className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/50"
            >
              Cover Letter
            </Link>
            <Link
              to="/my-data"
              className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/50"
            >
              My Data
            </Link>
            <Link
              to="/my-jobs"
              className="rounded-full border border-white/15 px-3 py-1.5 hover:border-teal/50"
            >
              My Jobs
            </Link>
          </div>
          <div className="flex items-center gap-3 text-sm text-slate-300">
            <span className="hidden sm:inline">{user.first_name || user.email}</span>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-full border border-white/15 px-3 py-1.5 hover:border-red-400/50 hover:text-red-200"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      {children}
    </div>
  );
}
