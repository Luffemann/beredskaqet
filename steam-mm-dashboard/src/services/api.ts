/**
 * Flask backend API client
 * Points to: https://beredskaqet.dk/api-server
 */

const API_URL = 'https://beredskaqet.dk/api-server';

export interface PlayerStats {
  player_name: string;
  total_matches: number;
  recent_matches: any[];
  avg_kills: number;
  avg_kd: number;
}

export interface LoginResponse {
  access_token: string;
  player_name: string;
  avatar?: string;
}

export interface ProgressionData {
  progression: Array<{
    match: number;
    kills: number;
    kd: number;
    hs_pct: number;
    adr: number;
    date: string;
  }>;
  player: string;
}

export interface H2HData {
  h2h: Array<{
    opponent: string;
    record: string;
    win_rate: number;
  }>;
  player: string;
}

export interface AchievementsData {
  badges: string[];
  player: string;
  total: number;
}

// Login
export const login = async (steamId: string): Promise<LoginResponse> => {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ steam_id: steamId }),
  });

  if (!response.ok) throw new Error('Login failed');
  return response.json();
};

// Get player stats
export const getPlayerStats = async (playerName: string): Promise<PlayerStats> => {
  const response = await fetch(`${API_URL}/player/${playerName}`);
  if (!response.ok) throw new Error('Failed to fetch player stats');
  return response.json();
};

// Get leaderboard
export const getLeaderboard = async () => {
  const response = await fetch(`${API_URL}/leaderboard`);
  if (!response.ok) throw new Error('Failed to fetch leaderboard');
  return response.json();
};

// Get progression
export const getProgression = async (playerName: string): Promise<ProgressionData> => {
  const response = await fetch(`${API_URL}/player/${playerName}/progression`);
  if (!response.ok) throw new Error('Failed to fetch progression');
  return response.json();
};

// Get H2H
export const getH2H = async (playerName: string): Promise<H2HData> => {
  const response = await fetch(`${API_URL}/player/${playerName}/h2h`);
  if (!response.ok) throw new Error('Failed to fetch H2H');
  return response.json();
};

// Get achievements
export const getAchievements = async (playerName: string): Promise<AchievementsData> => {
  const response = await fetch(`${API_URL}/player/${playerName}/achievements`);
  if (!response.ok) throw new Error('Failed to fetch achievements');
  return response.json();
};
