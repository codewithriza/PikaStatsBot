"""
Guild Cog — Guild information, member list, and guild tracking commands.
"""

import logging
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot.config import Config
from bot.utils.api import pika_api, GuildNotFoundError, APIError
from bot.utils.embeds import guild_embed, base_embed, error_embed, success_embed

logger = logging.getLogger(__name__)


class GuildCog(commands.Cog, name="Guild"):
    """🏰 Guild information and tracking commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Cache for guild tracking: {guild_name: {channel_id, last_members}}
        self._tracked_guilds: dict[str, dict] = {}

    def cog_unload(self):
        self._guild_tracker.cancel()

    # ── Guild Info ──────────────────────────────────────────────────

    @app_commands.command(name="guild", description="🏰 Get information about a Pika Network guild")
    @app_commands.describe(guild_name="The name of the guild/clan")
    async def guild_info(self, interaction: discord.Interaction, guild_name: str):
        await interaction.response.defer()

        try:
            guild_data = await pika_api.get_guild(guild_name)
            embed = guild_embed(guild_name, guild_data)
            await interaction.followup.send(embed=embed)

        except GuildNotFoundError:
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ Guild Not Found",
                    description=f"Could not find guild **{guild_name}** on Pika Network.",
                )
            )
        except APIError as e:
            logger.error("API error fetching guild: %s", e)
            await interaction.followup.send(
                embed=error_embed(description=f"Failed to fetch guild info: {e}")
            )
        except Exception:
            logger.exception("Unexpected error in guild command")
            await interaction.followup.send(
                embed=error_embed(description="Something went wrong. Please try again later.")
            )

    # ── Guild Members ───────────────────────────────────────────────

    @app_commands.command(name="guild-members", description="👥 List all members of a Pika Network guild")
    @app_commands.describe(guild_name="The name of the guild/clan")
    async def guild_members(self, interaction: discord.Interaction, guild_name: str):
        await interaction.response.defer()

        try:
            guild_data = await pika_api.get_guild(guild_name)
            members = guild_data.get("members", [])
            owner = guild_data.get("owner", {})
            owner_name = owner.get("username", "Unknown") if isinstance(owner, dict) else "Unknown"
            tag = guild_data.get("tag", "")

            embed = base_embed(
                title=f"👥 [{tag}] {guild_name} — Members ({len(members)})",
                color=Config.COLOR_INFO,
            )

            # Categorize members
            member_names = []
            for m in members:
                user = m.get("user", {})
                username = user.get("username", "Unknown")
                is_owner = username.lower() == owner_name.lower()
                prefix = "👑" if is_owner else "•"
                member_names.append(f"{prefix} {username}")

            # Split into pages if needed
            if len(member_names) <= 30:
                embed.add_field(
                    name="Members",
                    value="```\n" + "\n".join(member_names) + "\n```",
                    inline=False,
                )
            else:
                # Split into 3 columns
                chunk_size = len(member_names) // 3 + 1
                for i in range(3):
                    chunk = member_names[i * chunk_size:(i + 1) * chunk_size]
                    if chunk:
                        embed.add_field(
                            name=f"Members ({i + 1}/3)",
                            value="```\n" + "\n".join(chunk) + "\n```",
                            inline=True,
                        )

            await interaction.followup.send(embed=embed)

        except GuildNotFoundError:
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ Guild Not Found",
                    description=f"Could not find guild **{guild_name}** on Pika Network.",
                )
            )
        except APIError as e:
            logger.error("API error fetching guild members: %s", e)
            await interaction.followup.send(
                embed=error_embed(description=f"Failed to fetch guild members: {e}")
            )
        except Exception:
            logger.exception("Unexpected error in guild-members command")
            await interaction.followup.send(
                embed=error_embed(description="Something went wrong. Please try again later.")
            )

    # ── Guild Tracking (Logs) ───────────────────────────────────────

    @app_commands.command(
        name="guild-track",
        description="📡 Track a guild's member changes in this channel",
    )
    @app_commands.describe(guild_name="The name of the guild/clan to track")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def guild_track(self, interaction: discord.Interaction, guild_name: str):
        await interaction.response.defer()

        try:
            guild_data = await pika_api.get_guild(guild_name)
            members = guild_data.get("members", [])
            member_set = {
                m.get("user", {}).get("username", "").lower()
                for m in members
            }

            self._tracked_guilds[guild_name.lower()] = {
                "channel_id": interaction.channel_id,
                "last_members": member_set,
                "guild_name": guild_name,
            }

            # Start tracker if not running
            if not self._guild_tracker.is_running():
                self._guild_tracker.start()

            embed = success_embed(
                title="📡 Guild Tracking Enabled",
                description=(
                    f"Now tracking **{guild_name}** in this channel.\n"
                    f"Current members: **{len(members)}**\n\n"
                    f"I'll notify you when members join or leave!"
                ),
            )
            await interaction.followup.send(embed=embed)

        except GuildNotFoundError:
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ Guild Not Found",
                    description=f"Could not find guild **{guild_name}** on Pika Network.",
                )
            )
        except APIError as e:
            await interaction.followup.send(
                embed=error_embed(description=f"Failed to set up tracking: {e}")
            )

    @app_commands.command(
        name="guild-untrack",
        description="🔕 Stop tracking a guild in this channel",
    )
    @app_commands.describe(guild_name="The name of the guild/clan to stop tracking")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def guild_untrack(self, interaction: discord.Interaction, guild_name: str):
        key = guild_name.lower()
        if key in self._tracked_guilds:
            del self._tracked_guilds[key]
            await interaction.response.send_message(
                embed=success_embed(
                    title="🔕 Tracking Stopped",
                    description=f"Stopped tracking **{guild_name}**.",
                )
            )
        else:
            await interaction.response.send_message(
                embed=error_embed(
                    title="❌ Not Tracking",
                    description=f"**{guild_name}** is not being tracked.",
                )
            )

    @tasks.loop(minutes=5)
    async def _guild_tracker(self):
        """Background task that checks tracked guilds for member changes."""
        for key, data in list(self._tracked_guilds.items()):
            try:
                guild_data = await pika_api.get_guild(data["guild_name"])
                members = guild_data.get("members", [])
                current_set = {
                    m.get("user", {}).get("username", "").lower()
                    for m in members
                }
                previous_set = data["last_members"]

                joined = current_set - previous_set
                left = previous_set - current_set

                if joined or left:
                    channel = self.bot.get_channel(data["channel_id"])
                    if channel:
                        embed = base_embed(
                            title=f"📡 {data['guild_name']} — Member Update",
                            color=Config.COLOR_SUCCESS if joined else Config.COLOR_ERROR,
                        )

                        if joined:
                            join_list = "\n".join([f"🟢 {name}" for name in sorted(joined)])
                            embed.add_field(
                                name=f"✅ Joined ({len(joined)})",
                                value=join_list,
                                inline=True,
                            )

                        if left:
                            leave_list = "\n".join([f"🔴 {name}" for name in sorted(left)])
                            embed.add_field(
                                name=f"❌ Left ({len(left)})",
                                value=leave_list,
                                inline=True,
                            )

                        embed.add_field(
                            name="📊 Member Count",
                            value=f"`{len(previous_set)}` → `{len(current_set)}`",
                            inline=False,
                        )

                        embed.set_footer(
                            text=f"Tracked at {datetime.utcnow().strftime('%H:%M UTC')} | PikaStatsBot"
                        )

                        await channel.send(embed=embed)

                    # Update cache
                    self._tracked_guilds[key]["last_members"] = current_set

            except Exception as e:
                logger.error("Error tracking guild %s: %s", key, e)

    @_guild_tracker.before_loop
    async def _before_tracker(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(GuildCog(bot))
