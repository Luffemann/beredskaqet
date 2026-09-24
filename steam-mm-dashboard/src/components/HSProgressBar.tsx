import type { PlayerStats } from '../services/airtable';

interface HSProgressBarProps {
  data: PlayerStats[];
}

export const HSProgressBar = ({ data }: HSProgressBarProps) => {
  if (!data || data.length === 0) return <div>No data</div>;

  const avgHS = data.reduce((sum, s) => sum + s['HS%'], 0) / data.length;
  const latestHS = data[0]?.['HS%'] || 0;
  const maxHS = Math.max(...data.map((s) => s['HS%']));

  const getColor = (hs: number) => {
    if (hs > 60) return 'bg-green-500';
    if (hs > 50) return 'bg-blue-500';
    if (hs > 40) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-card border border-blue-900 rounded-lg p-4">
      <h3 className="text-primary font-bold mb-4">Headshot % Progression</h3>

      <div className="space-y-4">
        {/* Average */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-300">Average</span>
            <span className="text-primary font-bold">{avgHS.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getColor(avgHS)}`}
              style={{ width: `${Math.min(avgHS, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Latest */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-300">Latest Match</span>
            <span className="text-primary font-bold">{latestHS.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${getColor(latestHS)}`}
              style={{ width: `${Math.min(latestHS, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Career High */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-300">Career High</span>
            <span className="text-primary font-bold">{maxHS.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2">
            <div className="h-2 rounded-full bg-yellow-400" style={{ width: '100%' }}></div>
          </div>
        </div>
      </div>

      <p className="text-gray-400 text-xs mt-4">
        💡 Tip: Maintain 50%+ HS% for consistent high performance
      </p>
    </div>
  );
};
