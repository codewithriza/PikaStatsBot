"""
Configuration management for PikaStatsBot.
Loads settings from environment variables and .env file.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Bot configuration loaded from environment variables."""

    # Discord Bot Token (REQUIRED)
    TOKEN: str = os.getenv("DISCORD_TOKEN", "")

    # Bot Settings
    PREFIX: str = os.getenv("BOT_PREFIX", "!")
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0"))
    VOTE_REMINDER_USER_ID: int = int(os.getenv("VOTE_REMINDER_USER_ID", "0"))
    VOTE_REMINDER_HOUR: int = int(os.getenv("VOTE_REMINDER_HOUR", "18"))  # 24h format
    VOTE_REMINDER_TIMEZONE: str = os.getenv("VOTE_REMINDER_TIMEZONE", "Asia/Kolkata")

    # API Settings
    PIKA_API_BASE: str = "https://stats.pika-network.net/api"
    CRAFATAR_BASE: str = "https://crafatar.com"
    MC_HEADS_BASE: str = "https://mc-heads.net"
    MINETOOLS_API: str = "https://api.minetools.eu/uuid"

    # Embed Colors
    COLOR_PRIMARY: int = 0x3498DB   # Blue
    COLOR_SUCCESS: int = 0x2ECC71   # Green
    COLOR_WARNING: int = 0xF39C12   # Orange
    COLOR_ERROR: int = 0xE74C3C     # Red
    COLOR_INFO: int = 0x9B59B6      # Purple
    COLOR_BEDWARS: int = 0xE74C3C   # Red
    COLOR_SKYWARS: int = 0x3498DB   # Blue
    COLOR_PRACTICE: int = 0xE67E22  # Orange
    COLOR_LIFESTEAL: int = 0x2ECC71 # Green
    COLOR_KITPVP: int = 0x9B59B6    # Purple
    COLOR_SURVIVAL: int = 0x1ABC9C  # Teal
    COLOR_SKYBLOCK: int = 0xF1C40F  # Yellow
    COLOR_FACTIONS: int = 0xE91E63  # Pink

    # Game Types supported by the Pika Network API
    GAME_TYPES: dict = {
        "bedwars": {
            "display": "BedWars",
            "emoji": "🛏️",
            "color": 0xE74C3C,
            "modes": {
                "ALL_MODES": "All Modes",
                "solo": "Solo",
                "doubles": "Doubles",
                "3v3v3v3": "3v3v3v3",
                "4v4v4v4": "4v4v4v4",
                "ranked": "Ranked",
            },
            "key_stats": ["Wins", "Losses", "Kills", "Deaths", "Final kills", "Final deaths", "Beds destroyed"],
        },
        "skywars": {
            "display": "SkyWars",
            "emoji": "⚔️",
            "color": 0x3498DB,
            "modes": {
                "ALL_MODES": "All Modes",
                "solo": "Solo",
                "doubles": "Doubles",
                "mega": "Mega",
                "ranked": "Ranked",
            },
            "key_stats": ["Wins", "Losses", "Kills", "Deaths", "Arrows shot", "Arrows hit"],
        },
        "unrankedpractice": {
            "display": "Unranked Practice",
            "emoji": "🥊",
            "color": 0xE67E22,
            "modes": {
                "ALL_MODES": "All Modes",
                "global": "Global",
                "boxing": "Boxing",
                "nodebuff": "NoDebuff",
                "gapple": "Gapple",
                "sumo": "Sumo",
                "builduhc": "BuildUHC",
                "combo": "Combo",
                "debuff": "Debuff",
                "fist": "Fist",
                "spleef": "Spleef",
            },
            "key_stats": ["Wins", "Losses", "Kills", "Deaths", "Hits dealt"],
        },
        "rankedpractice": {
            "display": "Ranked Practice",
            "emoji": "🏆",
            "color": 0xF1C40F,
            "modes": {
                "ALL_MODES": "All Modes",
                "global": "Global",
                "boxing": "Boxing",
                "nodebuff": "NoDebuff",
                "gapple": "Gapple",
                "sumo": "Sumo",
                "builduhc": "BuildUHC",
                "combo": "Combo",
                "debuff": "Debuff",
                "fist": "Fist",
                "spleef": "Spleef",
            },
            "key_stats": ["Wins", "Losses", "Kills", "Deaths", "Hits dealt"],
        },
        "lifesteal": {
            "display": "Lifesteal",
            "emoji": "❤️",
            "color": 0x2ECC71,
            "modes": {
                "ALL_MODES": "All Modes",
            },
            "key_stats": ["Kills", "Deaths", "Player Level", "Mobs Killed", "Blocks Placed", "Blocks Broken"],
        },
        "kitpvp": {
            "display": "KitPvP",
            "emoji": "🗡️",
            "color": 0x9B59B6,
            "modes": {
                "ALL_MODES": "All Modes",
            },
            "key_stats": ["Kills", "Deaths", "Level", "Current Killstreak", "Highest Killstreak", "Prestige"],
        },
        "survival": {
            "display": "Survival",
            "emoji": "🌲",
            "color": 0x1ABC9C,
            "modes": {
                "ALL_MODES": "All Modes",
            },
            "key_stats": ["Mobs Killed", "Player Level", "EXP Collected", "Balance"],
        },
        "opskyblock": {
            "display": "OP Skyblock",
            "emoji": "🏝️",
            "color": 0xF1C40F,
            "modes": {
                "ALL_MODES": "All Modes",
            },
            "key_stats": ["Player Level", "Kills", "Balance", "Souls", "Special Ores Mined"],
        },
        "classicskyblock": {
            "display": "Classic Skyblock",
            "emoji": "🌴",
            "color": 0x27AE60,
            "modes": {
                "ALL_MODES": "All Modes",
            },
            "key_stats": ["Player Level", "Kills", "Deaths", "Mobs Killed", "Highest Killstreak"],
        },
        "opfactions": {
            "display": "OP Factions",
            "emoji": "⚡",
            "color": 0xE91E63,
            "modes": {
                "ALL_MODES": "All Modes",
            },
            "key_stats": ["Kills", "Deaths", "Harvest Sugar Cane", "Mobs Killed", "Player Level"],
        },
    }

    # Time intervals for stats
    INTERVALS: dict = {
        "total": "Total",
        "monthly": "Monthly",
        "weekly": "Weekly",
        "daily": "Daily",
    }

    # Vote links
    VOTE_LINKS: list = [
        "https://vote.pika-network.net/1",
        "https://vote.pika-network.net/2",
        "https://vote.pika-network.net/3",
        "https://vote.pika-network.net/4",
        "https://vote.pika-network.net/5",
        "https://vote.pika-network.net/6",
        "https://vote.pika-network.net/7",
    ]

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.TOKEN:
            raise ValueError(
                "DISCORD_TOKEN environment variable is required. "
                "Set it in your .env file or environment."
            )
        return True
