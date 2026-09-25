module.exports = {
  name: 'guildMemberAdd',
  execute: async (member, client) => {
    try {
      // Only send message if not a bot
      if (member.user.bot) return;

      // Get the mine_data channel
      const channel = member.guild.channels.cache.get('1481660798848991322');
      if (!channel) {
        console.error('❌ mine_data channel not found (1481660798848991322)');
        return;
      }

      // Send welcome message to #mine_data with Steam ID prompt
      const welcomeMessage = await channel.send({
        content: `👋 **Velkommen ${member}!**\n\nFor at få fuld adgang til Beredskaqet CS2 Club skal du bekræfte din Steam ID.\n\n**Brug denne kommando:**\n\`/steam-verify <din_steam_id>\`\n\n**Hvor finder du din Steam ID?**\n→ Gå til https://steamid.io\n→ Søg efter dit Steam-navn\n→ Kopier det 17-cifrede tal (ID3 eller ID64)\n\n**Eksempel:**\n\`/steam-verify 76561198111111111\`\n\nEfter verificering får du adgang til matcher, stats og leaderboard! 🎮`,
        reply: { messageReference: null }
      });

      console.log(`✅ Welcome message sent to ${member.user.tag} in #mine_data`);
    } catch (error) {
      console.error(`❌ Error sending welcome message:`, error);
    }
  },
};
