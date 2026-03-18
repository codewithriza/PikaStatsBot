"""
Profile Cog — Player profile, friends list, and skin display commands.
"""

import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.utils.api import pika_api, PlayerNotFoundError, APIError
from bot.utils.embeds import profile_embed, friends_embed, skin_embed, error_embed

logger = logging.getLogger(__name__)


class ProfileCog(commands.Cog, name="Profile"):
    """👤 Player profile and information commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ── Player Profile ──────────────────────────────────────────────

    @app_commands.command(name="profile", description="👤 View a Pika Network player's profile")
    @app_commands.describe(player_name="The Pika Network username")
    async def profile(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer()

        try:
            profile_data = await pika_api.get_profile(player_name)

            # Get avatar
            avatar_url = None
            try:
                uuid = await pika_api.get_minecraft_uuid(player_name)
                if uuid:
                    avatar_url = pika_api.get_avatar_url(uuid)
            except Exception:
                pass

            embed = profile_embed(player_name, profile_data, avatar_url)
            await interaction.followup.send(embed=embed)

        except PlayerNotFoundError:
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ Player Not Found",
                    description=f"Could not find player **{player_name}** on Pika Network.",
                )
            )
        except APIError as e:
            logger.error("API error fetching profile: %s", e)
            await interaction.followup.send(
                embed=error_embed(description=f"Failed to fetch profile: {e}")
            )
        except Exception:
            logger.exception("Unexpected error in profile command")
            await interaction.followup.send(
                embed=error_embed(description="Something went wrong. Please try again later.")
            )

    # ── Friends List ────────────────────────────────────────────────

    @app_commands.command(name="friends", description="👥 View a player's friends list")
    @app_commands.describe(player_name="The Pika Network username")
    async def friends(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer()

        try:
            profile_data = await pika_api.get_profile(player_name)
            friends_list = profile_data.get("friends", [])

            # Get avatar
            avatar_url = None
            try:
                uuid = await pika_api.get_minecraft_uuid(player_name)
                if uuid:
                    avatar_url = pika_api.get_avatar_url(uuid)
            except Exception:
                pass

            embed = friends_embed(player_name, friends_list, avatar_url)
            await interaction.followup.send(embed=embed)

        except PlayerNotFoundError:
            await interaction.followup.send(
                embed=error_embed(
                    title="❌ Player Not Found",
                    description=f"Could not find player **{player_name}** on Pika Network.",
                )
            )
        except APIError as e:
            logger.error("API error fetching friends: %s", e)
            await interaction.followup.send(
                embed=error_embed(description=f"Failed to fetch friends: {e}")
            )
        except Exception:
            logger.exception("Unexpected error in friends command")
            await interaction.followup.send(
                embed=error_embed(description="Something went wrong. Please try again later.")
            )

    # ── Player Skin ─────────────────────────────────────────────────

    @app_commands.command(name="skin", description="🎨 View a Minecraft player's skin")
    @app_commands.describe(player_name="The Minecraft/Pika Network username")
    async def skin(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer()

        try:
            uuid = await pika_api.get_minecraft_uuid(player_name)
            if not uuid:
                await interaction.followup.send(
                    embed=error_embed(
                        title="❌ Player Not Found",
                        description=f"Could not find Minecraft player **{player_name}**.",
                    )
                )
                return

            embed = skin_embed(player_name, uuid)
            await interaction.followup.send(embed=embed)

        except APIError as e:
            logger.error("API error fetching skin: %s", e)
            await interaction.followup.send(
                embed=error_embed(description=f"Failed to fetch skin: {e}")
            )
        except Exception:
            logger.exception("Unexpected error in skin command")
            await interaction.followup.send(
                embed=error_embed(description="Something went wrong. Please try again later.")
            )

    # ── Player Avatar (quick) ───────────────────────────────────────

    @app_commands.command(name="avatar", description="🖼️ Get a player's Minecraft head avatar")
    @app_commands.describe(player_name="The Minecraft/Pika Network username")
    async def avatar(self, interaction: discord.Interaction, player_name: str):
        await interaction.response.defer()

        try:
            uuid = await pika_api.get_minecraft_uuid(player_name)
            if not uuid:
                await interaction.followup.send(
                    embed=error_embed(
                        title="❌ Player Not Found",
                        description=f"Could not find Minecraft player **{player_name}**.",
                    )
                )
                return

            avatar_url = pika_api.get_avatar_url(uuid, size=256)
            head_url = pika_api.get_head_url(uuid)

            embed = discord.Embed(
                title=f"🖼️ {player_name}'s Avatar",
                color=0x3498DB,
            )
            embed.set_image(url=head_url)
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(
                name="🔗 Links",
                value=(
                    f"[2D Face]({avatar_url}) • "
                    f"[3D Head]({head_url}) • "
                    f"[Full Body]({pika_api.get_body_url(uuid)})"
                ),
                inline=False,
            )
            await interaction.followup.send(embed=embed)

        except Exception:
            logger.exception("Unexpected error in avatar command")
            await interaction.followup.send(
                embed=error_embed(description="Something went wrong. Please try again later.")
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ProfileCog(bot))
