import { useState } from 'react';
import { ThemeToggle } from './ThemeToggle';

interface LoginPageProps {
  onLoginSuccess: (token: string, playerName: string) => void;
}

const DEMO_STEAM_IDS = [
  { id: '76561198111111111', name: 'Luffemann' },
  { id: '76561198222222222', name: 'Player2' },
  { id: '76561198333333333', name: 'Player3' },
];

export const LoginPage = ({ onLoginSuccess }: LoginPageProps) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [steamId, setSteamId] = useState('');

  const handleLogin = async (id: string) => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ steam_id: id }),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('player_name', data.player_name);
      onLoginSuccess(data.access_token, data.player_name);
    } catch (err) {
      setError('Login failed. Make sure API server is running at http://localhost:8000');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark to-darker text-gray-100 flex flex-col">
      {/* Header */}
      <div className="flex justify-between items-center p-4 sm:p-6 border-b border-blue-900">
        <h1 className="text-2xl sm:text-3xl font-bold text-primary">BEREDSKAQET</h1>
        <ThemeToggle />
      </div>

      {/* Login Container */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-card border border-blue-900 rounded-lg p-6 sm:p-8">
          <h2 className="text-2xl font-bold text-primary mb-2 text-center">Steam Login</h2>
          <p className="text-gray-400 text-center mb-6">Select your account or use Steam ID</p>

          {error && (
            <div className="bg-red-900 bg-opacity-30 border border-red-600 rounded p-3 mb-4">
              <p className="text-red-200 text-sm">{error}</p>
            </div>
          )}

          {/* Demo Users */}
          <div className="mb-6 space-y-2">
            {DEMO_STEAM_IDS.map((user) => (
              <button
                key={user.id}
                onClick={() => handleLogin(user.id)}
                disabled={loading}
                className="w-full py-3 px-4 bg-gradient-to-r from-primary to-blue-500 hover:from-blue-400 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed rounded font-semibold transition"
              >
                {loading ? 'Logging in...' : user.name}
              </button>
            ))}
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-blue-900"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-card text-gray-400">Or enter Steam ID</span>
            </div>
          </div>

          {/* Custom Steam ID Input */}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="76561198..."
              value={steamId}
              onChange={(e) => setSteamId(e.target.value)}
              className="flex-1 px-4 py-3 bg-dark border border-blue-900 rounded text-gray-100 placeholder-gray-500 focus:outline-none focus:border-primary"
            />
            <button
              onClick={() => handleLogin(steamId)}
              disabled={loading || !steamId}
              className="px-4 py-3 bg-primary text-dark font-semibold rounded hover:bg-blue-400 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              Login
            </button>
          </div>

          {/* Footer */}
          <p className="text-gray-500 text-xs text-center mt-6">
            API: http://localhost:8000 | Demo mode (development)
          </p>
        </div>
      </div>
    </div>
  );
};
