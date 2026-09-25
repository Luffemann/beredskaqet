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

    console.log(`[DEBUG] Looking for commands in: ${commandsPath}`);
    console.log(`[DEBUG] __dirname: ${__dirname}`);

    if (fs.existsSync(commandsPath)) {
      const commandFiles = fs.readdirSync(commandsPath).filter(file => file.endsWith('.js'));
      console.log(`[DEBUG] Found ${commandFiles.length} command files: ${commandFiles.join(', ')}`);

      for (const file of commandFiles) {
        const filePath = path.join(commandsPath, file);
        try {
          const command = require(filePath);
          if (command.data) {
            commands.push(command.data.toJSON());
            console.log(`[DEBUG] ✓ Loaded command: ${file}`);
          }
        } catch (err) {
          console.error(`[DEBUG] ✗ Failed to load ${file}:`, err.message);
        }
      }
    } else {
      console.error(`[DEBUG] ✗ Commands path does not exist: ${commandsPath}`);
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
