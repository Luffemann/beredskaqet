import axios from 'axios';

const AIRTABLE_BASE_ID = 'appZh8kPulBOY571R';
const AIRTABLE_PAT = import.meta.env.VITE_AIRTABLE_PAT || '';

const api = axios.create({
  baseURL: `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}`,
  headers: {
    Authorization: `Bearer ${AIRTABLE_PAT}`,
    'Content-Type': 'application/json',
  },
});

export interface PlayerStats {
  Spiller: string;
  Kills: number;
  Death: number;
  Assist: number;
  'HS%': number;
  ADR: number;
  'Vund._rund': number;
  'Tabt_rund': number;
  Map: string;
  DATO: string;
}

export interface LeaderboardEntry {
  Spiller: string;
  'Antal kampe': number;
  'Kills total': number;
  'K/D Ratio': number;
  'Endelig Score': number;
  'CARRY_Score': number;
  'SUPPORT_Score': number;
}

// Fetch player personal stats
export const fetchPlayerStats = async (playerName: string): Promise<PlayerStats[]> => {
  try {
    const response = await api.get(`Input%20Data?filterByFormula={Spiller}="${playerName}"`);
    return response.data.records.map((r: any) => r.fields);
  } catch (error) {
    console.error('Fetch player stats error:', error);
    return [];
  }
};

// Fetch leaderboard
export const fetchLeaderboard = async (): Promise<LeaderboardEntry[]> => {
  try {
    const response = await api.get('LeaderBoard?maxRecords=100&sort=[{"field":"Endelig Score","direction":"desc"}]');
    return response.data.records.map((r: any) => r.fields);
  } catch (error) {
    console.error('Fetch leaderboard error:', error);
    return [];
  }
};

// Fetch head-to-head
export const fetchH2H = async (player1: string, player2: string) => {
  try {
    const response = await api.get(`Head_to_Head?filterByFormula=OR({Player1}="${player1}",{Player1}="${player2}")`);
    return response.data.records.map((r: any) => r.fields);
  } catch (error) {
    console.error('Fetch H2H error:', error);
    return [];
  }
};

export default api;
