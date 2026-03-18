"""
PikaStatsBot — The ultimate Pika Network statistics Discord bot.

A modern, feature-rich Discord bot built with discord.py v2 that provides
comprehensive statistics for all Pika Network game modes including BedWars,
SkyWars, Practice, Lifesteal, KitPvP, Survival, Skyblock, and Factions.

Features:
    - 10+ game mode stats with KDR/WLR/FKDR calculations
    - Player profiles with rank, level, guild, and online status
    - Player comparison (side-by-side stat comparison)
    - Guild information and real-time member tracking
    - Minecraft skin/avatar viewer
    - Interactive help menu with dropdowns
    - Daily vote reminders
    - Async API with caching for fast responses

Usage:
    Set DISCORD_TOKEN in .env file, then run:
        python -m bot.bot
    or:
        python bot/bot.py

Author: codewithriza
License: MIT
Repository: https://github.com/codewithriza/PikaStatsBot
"""

import asyncio
import logging
import os
import sys

import discord
from discord.ext import commands

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.config import Config
from bot.utils.api import pika_api

# ── Logging Setup ───────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8", mode="a"),
    ],
)
logger = logging.getLogger("PikaStatsBot")

# Suppress noisy loggers
logging.getLogger("discord.http").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)


# ── Bot Setup ───────────────────────────────────────────────────────

COGS = [
    "bot.cogs.stats",
    "bot.cogs.profile",
    "bot.cogs.guild",
    "bot.cogs.compare",
    "bot.cogs.utility",
]


class PikaStatsBot(commands.Bot):
    """Custom bot class with startup hooks and error handling."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = False  # Not needed, saves resources

        super().__init__(
            command_prefix=Config.PREFIX,
            intents=intents,
            help_command=None,  # We use a custom slash command
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Pika Network Stats",
            ),
            status=discord.Status.online,
        )

    async def setup_hook(self) -> None:
        """Load all cogs and sync slash commands on startup."""
        logger.info("Loading cogs...")
        for cog in COGS:
            try:
                await self.load_extension(cog)
                logger.info("  ✅ Loaded: %s", cog)
            except Exception as e:
                logger.error("  ❌ Failed to load %s: %s", cog, e)

        # Sync slash commands globally
        logger.info("Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            logger.info("  ✅ Synced %d commands globally", len(synced))
        except Exception as e:
            logger.error("  ❌ Failed to sync commands: %s", e)

    async def on_ready(self) -> None:
        """Called when the bot is fully connected and ready."""
        logger.info("━" * 60)
        logger.info("  PikaStatsBot is online!")
        logger.info("  User: %s (ID: %s)", self.user, self.user.id if self.user else "?")
        logger.info("  Servers: %d", len(self.guilds))
        logger.info("  discord.py: %s", discord.__version__)
        logger.info("━" * 60)

        # Update presence with server count
        await self._update_presence()

        # Log guilds
        for guild in self.guilds:
            logger.info("  📡 %s (ID: %s, Members: %s)", guild.name, guild.id, guild.member_count)

    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Update presence when joining a new server."""
        logger.info("Joined guild: %s (ID: %s)", guild.name, guild.id)
        await self._update_presence()

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        """Update presence when leaving a server."""
        logger.info("Left guild: %s (ID: %s)", guild.name, guild.id)
        await self._update_presence()

    async def _update_presence(self) -> None:
        """Update the bot's presence with current server count."""
        server_count = len(self.guilds)
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"/help | {server_count} servers",
            )
        )

    async def close(self) -> None:
        """Clean up resources on shutdown."""
        logger.info("Shutting down PikaStatsBot...")
        await pika_api.close()
        await super().close()


# ── Global Error Handler ────────────────────────────────────────────

async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
) -> None:
    """Global error handler for slash commands."""
    if isinstance(error, app_commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description=f"You need the following permissions: {', '.join(error.missing_permissions)}",
            color=Config.COLOR_ERROR,
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    elif isinstance(error, app_commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏳ Cooldown",
            description=f"Please wait **{error.retry_after:.1f}s** before using this command again.",
            color=Config.COLOR_WARNING,
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    elif isinstance(error, app_commands.BotMissingPermissions):
        embed = discord.Embed(
            title="❌ Bot Missing Permissions",
            description=f"I need the following permissions: {', '.join(error.missing_permissions)}",
            color=Config.COLOR_ERROR,
        )
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    else:
        logger.error("Unhandled command error: %s", error, exc_info=error)
        embed = discord.Embed(
            title="❌ Something Went Wrong",
            description="An unexpected error occurred. Please try again later.",
            color=Config.COLOR_ERROR,
        )
        try:
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception:
            pass


# ── Entry Point ─────────────────────────────────────────────────────

def main():
    """Start the bot."""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.critical("Configuration error: %s", e)
        print(f"\n❌ {e}")
        print("\nCreate a .env file with:")
        print("  DISCORD_TOKEN=your_bot_token_here")
        print("\nSee .env.example for all configuration options.")
        sys.exit(1)

    # Create and run bot
    bot = PikaStatsBot()
    bot.tree.on_error = on_app_command_error

    logger.info("Starting PikaStatsBot...")
    bot.run(Config.TOKEN, log_handler=None)


if __name__ == "__main__":
    main()
