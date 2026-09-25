const axios = require('axios');

const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID;
const AIRTABLE_TABLE_ID = 'tblMembers'; // TODO: get from .env
const AIRTABLE_PAT = process.env.AIRTABLE_PAT;

async function saveSteamId(discordId, steamId, playerName, role, discordUsername) {
  try {
    const response = await axios.patch(
      `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${AIRTABLE_TABLE_ID}`,
      {
        records: [
          {
            fields: {
              'Discord ID': discordId,
              'Steam ID': steamId,
              'Player Name': playerName,
              'CS2 Role': role,
              'Discord Username': discordUsername,
              'Verified': true,
              'Verified Date': new Date().toISOString(),
            },
          },
        ],
      },
      {
        headers: {
          Authorization: `Bearer ${AIRTABLE_PAT}`,
          'Content-Type': 'application/json',
        },
      }
    );

    console.log(`✅ [Airtable] Saved Steam ID for ${discordId}`);
    return response.data;
  } catch (error) {
    console.error(`❌ [Airtable] Error saving Steam ID:`, error.response?.data || error.message);
    throw error;
  }
}

async function getSteamIdByDiscordId(discordId) {
  try {
    const response = await axios.get(
      `https://api.airtable.com/v0/${AIRTABLE_BASE_ID}/${AIRTABLE_TABLE_ID}`,
      {
        params: {
          filterByFormula: `{Discord ID} = '${discordId}'`,
        },
        headers: {
          Authorization: `Bearer ${AIRTABLE_PAT}`,
        },
      }
    );

    if (response.data.records.length === 0) {
      return null;
    }

    return response.data.records[0].fields;
  } catch (error) {
    console.error(`❌ [Airtable] Error fetching Steam ID:`, error.message);
    return null;
  }
}

module.exports = {
  saveSteamId,
  getSteamIdByDiscordId,
};
