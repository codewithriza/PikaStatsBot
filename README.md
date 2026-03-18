# 🎮 PikaStatsBot

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://discordpy.readthedocs.io/)
[![Stars](https://img.shields.io/github/stars/codewithriza/PikaStatsBot?style=social)](https://github.com/codewithriza/PikaStatsBot)

**The ultimate Pika Network statistics Discord bot** — Track player stats, compare players, monitor guilds, view skins, and much more!

[**Invite Bot**](https://discord.com/oauth2/authorize?client_id=1209050248958312448&permissions=551903422464&scope=bot%20applications.commands) •
[**Report Bug**](https://github.com/codewithriza/PikaStatsBot/issues) •
[**Request Feature**](https://github.com/codewithriza/PikaStatsBot/issues)

</div>

---

## ✨ Features

### 🎮 10+ Game Mode Statistics
Get detailed stats with **auto-calculated ratios** (KDR, WLR, FKDR, arrow accuracy) for:

| Game Mode | Command | Modes Available |
|-----------|---------|-----------------|
| 🛏️ BedWars | `/bw` | Solo, Doubles, 3v3v3v3, 4v4v4v4, Ranked |
| ⚔️ SkyWars | `/sw` | Solo, Doubles, Mega, Ranked |
| 🥊 Unranked Practice | `/practice` | Boxing, NoDebuff, Gapple, Sumo, BuildUHC, Combo, Debuff, Fist, Spleef |
| 🏆 Ranked Practice | `/ranked` | Boxing, NoDebuff, Gapple, Sumo, BuildUHC, Combo, Debuff, Fist, Spleef |
| ❤️ Lifesteal | `/lifesteal` | All Modes |
| 🗡️ KitPvP | `/kitpvp` | All Modes |
| 🌲 Survival | `/survival` | All Modes |
| 🏝️ OP Skyblock | `/opskyblock` | All Modes |
| 🌴 Classic Skyblock | `/classicskyblock` | All Modes |
| ⚡ OP Factions | `/opfactions` | All Modes |

All stats support **4 time intervals**: Total, Monthly, Weekly, Daily.

### 👤 Rich Player Profiles
- **Rank & Level** with progress bar
- **Online status** detection
- **Guild membership** info
- **Verification badges** (Discord, Email, Booster)
- **Minecraft avatar** display

### ⚔️ Player Comparison
- Compare **any two players** side by side
- Color-coded indicators (🟢 Better, 🔴 Worse, 🟡 Tied)
- Auto-calculated **ratio comparisons**
- Quick shortcuts: `/bw-compare`, `/sw-compare`

### 🏰 Guild System
- **Guild info** — Owner, level, creation date, member count
- **Member list** — Full guild roster
- **Guild tracking** — Real-time notifications when members join/leave
- Background monitoring every 5 minutes

### 🎨 Skin & Avatar Viewer
- **Full body render** of Minecraft skins
- **3D head render**
- **2D face avatar**
- **Download links** for all formats

### 🔧 Utility Features
- **Interactive help menu** with dropdown categories
- **Bot statistics** — Server count, uptime, latency
- **Server info** — Discord server details
- **Vote reminders** — Configurable daily DM reminders
- **Ping checker** — WebSocket & API latency

---

## 📸 Screenshots

<details>
<summary>Click to view screenshots</summary>

### Stats Command
```
/bw PlayerName total solo
```
Shows BedWars stats with KDR, WLR, FKDR ratios, arrow accuracy, and leaderboard rankings.

### Player Comparison
```
/compare Player1 Player2 bedwars total ALL_MODES
```
Side-by-side comparison with color-coded indicators.

### Player Profile
```
/profile PlayerName
```
Rich profile with rank, level progress bar, guild info, and online status.

### Guild Info
```
/guild GuildName
```
Complete guild information with member roster.

</details>

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **Discord Bot Token** — [Create one](https://discord.com/developers/applications)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/codewithriza/PikaStatsBot.git
   cd PikaStatsBot
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r bot/requirements.txt
   ```

4. **Configure the bot**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_bot_token_here
   ```

5. **Run the bot**
   ```bash
   python -m bot.bot
   ```

### Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a **New Application**
3. Go to **Bot** → Click **Add Bot**
4. Copy the **Token** and paste it in your `.env` file
5. Enable these **Privileged Gateway Intents**:
   - ✅ Message Content Intent
6. Go to **OAuth2** → **URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Embed Links`, `Read Message History`, `Use External Emojis`
7. Use the generated URL to invite the bot to your server

---

## 📁 Project Structure

```
PikaStatsBot/
├── bot/
│   ├── __init__.py
│   ├── bot.py              # Main bot entry point & setup
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   ├── cogs/
│   │   ├── __init__.py
│   │   ├── stats.py        # Game stats commands (10+ game modes)
│   │   ├── profile.py      # Profile, friends, skin, avatar commands
│   │   ├── guild.py        # Guild info, members, tracking commands
│   │   ├── compare.py      # Player comparison commands
│   │   └── utility.py      # Help, ping, vote, bot info commands
│   └── utils/
│       ├── __init__.py
│       ├── api.py           # Async Pika Network API wrapper with caching
│       └── embeds.py        # Embed builder utilities
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
├── CONTRIBUTING.md          # Contribution guidelines
├── LICENSE                  # MIT License
└── README.md                # This file
```

---

## 📋 All Commands

### 🎮 Game Stats
| Command | Description |
|---------|-------------|
| `/bw <player> [interval] [mode]` | BedWars statistics |
| `/sw <player> [interval] [mode]` | SkyWars statistics |
| `/practice <player> [interval] [mode]` | Unranked Practice statistics |
| `/ranked <player> [interval] [mode]` | Ranked Practice statistics |
| `/lifesteal <player> [interval]` | Lifesteal statistics |
| `/kitpvp <player> [interval]` | KitPvP statistics |
| `/survival <player> [interval]` | Survival statistics |
| `/opskyblock <player> [interval]` | OP Skyblock statistics |
| `/classicskyblock <player> [interval]` | Classic Skyblock statistics |
| `/opfactions <player> [interval]` | OP Factions statistics |
| `/stats <player> <game> [interval] [mode]` | Any game mode (generic) |

### 👤 Profile
| Command | Description |
|---------|-------------|
| `/profile <player>` | View player profile |
| `/friends <player>` | View friends list |
| `/skin <player>` | View Minecraft skin (full body) |
| `/avatar <player>` | View Minecraft head avatar |

### 🏰 Guild
| Command | Description |
|---------|-------------|
| `/guild <name>` | View guild information |
| `/guild-members <name>` | List all guild members |
| `/guild-track <name>` | Track guild member changes |
| `/guild-untrack <name>` | Stop tracking a guild |

### ⚔️ Compare
| Command | Description |
|---------|-------------|
| `/compare <p1> <p2> [game] [interval] [mode]` | Compare two players |
| `/bw-compare <p1> <p2> [mode]` | Quick BedWars comparison |
| `/sw-compare <p1> <p2> [mode]` | Quick SkyWars comparison |

### 🔧 Utility
| Command | Description |
|---------|-------------|
| `/help` | Interactive help menu |
| `/ping` | Check bot latency |
| `/vote` | Pika Network vote links |
| `/botinfo` | Bot statistics & info |
| `/serverinfo` | Discord server info |
| `/invite` | Bot invite link |

---

## ⚙️ Configuration

All configuration is done through environment variables (`.env` file):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | ✅ Yes | — | Your Discord bot token |
| `BOT_PREFIX` | No | `!` | Legacy command prefix |
| `OWNER_ID` | No | `0` | Your Discord user ID |
| `VOTE_REMINDER_USER_ID` | No | `0` | User ID for vote reminders (0 = disabled) |
| `VOTE_REMINDER_HOUR` | No | `18` | Hour to send reminder (24h format) |
| `VOTE_REMINDER_TIMEZONE` | No | `Asia/Kolkata` | Timezone for reminders |

---

## 🔌 API Reference

PikaStatsBot uses the following Pika Network API endpoints:

### Player Profile
```
GET https://stats.pika-network.net/api/profile/{player_name}
```
Returns: username, rank, level, experience, lastSeen, friends, clan, verification status.

### Player Statistics
```
GET https://stats.pika-network.net/api/profile/{player_name}/leaderboard?type={game}&interval={interval}&mode={mode}
```
- **type**: `bedwars`, `skywars`, `unrankedpractice`, `rankedpractice`, `lifesteal`, `kitpvp`, `survival`, `opskyblock`, `classicskyblock`, `opfactions`
- **interval**: `total`, `monthly`, `weekly`, `daily`
- **mode**: `ALL_MODES`, `solo`, `doubles`, etc.

### Guild Information
```
GET https://stats.pika-network.net/api/clans/{guild_name}
```
Returns: name, tag, owner, members, leveling, creationTime.

### Minecraft UUID (via Minetools)
```
GET https://api.minetools.eu/uuid/{player_name}
```

### Skin Renders (via Crafatar)
```
GET https://crafatar.com/avatars/{uuid}
GET https://crafatar.com/renders/head/{uuid}
GET https://crafatar.com/renders/body/{uuid}
GET https://crafatar.com/skins/{uuid}
```

---

## 🏗️ Architecture

- **Async-first** — All API calls use `aiohttp` for non-blocking I/O
- **Caching** — 2-minute TTL cache to reduce API load and improve response times
- **Modular cogs** — Each feature area is a separate cog for maintainability
- **Error handling** — Global error handler + per-command error handling
- **Logging** — Structured logging to console and file
- **Type hints** — Full type annotations throughout the codebase

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick start:
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Submit a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

**PikaStatsBot is not affiliated with, endorsed by, or partnered with PikaNetwork.** All data is fetched from publicly available API endpoints.

---

<div align="center">

[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/oauth2/authorize?client_id=1209050248958312448&permissions=551903422464&scope=bot%20applications.commands)
[![GitHub](https://img.shields.io/badge/GitHub-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)](https://github.com/codewithriza/PikaStatsBot)
[![X](https://img.shields.io/badge/X-%23000000.svg?style=for-the-badge&logo=X&logoColor=white)](https://twitter.com/PikachuStats)

**Made with ❤️ by [codewithriza](https://github.com/codewithriza)**

</div>
