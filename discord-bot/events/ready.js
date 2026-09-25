const { REST, Routes } = require('discord.js');
const fs = require('fs');
const path = require('path');

module.exports = {
  name: 'ready',
  once: true,
  execute: async (client) => {
    console.log(`✅ Bot logged in as ${client.user.tag}`);

    // Register slash commands
    const commands = [];
    const commandsPath = path.join(__dirname, '..', 'commands');

    if (fs.existsSync(commandsPath)) {
      const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));

      for (const file of commandFiles) {
        const filePath = path.join(commandsPath, file);
        const command = require(filePath);
        if (command.data) {
          commands.push(command.data.toJSON());
        }
      }
    }

    // Deploy slash commands to all guilds
    const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_BEREDSKAQET_TOKEN);

    try {
      console.log(`🔄 Registering ${commands.length} slash commands...`);

      for (const guild of client.guilds.cache.values()) {
        await rest.put(Routes.applicationGuildCommands(client.user.id, guild.id), {
          body: commands,
        });
      }

      console.log(`✅ Slash commands registered!`);
    } catch (error) {
      console.error('❌ Error registering commands:', error);
    }
  },
};
