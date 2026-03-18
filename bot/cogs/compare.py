"""
Compare Cog — Compare two players' stats side by side.
"""

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import Config
from bot.utils.api import pika_api, PlayerNotFoundError, APIError
from bot.utils.embeds import compare_embed, error_embed

logger = logging.getLogger(__name__)


# ── Autocomplete helpers ────────────────────────────────────────────

async def interval_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=v, value=k)
        for k, v in Config.INTERVALS.items()
        if current.lower() in v.lower()
    ]
    return choices[:25]


async def game_type_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    choices = [
        app_commands.Choice(name=v["display"], value=k)
        for k, v in Config.GAME_TYPES.items()
        if current.lower() in v["display"].lower()
    ]
    return choices[:25]


class CompareCog(commands.Cog, name="Compare"):
    """⚔️ Player comparison commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="compare",
        description="⚔️ Compare two players' stats side by side",
    )
    @app_commands.describe(
        player1="First player's Pika Network username",
        player2="Second player's Pika Network username",
        game_type="The game type to compare",
        interval="Time interval (total/monthly/weekly/daily)",
        mode="Game mode",
    )
    @app_commands.autocomplete(interval=interval_autocomplete, game_type=game_type_autocomplete)
    async def compare(
        self,
        interaction: discord.Interaction,
        player1: str,
        player2: str,
        game_type: str = "bedwars",
        interval: Optional[str] = "total",
        mode: Optional[str] = "ALL_MODES",
    ):
        await interaction.response.defer()

        try:
            # Validate game type
            if game_type not in Config.GAME_TYPES:
                await interaction.followup.send(
                    embed=error_embed(
                        title="❌ Invalid Game Type",
                        description=(
                            f"**{game_type}** is not a valid game type.\n"
                            f"Available: {', '.join(Config.GAME_TYPES.keys())}"
                        ),
                    )
                )
                return

            # Fetch both players' stats concurrently
            import asyncio
            stats1_task = pika_api.get_stats(player1, game_type, interval, mode)
            stats2_task = pika_api.get_stats(player2, game_type, interval, mode)

            try:
                stats1, stats2 = await asyncio.gather(stats1_task, stats2_task)
            except PlayerNotFoundError as e:
                await interaction.followup.send(
                    embed=error_embed(
                        title="❌ Player Not Found",
                        description=str(e),
                    )
                )
                return

            # Get avatars
            avatar1_url = None
            avatar2_url = None
            try:
                uuid1_task = pika_api.get_minecraft_uuid(player1)
                uuid2_task = pika_api.get_minecraft_uuid(player2)
                uuid1, uuid2 = await asyncio.gather(uuid1_task, uuid2_task)
                if uuid1:
                    avatar1_url = pika_api.get_avatar_url(uuid1)
                if uuid2:
                    avatar2_url = pika_api.get_avatar_url(uuid2)
            except Exception:
                pass

            embed = compare_embed(
                player1=player1,
                player2=player2,
                stats1=stats1,
                stats2=stats2,
                game_type=game_type,
                interval=interval,
                mode=mode,
                avatar1_url=avatar1_url,
                avatar2_url=avatar2_url,
            )
            await interaction.followup.send(embed=embed)

        except APIError as e:
            logger.error("API error in compare: %s", e)
            await interaction.followup.send(
                embed=error_embed(description=f"Failed to fetch stats: {e}")
            )
        except Exception:
            logger.exception("Unexpected error in compare command")
            await interaction.followup.send(
                embed=error_embed(description="Something went wrong. Please try again later.")
            )

    # ── Quick Compare (BedWars shortcut) ────────────────────────────

    @app_commands.command(
        name="bw-compare",
        description="🛏️ Quick BedWars comparison between two players",
    )
    @app_commands.describe(
        player1="First player's username",
        player2="Second player's username",
        mode="BedWars mode",
    )
    async def bw_compare(
        self,
        interaction: discord.Interaction,
        player1: str,
        player2: str,
        mode: Optional[str] = "ALL_MODES",
    ):
        # Delegate to the main compare command logic
        await self.compare.callback(
            self, interaction, player1, player2, "bedwars", "total", mode
        )

    # ── Quick Compare (SkyWars shortcut) ────────────────────────────

    @app_commands.command(
        name="sw-compare",
        description="⚔️ Quick SkyWars comparison between two players",
    )
    @app_commands.describe(
        player1="First player's username",
        player2="Second player's username",
        mode="SkyWars mode",
    )
    async def sw_compare(
        self,
        interaction: discord.Interaction,
        player1: str,
        player2: str,
        mode: Optional[str] = "ALL_MODES",
    ):
        await self.compare.callback(
            self, interaction, player1, player2, "skywars", "total", mode
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(CompareCog(bot))
