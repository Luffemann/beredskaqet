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

      // Send welcome message to #mine_data with Steam OAuth button
      const { ActionRowBuilder, ButtonBuilder, ButtonStyle } = require('discord.js');

      const steamButton = new ButtonBuilder()
        .setLabel('🔓 Login med Steam')
        .setStyle(ButtonStyle.Link)
        .setURL(`https://beredskaqet.dk/api-server/auth/steam/login?discord_id=${member.id}&guild_id=${member.guild.id}`);

      const row = new ActionRowBuilder().addComponents(steamButton);

      const welcomeMessage = await channel.send({
        content: `👋 **Velkommen ${member}!**\n\nFor at få fuld adgang til Beredskaqet CS2 Club skal du bekræfte din Steam ID.\n\n**Klik knappen nedenfor for at logge ind med Steam:**`,
        components: [row]
      });

      console.log(`✅ Welcome message sent to ${member.user.tag} in #mine_data`);
    } catch (error) {
      console.error(`❌ Error sending welcome message:`, error);
    }
  },
};
