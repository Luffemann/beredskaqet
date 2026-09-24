import type { PlayerStats } from '../services/airtable';

interface MapStats {
  map: string;
  matches: number;
  avgKD: number;
  avgHS: number;
  avgADR: number;
  wins: number;
  winRate: number;
}

interface MapStatsBreakdownProps {
  data: PlayerStats[];
}

export const MapStatsBreakdown = ({ data }: MapStatsBreakdownProps) => {
  if (!data || data.length === 0) return <div>No map data</div>;

  // Group by map
  const mapGroups = data.reduce(
    (acc, match) => {
      const map = match.Map || 'Unknown';
      if (!acc[map]) {
        acc[map] = [];
      }
      acc[map].push(match);
      return acc;
    },
    {} as Record<string, PlayerStats[]>
  );

  // Calculate stats per map
  const mapStats: MapStats[] = Object.entries(mapGroups).map(([map, matches]) => ({
    map,
    matches: matches.length,
    avgKD: matches.reduce((sum, m) => sum + m.Kills / (m.Death + 1), 0) / matches.length,
    avgHS: matches.reduce((sum, m) => sum + m['HS%'], 0) / matches.length,
    avgADR: matches.reduce((sum, m) => sum + m.ADR, 0) / matches.length,
    wins: matches.reduce((sum, m) => sum + m['Vund._rund'], 0),
    winRate: (matches.reduce((sum, m) => sum + m['Vund._rund'], 0) / (matches.length || 1)) * 100,
  }));

  return (
    <div className="bg-card border border-blue-900 rounded-lg p-4">
      <h3 className="text-primary font-bold mb-4">Map-Specific Stats</h3>

      <div className="space-y-3">
        {mapStats.length === 0 ? (
          <p className="text-gray-400 text-sm">No map data yet</p>
        ) : (
          mapStats.map((map) => (
            <div key={map.map} className="border-l-2 border-blue-900 pl-3 pb-3">
              <div className="flex justify-between items-baseline mb-2">
                <span className="font-bold text-gray-200">{map.map}</span>
                <span className="text-xs text-gray-400">{map.matches} matches</span>
              </div>
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div>
                  <div className="text-gray-400">K/D</div>
                  <div className="text-primary font-bold">{map.avgKD.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-gray-400">HS%</div>
                  <div className="text-primary font-bold">{map.avgHS.toFixed(1)}%</div>
                </div>
                <div>
                  <div className="text-gray-400">ADR</div>
                  <div className="text-primary font-bold">{map.avgADR.toFixed(1)}</div>
                </div>
                <div>
                  <div className="text-gray-400">W%</div>
                  <div className={`font-bold ${map.winRate > 50 ? 'text-green-400' : 'text-red-400'}`}>
                    {map.winRate.toFixed(0)}%
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
