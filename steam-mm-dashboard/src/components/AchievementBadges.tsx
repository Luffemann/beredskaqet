interface Badge {
  id: string;
  name: string;
  icon: string;
  description: string;
  unlocked: boolean;
  unlockedDate?: string;
}

const BADGE_LIBRARY: Badge[] = [
  { id: 'carry', name: 'CARRY', icon: '🔫', description: 'K/D > 2.0', unlocked: false },
  { id: 'support', name: 'SUPPORT', icon: '🛡️', description: 'Assists > 8', unlocked: false },
  { id: 'lurker', name: 'LURKER', icon: '👁️', description: 'Entry Frags > 40%', unlocked: false },
  { id: 'igl', name: 'IGL', icon: '🎯', description: 'MVPs >= 3', unlocked: false },
  { id: '100kills', name: '100 Kills', icon: '💥', description: 'Career milestone', unlocked: false },
  { id: '60hs', name: 'Precision', icon: '💯', description: 'HS% > 60%', unlocked: false },
  { id: 'streak', name: 'On Fire', icon: '🔥', description: '3-win streak', unlocked: false },
  { id: 'duo', name: 'Best Duo', icon: '👥', description: '85%+ win rate', unlocked: false },
];

interface AchievementBadgesProps {
  unlockedBadges?: string[];
}

export const AchievementBadges = ({ unlockedBadges = [] }: AchievementBadgesProps) => {
  const badges = BADGE_LIBRARY.map((badge) => ({
    ...badge,
    unlocked: unlockedBadges.includes(badge.id),
  }));

  return (
    <div className="bg-card border border-blue-900 rounded-lg p-4">
      <h3 className="text-primary font-bold mb-4">Achievements</h3>

      <div className="grid grid-cols-4 gap-3">
        {badges.map((badge) => (
          <div
            key={badge.id}
            className={`flex flex-col items-center p-3 rounded-lg border-2 transition ${
              badge.unlocked
                ? 'border-yellow-500 bg-yellow-500/10'
                : 'border-gray-700 bg-gray-900/30 opacity-50'
            }`}
          >
            <div className="text-3xl mb-2">{badge.icon}</div>
            <div className="text-xs font-bold text-center text-primary">{badge.name}</div>
            <div className="text-xs text-gray-400 text-center mt-1">{badge.description}</div>
          </div>
        ))}
      </div>

      <p className="text-gray-400 text-xs mt-4">
        🏆 Unlocked: {badges.filter((b) => b.unlocked).length} / {badges.length}
      </p>
    </div>
  );
};
