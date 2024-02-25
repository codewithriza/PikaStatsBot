# Pika Stats Bot

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**Pika Stats Bot** is a Discord bot that provides statistics for Pika Network games, including Bedwars, Skywars, and more. It offers features like displaying player profiles, game stats, guild information, and daily vote reminders.

# Features

- Display Pika Network player profiles
- Show game statistics for Bedwars, Skywars, and more
- Provide information about Pika Network guilds
- Send daily vote reminders to users

# How it Works

The bot uses the following API endpoints from Pika Network to gather data:

###  Retrieves information about a Pika Network guild 
- ```https://stats.pika-network.net/api/clans/{guild_name}```

---
###  Retrieves leaderboard data for a player in a specific game mode.
- `https://stats.pika-network.net/api/profile/{player_name}/leaderboard?type={game_type}&interval={interval}&mode={mode}`
---
### Retrieves a player's profile information.  
- `https://stats.pika-network.net/api/profile/{player_name}`
---

# Usage

To use the bot, invite it to your Discord server using [this invite link](https://discord.com/oauth2/authorize?client_id=1209050248958312448&permissions=551903422464&scope=bot).

Once the bot is in your server, you can use the following commands:

- `/bw [player_name] [interval] [mode]`: Get Bedwars stats for a player.
- `/sw [player_name] [interval] [mode]`: Get Skywars stats for a player.
- `/friends [player_name]`: List a player's friends.
- `/guild-info [guild_name]`: Get information about a Pika Network guild.

For more commands, use `/help`.

# Contributing

We welcome contributions from the community! If you'd like to contribute to the bot, please check out our [contribution guidelines](CONTRIBUTING.md).

# License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

**Note**: Pika Stats Bot is not affiliated nor partnered with PikaNetwork!
---
[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1209050248958312448&permissions=551903422464&scope=bot)
[![X](https://img.shields.io/badge/X-%23000000.svg?style=for-the-badge&logo=X&logoColor=white)](https://twitter.com/PikachuStats)
