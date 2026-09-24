interface H2HRecord {
  opponent: string;
  wins: number;
  losses: number;
  winRate: number;
}

interface HeadToHeadDisplayProps {
  records: H2HRecord[];
}

export const HeadToHeadDisplay = ({ records }: HeadToHeadDisplayProps) => {
  return (
    <div className="bg-card border border-blue-900 rounded-lg p-4">
      <h3 className="text-primary font-bold mb-4">Head-to-Head</h3>

      <div className="space-y-3">
        {records.length === 0 ? (
          <p className="text-gray-400 text-sm">No H2H data yet</p>
        ) : (
          records.map((record, idx) => (
            <div key={idx} className="border-l-2 border-blue-900 pl-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-200 font-semibold">{record.opponent}</span>
                <span className={record.winRate > 50 ? 'text-green-400' : 'text-red-400'}>
                  {record.wins}-{record.losses}
                </span>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <div className="flex-1 bg-gray-800 rounded-full h-1.5">
                  <div
                    className={record.winRate > 50 ? 'bg-green-500' : 'bg-red-500'}
                    style={{ width: `${record.winRate}%`, height: '100%' }}
                  ></div>
                </div>
                <span className="text-xs text-gray-400 w-10">{record.winRate.toFixed(0)}%</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
