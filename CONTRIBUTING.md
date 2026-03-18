# 🤝 Contributing to PikaStatsBot

Thank you for your interest in contributing to PikaStatsBot! This guide will help you get started.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
- [Code Style](#code-style)
- [Adding a New Game Mode](#adding-a-new-game-mode)
- [Adding a New Command](#adding-a-new-command)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

- Be respectful and constructive in all interactions
- Welcome newcomers and help them get started
- Focus on the code, not the person
- Report any unacceptable behavior to the maintainers

---

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/PikaStatsBot.git
   cd PikaStatsBot
   ```
3. **Add upstream** remote:
   ```bash
   git remote add upstream https://github.com/codewithriza/PikaStatsBot.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🛠️ Development Setup

### Prerequisites
- Python 3.10 or higher
- A Discord bot token ([create one here](https://discord.com/developers/applications))

### Setup Steps

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r bot/requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

4. **Run the bot:**
   ```bash
   python -m bot.bot
   ```

---

## 📁 Project Structure

```
PikaStatsBot/
├── bot/
│   ├── bot.py              # Main entry point, bot class, error handling
│   ├── config.py           # Configuration (env vars, game types, colors)
│   ├── cogs/
│   │   ├── stats.py        # Game stats commands (/bw, /sw, /practice, etc.)
│   │   ├── profile.py      # Profile commands (/profile, /friends, /skin)
│   │   ├── guild.py        # Guild commands (/guild, /guild-track)
│   │   ├── compare.py      # Comparison commands (/compare, /bw-compare)
│   │   └── utility.py      # Utility commands (/help, /ping, /vote)
│   └── utils/
│       ├── api.py           # Async API wrapper with caching
│       └── embeds.py        # Embed builder utilities
├── .env.example             # Environment variable template
├── .gitignore
├── CONTRIBUTING.md          # This file
├── LICENSE
└── README.md
```

### Key Files

| File | Purpose |
|------|---------|
| `bot/bot.py` | Bot initialization, cog loading, global error handling |
| `bot/config.py` | All configuration: game types, modes, colors, API URLs |
| `bot/utils/api.py` | `PikaAPI` class — async HTTP client with TTL caching |
| `bot/utils/embeds.py` | Embed builders for consistent, beautiful Discord embeds |

---

## 💡 How to Contribute

### 🐛 Bug Reports
1. Check if the bug is already reported in [Issues](https://github.com/codewithriza/PikaStatsBot/issues)
2. Create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs (if any)
   - Python version and OS

### ✨ Feature Requests
1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Include mockups or examples if possible

### 🔧 Code Contributions
1. Pick an issue or create one for your feature
2. Follow the [Development Setup](#development-setup)
3. Write your code following the [Code Style](#code-style)
4. Test your changes
5. Submit a [Pull Request](#pull-request-process)

---

## 🎨 Code Style

### General Rules
- Follow **PEP 8** guidelines
- Use **type hints** for all function parameters and return types
- Maximum line length: **100 characters** (soft limit)
- Use **docstrings** for all modules, classes, and public functions

### Naming Conventions
```python
# Variables and functions: snake_case
player_name = "Steve"
def get_player_stats():
    pass

# Classes: PascalCase
class StatsCog(commands.Cog):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_BASE_URL = "https://..."
```

### Import Order
```python
# 1. Standard library
import logging
from typing import Optional

# 2. Third-party packages
import discord
from discord.ext import commands

# 3. Local modules
from bot.config import Config
from bot.utils.api import pika_api
```

### Docstrings
```python
def calculate_ratio(kills: int, deaths: int) -> str:
    """
    Calculate a kill/death ratio.

    Args:
        kills: Number of kills.
        deaths: Number of deaths.

    Returns:
        Formatted ratio string (e.g., "2.50").
    """
```

---

## 🎮 Adding a New Game Mode

To add support for a new Pika Network game mode:

### 1. Update `bot/config.py`

Add the game type to `Config.GAME_TYPES`:

```python
"newgame": {
    "display": "New Game",
    "emoji": "🎮",
    "color": 0x3498DB,
    "modes": {
        "ALL_MODES": "All Modes",
        "solo": "Solo",
        "doubles": "Doubles",
    },
    "key_stats": ["Wins", "Losses", "Kills", "Deaths"],
},
```

### 2. Add command in `bot/cogs/stats.py`

```python
@app_commands.command(name="newgame", description="🎮 Get New Game stats")
@app_commands.describe(
    player_name="The Pika Network username",
    interval="Time interval",
    mode="Game mode",
)
@app_commands.autocomplete(
    interval=interval_autocomplete,
    mode=_mode_autocomplete_factory("newgame"),
)
async def new_game(
    self,
    interaction: discord.Interaction,
    player_name: str,
    interval: Optional[str] = "total",
    mode: Optional[str] = "ALL_MODES",
):
    await self._fetch_and_send_stats(
        interaction, player_name, "newgame", interval, mode
    )
```

### 3. Update help menu in `bot/cogs/utility.py`

Add the new command to the `_stats_help()` method.

### 4. Update `README.md`

Add the new game mode to the features table and commands list.

---

## 🆕 Adding a New Command

### 1. Choose the right cog
- **Stats** → Game statistics
- **Profile** → Player information
- **Guild** → Guild/clan features
- **Compare** → Comparison features
- **Utility** → Bot utilities

### 2. Create the command

```python
@app_commands.command(name="mycommand", description="Description here")
@app_commands.describe(param="Parameter description")
async def my_command(self, interaction: discord.Interaction, param: str):
    await interaction.response.defer()
    
    try:
        # Your logic here
        embed = base_embed(title="Result", description="...")
        await interaction.followup.send(embed=embed)
    except Exception as e:
        logger.exception("Error in mycommand")
        await interaction.followup.send(
            embed=error_embed(description="Something went wrong.")
        )
```

### 3. Update the help menu

Add your command to the appropriate help category in `bot/cogs/utility.py`.

---

## 🧪 Testing

Before submitting a PR, ensure:

1. **Bot starts without errors:**
   ```bash
   python -m bot.bot
   ```

2. **All commands respond correctly** — Test in a Discord server

3. **Error handling works** — Try invalid inputs:
   - Non-existent player names
   - Invalid game modes
   - Empty responses

4. **No breaking changes** — Existing commands still work

---

## 📤 Pull Request Process

1. **Update your branch** with the latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Commit your changes** with clear messages:
   ```bash
   git commit -m "feat: add TheBridge game mode support"
   git commit -m "fix: handle empty API response in profile command"
   git commit -m "docs: update README with new commands"
   ```

   Commit message prefixes:
   - `feat:` — New feature
   - `fix:` — Bug fix
   - `docs:` — Documentation
   - `refactor:` — Code refactoring
   - `style:` — Formatting changes
   - `chore:` — Maintenance tasks

3. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub:
   - Clear title describing the change
   - Reference any related issues
   - Include screenshots for UI changes
   - Describe what was changed and why

5. **Wait for review** — Maintainers will review your PR and may request changes

---

## 📞 Contact

- **GitHub Issues** — For bugs and feature requests
- **Pull Requests** — For code contributions
- **Discord** — Join our community server

---

Thank you for contributing to PikaStatsBot! 🎉
