# Discord Bot - Steam ID Onboarding Flow

## 🔄 Complete Flow

### STEP 1️⃣ New Member Joins Discord
```
👤 User joins Beredskaqet Discord server
↓
🔔 Discord sends guildMemberAdd event
↓
🤖 Bot triggers: events/memberJoin.js
↓
💬 Bot sends message to #mine_data channel:
   "Velkommen [USER]! For at få adgang skal du bekræfte din Steam ID.
    Brug: /steam-verify <steam_id>
    Hvor finder du din Steam ID? → https://steamid.io"
```

### STEP 2️⃣ Member Uses `/steam-verify` Command
```
👤 User types: /steam-verify 76561198111111111
↓
🤖 Bot triggers: commands/steam-verify.js
↓
✅ Validation:
   - Check format is 17 digits
   - Check Steam ID exists in database (DEMO_STEAM_IDS)
   - Check if verified before (optional)
↓
💾 Save to Airtable:
   - Discord ID
   - Steam ID
   - Player Name
   - CS2 Role (Carry/Support/Lurker/IGL)
   - Verified timestamp
↓
👑 Grant Discord Role:
   - Add "Beredskaqet Member" role
↓
✨ Success message to user (ephemeral):
   "✅ Steam ID Verificeret!
    Spiller: Luffemann
    Rolle: IGL
    Du har nu adgang til: #matchmager, #stats, leaderboard
    Næste skridt: /find-team eller beredskaqet.dk/app/"
```

---

## 📁 File Structure

```
E:\beredskaqet_V2\discord-bot\
├── bot.js                    # Main bot entry - loads events & commands
├── events/
│   ├── ready.js             # Bot startup - registers slash commands
│   └── memberJoin.js        # Triggered when new member joins
├── commands/
│   └── steam-verify.js      # /steam-verify <steam_id> command
├── handlers/
│   └── airtable.js          # Airtable API calls (save/fetch Steam IDs)
├── package.json             # Dependencies
├── .env.example             # Template (actual tokens in E:\.env)
└── FLOW.md                  # This file
```

---

## 🔧 Setup Requirements

### 1. Install Dependencies
```bash
cd E:\beredskaqet_V2\discord-bot
npm install
```

### 2. Add to E:\.env
```
DISCORD_BEREDSKAQET_TOKEN=your_bot_token_here
AIRTABLE_BASE_ID=appXXXXXXXXXXXXXX
AIRTABLE_PAT=patXXXXXXXXXXXXXX
```

### 3. Create Discord Bot
1. Go to Discord Developer Portal (https://discord.com/developers/applications)
2. Create new application "Beredskaqet"
3. Go to Bot section → Add Bot
4. Copy token → add to E:\.env as DISCORD_BEREDSKAQET_TOKEN
5. Enable intents:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Go to OAuth2 → URL Generator
7. Scopes: `bot`
8. Permissions: `Send Messages`, `Use Slash Commands`, `Manage Roles`
9. Copy generated URL → invite bot to server

### 4. Run Bot
```bash
npm start
```

---

## 🎯 Current State (DEMO)

- ✅ Bot joins server & listens for new members
- ✅ Auto-sends welcome message to #mine_data
- ✅ `/steam-verify` command validates format
- ✅ Demo Steam IDs work: 76561198111111111, 76561198222222222, 76561198333333333
- ⏳ TODO: Real Airtable integration (save to Members table)
- ⏳ TODO: Real role granting (need "Beredskaqet Member" role in Discord)

---

## 📊 Demo Test Sequence

1. **Add bot to Discord server**
   - Bot shows: "✅ Bot logged in as Beredskaqet#1234"
   - Bot registers slash commands

2. **New member joins**
   - Bot sends message in #mine_data: "Velkommen @NewUser! ..."

3. **New member uses `/steam-verify 76561198111111111`**
   - Bot responds: "✅ Steam ID Verificeret! Spiller: Luffemann, Rolle: IGL"

4. **Check Airtable** (when integrated)
   - New row in Members table with Discord ID, Steam ID, Player Name, Role, Timestamp

---

## 🚀 Next Steps (TODO)

1. **Real Airtable Integration**
   - Get AIRTABLE_BASE_ID from Beredskaqet base
   - Get Members table ID (currently hardcoded as "tblMembers")
   - Test saveSteamId() function

2. **Role Management**
   - Create "Beredskaqet Member" role in Discord
   - Auto-add role when Steam ID verified
   - Optional: add role based on CS2 Rank (Gold/Silver/etc)

3. **Duplicate Check**
   - Prevent same Steam ID being verified twice
   - Handle "already verified" case

4. **Error Handling**
   - Log to a #bot-logs channel instead of console
   - User-friendly error messages

5. **Admin Commands** (future)
   - `/admin-verify <user> <steam_id>` - admins can manually verify
   - `/admin-list-verified` - list all verified members
