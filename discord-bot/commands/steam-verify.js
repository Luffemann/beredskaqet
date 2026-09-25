const { SlashCommandBuilder } = require('discord.js');
const axios = require('axios');

// Demo Steam ID database (would be in Airtable in production)
const DEMO_STEAM_IDS = {
  '76561198111111111': { name: 'Luffemann', role: 'IGL' },
  '76561198222222222': { name: 'Player2', role: 'Lurker' },
  '76561198333333333': { name: 'Player3', role: 'Support' },
};

module.exports = {
  data: new SlashCommandBuilder()
    .setName('steam-verify')
    .setDescription('Verificer din Steam ID for at få adgang til Beredskaqet')
    .addStringOption(option =>
      option
        .setName('steam_id')
        .setDescription('Dit 17-cifrede Steam ID (fx: 76561198111111111)')
        .setRequired(true)
    ),

  execute: async (interaction, client) => {
    try {
      const steamId = interaction.options.getString('steam_id').trim();

      // Validate Steam ID format (17 digits)
      if (!/^\d{17}$/.test(steamId)) {
        return interaction.reply({
          content: `❌ **Ugyldigt Steam ID format!**\nSteam ID skal være 17 cifre (fx: 76561198111111111)\nDu skrev: \`${steamId}\` (${steamId.length} cifre)`,
          ephemeral: true,
        });
      }

      // Check if Steam ID exists in demo database
      const steamData = DEMO_STEAM_IDS[steamId];
      if (!steamData) {
        return interaction.reply({
          content: `❌ **Steam ID ikke fundet!**\nSteam ID \`${steamId}\` er ikke registreret i vores system.\n\n**Hvad skal du gøre?**\n1. Tjek at du skrev ID'et korrekt (uden anførselstegn)\n2. Gå til https://steamid.io og søg efter dit Steam-navn\n3. Prøv igen med det rigtige ID`,
          ephemeral: true,
        });
      }

      // Save to Airtable (TODO: implement)
      console.log(`✅ ${interaction.user.tag} verified Steam ID: ${steamId} (${steamData.name})`);

      // Grant role based on Steam data
      try {
        const beredskaqetRole = interaction.guild.roles.cache.find(r => r.name === 'Beredskaqet Member');
        if (beredskaqetRole) {
          await interaction.member.roles.add(beredskaqetRole);
        }
      } catch (roleError) {
        console.error('Error adding role:', roleError);
      }

      // Send success message
      const successEmbed = {
        color: 0x00FF00,
        title: '✅ Steam ID Verificeret!',
        description: `**Spiller:** ${steamData.name}\n**Steam ID:** \`${steamId}\`\n**Rolle:** ${steamData.role}`,
        fields: [
          {
            name: '📊 Du har nu adgang til:',
            value: '✅ #matchmager\n✅ #stats & leaderboard\n✅ Din personlige profil',
            inline: false,
          },
          {
            name: '🎮 Næste skridt:',
            value: 'Find et match med `/find-team` eller se stats på https://beredskaqet.dk/app/',
            inline: false,
          },
        ],
        timestamp: new Date(),
      };

      await interaction.reply({
        embeds: [successEmbed],
        ephemeral: true,
      });
    } catch (error) {
      console.error('Error in steam-verify command:', error);
      await interaction.reply({
        content: '❌ Der opstod en fejl ved verificering.',
        ephemeral: true,
      });
    }
  },
};
