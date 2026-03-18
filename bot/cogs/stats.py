"""
Stats Cog — Slash commands for all Pika Network game mode statistics.

Supports: BedWars, SkyWars, Unranked Practice, Ranked Practice,
Lifesteal, KitPvP, Survival, OP Skyblock, Classic Skyblock, OP Factions.
"""

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import Config
from bot.utils.api import pika_api, PlayerNotFoundError, APIError
from bot.utils.embeds import stats_embed, error_embed

logger = logging.getLogger(__name__)


# ── Autocomplete helpers ────────────────────────────────────────────

async def interval_autocomplete(
    interaction: discord.Interaction, current: str
) -> list[app_commands.Choice[str]]:
    """Autocomplete for time interval choices."""
    choices = [
        app_commands.Choice(name=v, value=k)
        for k, v in Config.INTERVALS.items()
        if current.lower() in v.lower()
    ]
    return choices[:25]


def _mode_autocomplete_factory(game_type: str):
    """Factory to create mode autocomplete for a specific game type."""
    async def autocomplete(
        interaction: discord.Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        modes = Config.GAME_TYPES.get(game_type, {}).get("modes", {})
        choices = [
            app_commands.Choice(name=v, value=k)
            for k, v in modes.items()
            if current.lower() in v.lower()
        ]
        return choices[:25]
    return autocomplete


# ── Stats Cog ───────────────────────────────────────────────────────

class StatsCog(commands.Cog, name="Stats"):
    """🎮 Game statistics commands for all Pika Network game modes."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _fetch_and_send_stats(
        self,
        interaction: discord.Interaction,
        player_name: str,
        game_type: str,
        interval: str = "total",
        mode: str = "ALL_MODES",
    ) -> None:
        """Common handler for all stats commands."""
        await interaction.response.defer()

        try:
            # Fetch stats
            stats_data = await pika_api.get_stats(player_name, game_type, interval, mode)

            # Try to get player avatar
            avatar_url = None
            try:
                uuid = await pika_api.get_minecraft_uuid(player_name)
                if uuid:
                    avatar_url = pika_api.get_avatar_url(uuid)
            except Exception:
                pass

            # Build and send embed
            embed = stats_embed(
                player_name=player_name,
                game_type=game_type,
                stats_data=stats_data,
                interval=interval,
                mode=mode,
                avatar_url=avatar_url,
            )
            await interaction.followup.send(embed=embed)

        except PlayerNotFoundError:
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ Player Not Found",
                    description=f"Could not find player **{player_name}** on Pika Network.",
                )
            )
        except APIError as e:
            logger.error("API error fetching stats: %s", e)
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ API Error",
                    description=f"Failed to fetch stats: {e}",
                )
            )
        except Exception as e:
            logger.exception("Unexpected error in stats command")
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ Unexpected Error",
                    description="Something went wrong. Please try again later.",
                )
            )

    # ── BedWars ─────────────────────────────────────────────────────

    @app_commands.command(name="bw", description="🛏️ Get BedWars stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
        mode="Game mode (solo/doubles/3v3v3v3/4v4v4v4/ranked)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete, mode=_mode_autocomplete_factory("bedwars"))
    async def bedwars(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
        mode: Optional[str] = "ALL_MODES",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "bedwars", interval, mode)

    # ── SkyWars ─────────────────────────────────────────────────────

    @app_commands.command(name="sw", description="⚔️ Get SkyWars stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
        mode="Game mode (solo/doubles/mega/ranked)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete, mode=_mode_autocomplete_factory("skywars"))
    async def skywars(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
        mode: Optional[str] = "ALL_MODES",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "skywars", interval, mode)

    # ── Unranked Practice ───────────────────────────────────────────

    @app_commands.command(name="practice", description="🥊 Get Unranked Practice stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
        mode="Practice mode (boxing/nodebuff/gapple/sumo/etc.)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete, mode=_mode_autocomplete_factory("unrankedpractice"))
    async def unranked_practice(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
        mode: Optional[str] = "ALL_MODES",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "unrankedpractice", interval, mode)

    # ── Ranked Practice ─────────────────────────────────────────────

    @app_commands.command(name="ranked", description="🏆 Get Ranked Practice stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
        mode="Practice mode (boxing/nodebuff/gapple/sumo/etc.)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete, mode=_mode_autocomplete_factory("rankedpractice"))
    async def ranked_practice(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
        mode: Optional[str] = "ALL_MODES",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "rankedpractice", interval, mode)

    # ── Lifesteal ───────────────────────────────────────────────────

    @app_commands.command(name="lifesteal", description="❤️ Get Lifesteal stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete)
    async def lifesteal(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "lifesteal", interval, "ALL_MODES")

    # ── KitPvP ──────────────────────────────────────────────────────

    @app_commands.command(name="kitpvp", description="🗡️ Get KitPvP stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete)
    async def kitpvp(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "kitpvp", interval, "ALL_MODES")

    # ── Survival ────────────────────────────────────────────────────

    @app_commands.command(name="survival", description="🌲 Get Survival stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete)
    async def survival(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "survival", interval, "ALL_MODES")

    # ── OP Skyblock ─────────────────────────────────────────────────

    @app_commands.command(name="opskyblock", description="🏝️ Get OP Skyblock stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete)
    async def op_skyblock(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "opskyblock", interval, "ALL_MODES")

    # ── Classic Skyblock ────────────────────────────────────────────

    @app_commands.command(name="classicskyblock", description="🌴 Get Classic Skyblock stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete)
    async def classic_skyblock(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "classicskyblock", interval, "ALL_MODES")

    # ── OP Factions ─────────────────────────────────────────────────

    @app_commands.command(name="opfactions", description="⚡ Get OP Factions stats for a Pika Network player")
    @app_commands.describe(
        player_name="The Pika Network username",
        interval="Time interval (total/monthly/weekly/daily)",
    )
    @app_commands.autocomplete(interval=interval_autocomplete)
    async def op_factions(
        self,
        interaction: discord.Interaction,
        player_name: str,
        interval: Optional[str] = "total",
    ):
        await self._fetch_and_send_stats(interaction, player_name, "opfactions", interval, "ALL_MODES")

    # ── Generic Stats (any game type) ──────────────────────────────

    @app_commands.command(name="stats", description="🎮 Get stats for any Pika Network game mode")
    @app_commands.describe(
        player_name="The Pika Network username",
        game_type="The game type",
        interval="Time interval (total/monthly/weekly/daily)",
        mode="Game mode",
    )
    @app_commands.choices(
        game_type=[
            app_commands.Choice(name=v["display"], value=k)
            for k, v in Config.GAME_TYPES.items()
        ]
    )
    @app_commands.autocomplete(interval=interval_autocomplete)
    async def generic_stats(
        self,
        interaction: discord.Interaction,
        player_name: str,
        game_type: str,
        interval: Optional[str] = "total",
        mode: Optional[str] = "ALL_MODES",
    ):
        await self._fetch_and_send_stats(interaction, player_name, game_type, interval, mode)


async def setup(bot: commands.Bot):
    await bot.add_cog(StatsCog(bot))
