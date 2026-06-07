import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

import { apiRequest } from '../auth/api';

export default function AuthPage() {
  const [mode, setMode] = useState('login');
  const [firstName, setFirstName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();

  const nextPath = location.state?.from || '/';

  useEffect(() => {
    let mounted = true;

    async function checkSession() {
      try {
        await apiRequest('/api/v1/auth/me');
        if (mounted) {
          navigate('/', { replace: true });
        }
      } catch {
        // Not logged in yet.
      }
    }

    checkSession();

    return () => {
      mounted = false;
    };
  }, [navigate]);

  const submit = async (event) => {
    event.preventDefault();

    if (mode === 'signup' && password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const endpoint = mode === 'signup' ? '/api/v1/auth/signup' : '/api/v1/auth/login';
      await apiRequest(endpoint, {
        method: 'POST',
        body: {
          ...(mode === 'signup' ? { first_name: firstName.trim() } : {}),
          email: email.trim(),
          password,
        },
      });

      navigate(nextPath, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-md glass rounded-3xl p-8 shadow-glow-teal card-border">
        <p className="text-xs uppercase tracking-[0.22em] text-teal">ATS CV Maker</p>
        <h1 className="mt-3 text-3xl font-semibold text-white">
          {mode === 'login' ? 'Login' : 'Create account'}
        </h1>
        <p className="mt-2 text-slate-300 text-sm">
          {mode === 'login'
            ? 'Sign in to access your personal workspace.'
            : 'Sign up to start saving and managing your own data.'}
        </p>

        <form className="mt-6 space-y-4" onSubmit={submit}>
          {mode === 'signup' && (
            <label className="block">
              <span className="text-sm text-slate-300">First name</span>
              <input
                type="text"
                required
                maxLength={120}
                autoComplete="given-name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="mt-1 w-full rounded-xl bg-white/5 border border-white/15 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal/60"
              />
            </label>
          )}

          <label className="block">
            <span className="text-sm text-slate-300">Email</span>
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="mt-1 w-full rounded-xl bg-white/5 border border-white/15 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal/60"
            />
          </label>

          <label className="block">
            <span className="text-sm text-slate-300">Password</span>
            <input
              type="password"
              required
              minLength={8}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full rounded-xl bg-white/5 border border-white/15 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal/60"
            />
          </label>

          {mode === 'signup' && (
            <label className="block">
              <span className="text-sm text-slate-300">Confirm password</span>
              <input
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="mt-1 w-full rounded-xl bg-white/5 border border-white/15 px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-teal/60"
              />
            </label>
          )}

          {error && (
            <div className="rounded-xl border border-red-400/40 bg-red-500/10 px-4 py-3 text-sm text-red-100">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-teal text-ink px-4 py-3 font-semibold uppercase tracking-[0.08em] shadow-glow-teal disabled:opacity-60"
          >
            {loading ? 'Please wait...' : mode === 'login' ? 'Login' : 'Sign up'}
          </button>
        </form>

        <div className="mt-5 text-sm text-slate-300">
          {mode === 'login' ? 'No account yet?' : 'Already have an account?'}{' '}
          <button
            type="button"
            onClick={() => {
              setError('');
              setMode(mode === 'login' ? 'signup' : 'login');
            }}
            className="text-teal hover:underline"
          >
            {mode === 'login' ? 'Create one' : 'Login'}
          </button>
        </div>
      </div>
    </div>
  );
}
