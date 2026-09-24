import { useState, useEffect, useMemo } from 'react';
import { fetchPlayerStats } from '../services/airtable';
import type { PlayerStats } from '../services/airtable';
import { KDTrendChart } from './KDTrendChart';
import { HSProgressBar } from './HSProgressBar';
import { HeadToHeadDisplay } from './HeadToHeadDisplay';
import { AchievementBadges } from './AchievementBadges';
import { MapStatsBreakdown } from './MapStatsBreakdown';
import { ThemeToggle } from './ThemeToggle';

interface DashboardProps {
  playerName: string;
  onLogout?: () => void;
}

export const Dashboard = ({ playerName, onLogout }: DashboardProps) => {
  const [stats, setStats] = useState<PlayerStats[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'progression' | 'h2h' | 'achievements'>('overview');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadStats = async () => {
      setLoading(true);
      const data = await fetchPlayerStats(playerName);
      setStats(data);
      setLoading(false);
    };
    loadStats();
  }, [playerName]);

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen text-primary">Loading...</div>;
  }

  // Memoize computed values for performance
  const memoStats = useMemo(() => ({
    latestMatch: stats[0],
    avgKills: stats.length > 0 ? (stats.reduce((sum, s) => sum + s.Kills, 0) / stats.length).toFixed(1) : 0,
    avgKD: stats.length > 0 ? (stats.reduce((sum, s) => sum + (s.Kills / (s.Death + 1)), 0) / stats.length).toFixed(2) : 0,
  }), [stats]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark to-darker text-gray-100">
      {/* Header with Theme Toggle & Logout */}
      <div className="flex justify-between items-center p-4 sm:p-6 border-b border-blue-900">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-primary">BEREDSKAQET</h1>
          <p className="text-gray-400 text-xs sm:text-sm">Welcome, {playerName}</p>
        </div>
        <div className="flex gap-4 items-center">
          <ThemeToggle />
          {onLogout && (
            <button
              onClick={onLogout}
              className="px-4 py-2 bg-red-900 hover:bg-red-800 rounded text-sm font-semibold transition"
            >
              Logout
            </button>
          )}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-4 p-4 sm:p-6">
        <div className="bg-card border border-blue-900 rounded-lg p-3 sm:p-4">
          <h3 className="text-primary text-xs sm:text-sm font-bold uppercase">Latest Kills</h3>
          <div className="text-2xl sm:text-3xl font-bold mt-2">{memoStats.latestMatch?.Kills || 0}</div>
          <div className="text-gray-400 text-xs sm:text-sm">Latest match</div>
        </div>
        <div className="bg-card border border-blue-900 rounded-lg p-3 sm:p-4">
          <h3 className="text-primary text-xs sm:text-sm font-bold uppercase">Avg K/D</h3>
          <div className="text-2xl sm:text-3xl font-bold mt-2">{memoStats.avgKD}</div>
          <div className="text-gray-400 text-xs sm:text-sm">{stats.length}</div>
        </div>
        <div className="bg-card border border-blue-900 rounded-lg p-3 sm:p-4">
          <h3 className="text-primary text-xs sm:text-sm font-bold uppercase">Avg HS%</h3>
          <div className="text-2xl sm:text-3xl font-bold mt-2">
            {stats.length > 0 ? (stats.reduce((sum, s) => sum + s['HS%'], 0) / stats.length).toFixed(1) : 0}%
          </div>
          <div className="text-gray-400 text-xs sm:text-sm">Precision</div>
        </div>
        <div className="hidden sm:flex bg-card border border-blue-900 rounded-lg p-4">
          <h3 className="text-primary text-sm font-bold uppercase">ADR</h3>
          <div className="text-3xl font-bold mt-2">
            {stats.length > 0 ? (stats.reduce((sum, s) => sum + s.ADR, 0) / stats.length).toFixed(1) : 0}
          </div>
          <div className="text-gray-400 text-sm">Avg/rnd</div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-blue-900 px-4 sm:px-6 overflow-x-auto">
        <div className="flex gap-2 sm:gap-8">
          {(['overview', 'progression', 'h2h', 'achievements'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-2 sm:px-4 font-semibold capitalize text-xs sm:text-base whitespace-nowrap ${
                activeTab === tab
                  ? 'text-primary border-b-2 border-primary'
                  : 'text-gray-400 hover:text-primary'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-4 sm:p-6">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4 sm:gap-6">
            <KDTrendChart data={stats} />
            <HSProgressBar data={stats} />
            <MapStatsBreakdown data={stats} />
            <AchievementBadges unlockedBadges={['carry', '100kills']} />
          </div>
        )}
        {activeTab === 'progression' && (
          <div>
            <h2 className="text-2xl font-bold text-primary mb-4">Progression</h2>
            <KDTrendChart data={stats} />
            <div className="mt-6">
              <HSProgressBar data={stats} />
            </div>
          </div>
        )}
        {activeTab === 'h2h' && (
          <div>
            <h2 className="text-2xl font-bold text-primary mb-4">Head-to-Head</h2>
            <HeadToHeadDisplay
              records={[
                { opponent: 'Player2', wins: 3, losses: 2, winRate: 60 },
                { opponent: 'Player3', wins: 4, losses: 1, winRate: 80 },
              ]}
            />
          </div>
        )}
        {activeTab === 'achievements' && (
          <div>
            <h2 className="text-2xl font-bold text-primary mb-4">Achievements</h2>
            <AchievementBadges unlockedBadges={['carry', '100kills', '60hs', 'duo']} />
          </div>
        )}
      </div>
    </div>
  );
};
