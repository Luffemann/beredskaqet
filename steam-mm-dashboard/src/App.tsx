import { useState, useEffect } from 'react';
import { Dashboard } from './components/Dashboard';
import { LoginPage } from './components/LoginPage';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [playerName, setPlayerName] = useState('');

  useEffect(() => {
    // Check if user already logged in (token in localStorage)
    const savedToken = localStorage.getItem('token');
    const savedName = localStorage.getItem('player_name');
    if (savedToken && savedName) {
      setPlayerName(savedName);
      setIsLoggedIn(true);
    }
  }, []);

  const handleLoginSuccess = (_newToken: string, newPlayerName: string) => {
    setPlayerName(newPlayerName);
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('player_name');
    setPlayerName('');
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  return <Dashboard playerName={playerName} onLogout={handleLogout} />;
}

export default App;
