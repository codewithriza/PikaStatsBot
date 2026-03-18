"""
Utility Cog — Help, vote reminders, ping, bot info, and server info commands.
"""

import logging
import time
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks
import pytz

from bot.config import Config
from bot.utils.embeds import base_embed, success_embed, error_embed

logger = logging.getLogger(__name__)


# ── Interactive Help Menu (Select Menu) ─────────────────────────────

class HelpSelect(discord.ui.Select):
    """Dropdown menu for selecting a help category."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        options = [
            discord.SelectOption(
                label="🎮 Game Stats",
                description="BedWars, SkyWars, Practice, and more",
                value="stats",
            ),
            discord.SelectOption(
                label="👤 Profile",
                description="Player profiles, friends, skins",
                value="profile",
            ),
            discord.SelectOption(
                label="🏰 Guild",
                description="Guild info, members, tracking",
                value="guild",
            ),
            discord.SelectOption(
                label="⚔️ Compare",
                description="Compare players side by side",
                value="compare",
            ),
            discord.SelectOption(
                label="🔧 Utility",
                description="Bot info, ping, vote reminders",
                value="utility",
            ),
        ]
        super().__init__(
            placeholder="📖 Select a category...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        embeds = {
            "stats": self._stats_help(),
            "profile": self._profile_help(),
            "guild": self._guild_help(),
            "compare": self._compare_help(),
            "utility": self._utility_help(),
        }
        embed = embeds.get(category, self._stats_help())
        await interaction.response.edit_message(embed=embed)

    def _stats_help(self) -> discord.Embed:
        embed = base_embed(
            title="🎮 Game Stats Commands",
            description="Get detailed statistics for any Pika Network game mode.",
            color=Config.COLOR_PRIMARY,
        )
        commands_list = [
            ("`/bw <player> [interval] [mode]`", "🛏️ BedWars stats"),
            ("`/sw <player> [interval] [mode]`", "⚔️ SkyWars stats"),
            ("`/practice <player> [interval] [mode]`", "🥊 Unranked Practice stats"),
            ("`/ranked <player> [interval] [mode]`", "🏆 Ranked Practice stats"),
            ("`/lifesteal <player> [interval]`", "❤️ Lifesteal stats"),
            ("`/kitpvp <player> [interval]`", "🗡️ KitPvP stats"),
            ("`/survival <player> [interval]`", "🌲 Survival stats"),
            ("`/opskyblock <player> [interval]`", "🏝️ OP Skyblock stats"),
            ("`/classicskyblock <player> [interval]`", "🌴 Classic Skyblock stats"),
            ("`/opfactions <player> [interval]`", "⚡ OP Factions stats"),
            ("`/stats <player> <game> [interval] [mode]`", "🎮 Any game mode stats"),
        ]
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.add_field(
            name="📝 Intervals",
            value="`total` • `monthly` • `weekly` • `daily`",
            inline=False,
        )
        embed.add_field(
            name="📊 Features",
            value="• Auto-calculated KDR, WLR, FKDR ratios\n• Arrow accuracy percentage\n• Rank on leaderboard\n• Player avatar display",
            inline=False,
        )
        return embed

    def _profile_help(self) -> discord.Embed:
        embed = base_embed(
            title="👤 Profile Commands",
            description="View player profiles, friends, and skins.",
            color=Config.COLOR_PRIMARY,
        )
        commands_list = [
            ("`/profile <player>`", "👤 View player profile (rank, level, guild, last seen)"),
            ("`/friends <player>`", "👥 View player's friends list"),
            ("`/skin <player>`", "🎨 View player's Minecraft skin (full body render)"),
            ("`/avatar <player>`", "🖼️ View player's Minecraft head avatar"),
        ]
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        return embed

    def _guild_help(self) -> discord.Embed:
        embed = base_embed(
            title="🏰 Guild Commands",
            description="Guild information and member tracking.",
            color=Config.COLOR_PRIMARY,
        )
        commands_list = [
            ("`/guild <name>`", "🏰 View guild info (owner, level, members, creation date)"),
            ("`/guild-members <name>`", "👥 List all guild members"),
            ("`/guild-track <name>`", "📡 Track guild member changes in this channel"),
            ("`/guild-untrack <name>`", "🔕 Stop tracking a guild"),
        ]
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        return embed

    def _compare_help(self) -> discord.Embed:
        embed = base_embed(
            title="⚔️ Compare Commands",
            description="Compare two players' stats side by side.",
            color=Config.COLOR_PRIMARY,
        )
        commands_list = [
            ("`/compare <p1> <p2> [game] [interval] [mode]`", "⚔️ Compare any game mode"),
            ("`/bw-compare <p1> <p2> [mode]`", "🛏️ Quick BedWars comparison"),
            ("`/sw-compare <p1> <p2> [mode]`", "⚔️ Quick SkyWars comparison"),
        ]
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)

        embed.add_field(
            name="📊 Features",
            value="• 🟢 Green = Better stat\n• 🔴 Red = Worse stat\n• 🟡 Yellow = Tied\n• Auto ratio comparison",
            inline=False,
        )
        return embed

    def _utility_help(self) -> discord.Embed:
        embed = base_embed(
            title="🔧 Utility Commands",
            description="Bot information and utilities.",
            color=Config.COLOR_PRIMARY,
        )
        commands_list = [
            ("`/help`", "📖 Show this help menu"),
            ("`/ping`", "🏓 Check bot latency"),
            ("`/vote`", "🗳️ Get Pika Network vote links"),
            ("`/botinfo`", "🤖 View bot information and stats"),
            ("`/serverinfo`", "📊 View Discord server information"),
            ("`/invite`", "🔗 Get bot invite link"),
        ]
        for cmd, desc in commands_list:
            embed.add_field(name=cmd, value=desc, inline=False)
        return embed


class HelpView(discord.ui.View):
    """View containing the help dropdown and navigation buttons."""

    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=300)
        self.add_item(HelpSelect(bot))

    @discord.ui.button(label="🔗 Invite Bot", style=discord.ButtonStyle.link, url="https://discord.com/oauth2/authorize?client_id=1209050248958312448&permissions=551903422464&scope=bot%20applications.commands")
    async def invite_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="⭐ GitHub", style=discord.ButtonStyle.link, url="https://github.com/codewithriza/PikaStatsBot")
    async def github_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


# ── Utility Cog ─────────────────────────────────────────────────────

class UtilityCog(commands.Cog, name="Utility"):
    """🔧 Bot utility and information commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._start_time = datetime.utcnow()

    def cog_unload(self):
        if self._vote_reminder.is_running():
            self._vote_reminder.cancel()

    # ── Help Command ────────────────────────────────────────────────

    @app_commands.command(name="help", description="📖 Show all bot commands and features")
    async def help_command(self, interaction: discord.Interaction):
        embed = base_embed(
            title="📖 PikaStatsBot — Help",
            description=(
                "**Your ultimate Pika Network stats companion!**\n\n"
                "🎮 **10+ Game Modes** — BedWars, SkyWars, Practice, Lifesteal, and more\n"
                "📊 **Detailed Stats** — KDR, WLR, FKDR, arrow accuracy, rankings\n"
                "⚔️ **Player Comparison** — Compare any two players side by side\n"
                "👤 **Rich Profiles** — Rank, level, guild, last seen, skins\n"
                "🏰 **Guild Tracking** — Real-time guild member change notifications\n"
                "🎨 **Skin Viewer** — Full body renders and avatar display\n\n"
                "**Select a category below to see commands:**"
            ),
            color=Config.COLOR_PRIMARY,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url if self.bot.user else None)

        view = HelpView(self.bot)
        await interaction.response.send_message(embed=embed, view=view)

    # ── Ping Command ────────────────────────────────────────────────

    @app_commands.command(name="ping", description="🏓 Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        start = time.perf_counter()
        await interaction.response.defer()
        end = time.perf_counter()

        ws_latency = round(self.bot.latency * 1000)
        api_latency = round((end - start) * 1000)

        # Latency quality indicator
        if ws_latency < 100:
            quality = "🟢 Excellent"
        elif ws_latency < 200:
            quality = "🟡 Good"
        else:
            quality = "🔴 High"

        embed = base_embed(
            title="🏓 Pong!",
            color=Config.COLOR_SUCCESS,
        )
        embed.add_field(name="WebSocket", value=f"`{ws_latency}ms`", inline=True)
        embed.add_field(name="API", value=f"`{api_latency}ms`", inline=True)
        embed.add_field(name="Quality", value=quality, inline=True)

        await interaction.followup.send(embed=embed)

    # ── Vote Command ────────────────────────────────────────────────

    @app_commands.command(name="vote", description="🗳️ Get Pika Network vote links")
    async def vote(self, interaction: discord.Interaction):
        vote_lines = [
            f"**Vote {i + 1}** — [Click Here]({link})"
            for i, link in enumerate(Config.VOTE_LINKS)
        ]

        embed = base_embed(
            title="🗳️ Vote for Pika Network",
            description=(
                "Support Pika Network by voting daily!\n\n"
                + "\n".join(vote_lines)
                + "\n\n*Voting gives you in-game rewards!*"
            ),
            color=Config.COLOR_SUCCESS,
        )
        await interaction.response.send_message(embed=embed)

    # ── Bot Info Command ────────────────────────────────────────────

    @app_commands.command(name="botinfo", description="🤖 View bot information and statistics")
    async def bot_info(self, interaction: discord.Interaction):
        uptime = datetime.utcnow() - self._start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        total_members = sum(g.member_count or 0 for g in self.bot.guilds)

        embed = base_embed(
            title="🤖 PikaStatsBot — Info",
            description="The ultimate Pika Network statistics Discord bot.",
            color=Config.COLOR_PRIMARY,
        )

        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Servers:** `{len(self.bot.guilds)}`\n"
                f"**Users:** `{total_members:,}`\n"
                f"**Commands:** `25+`\n"
                f"**Game Modes:** `{len(Config.GAME_TYPES)}`"
            ),
            inline=True,
        )
        embed.add_field(
            name="⚙️ Technical",
            value=(
                f"**Library:** `discord.py 2.x`\n"
                f"**Python:** `3.10+`\n"
                f"**Latency:** `{round(self.bot.latency * 1000)}ms`\n"
                f"**Uptime:** `{days}d {hours}h {minutes}m`"
            ),
            inline=True,
        )
        embed.add_field(
            name="🔗 Links",
            value=(
                "[Invite Bot](https://discord.com/oauth2/authorize?client_id=1209050248958312448&permissions=551903422464&scope=bot%20applications.commands) • "
                "[GitHub](https://github.com/codewithriza/PikaStatsBot) • "
                "[Pika Network](https://pika-network.net)"
            ),
            inline=False,
        )
        embed.add_field(
            name="🎮 Supported Games",
            value=" • ".join(
                [f"{v['emoji']} {v['display']}" for v in Config.GAME_TYPES.values()]
            ),
            inline=False,
        )

        await interaction.response.send_message(embed=embed)

    # ── Server Info Command ─────────────────────────────────────────

    @app_commands.command(name="serverinfo", description="📊 View Discord server information")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message(
                embed=error_embed(description="This command can only be used in a server.")
            )
            return

        embed = base_embed(
            title=f"📊 {guild.name}",
            color=Config.COLOR_PRIMARY,
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # General info
        embed.add_field(
            name="📋 General",
            value=(
                f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'}\n"
                f"**Created:** <t:{int(guild.created_at.timestamp())}:R>\n"
                f"**ID:** `{guild.id}`"
            ),
            inline=True,
        )

        # Member counts
        total = guild.member_count or 0
        embed.add_field(
            name="👥 Members",
            value=(
                f"**Total:** `{total}`\n"
                f"**Roles:** `{len(guild.roles)}`\n"
                f"**Emojis:** `{len(guild.emojis)}`"
            ),
            inline=True,
        )

        # Channel counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        embed.add_field(
            name="💬 Channels",
            value=(
                f"**Text:** `{text_channels}`\n"
                f"**Voice:** `{voice_channels}`\n"
                f"**Categories:** `{categories}`"
            ),
            inline=True,
        )

        # Boost info
        if guild.premium_subscription_count:
            embed.add_field(
                name="💎 Boosts",
                value=(
                    f"**Level:** `{guild.premium_tier}`\n"
                    f"**Boosts:** `{guild.premium_subscription_count}`"
                ),
                inline=True,
            )

        await interaction.response.send_message(embed=embed)

    # ── Invite Command ──────────────────────────────────────────────

    @app_commands.command(name="invite", description="🔗 Get the bot invite link")
    async def invite(self, interaction: discord.Interaction):
        embed = base_embed(
            title="🔗 Invite PikaStatsBot",
            description=(
                "Add PikaStatsBot to your Discord server!\n\n"
                "[**Click here to invite**](https://discord.com/oauth2/authorize?"
                "client_id=1209050248958312448&permissions=551903422464&scope=bot%20applications.commands)\n\n"
                "⭐ [Star us on GitHub](https://github.com/codewithriza/PikaStatsBot)"
            ),
            color=Config.COLOR_SUCCESS,
        )
        await interaction.response.send_message(embed=embed)

    # ── Daily Vote Reminder Task ────────────────────────────────────

    @tasks.loop(minutes=1)
    async def _vote_reminder(self):
        """Send daily vote reminder at configured time."""
        if Config.VOTE_REMINDER_USER_ID == 0:
            return

        try:
            tz = pytz.timezone(Config.VOTE_REMINDER_TIMEZONE)
            now = datetime.now(tz)
            if now.hour == Config.VOTE_REMINDER_HOUR and now.minute == 0:
                user = await self.bot.fetch_user(Config.VOTE_REMINDER_USER_ID)
                if user:
                    vote_lines = [
                        f"**Vote {i + 1}** — {link}"
                        for i, link in enumerate(Config.VOTE_LINKS)
                    ]
                    embed = base_embed(
                        title="🗳️ Daily Vote Reminder",
                        description=(
                            "Time to vote for Pika Network!\n\n"
                            + "\n".join(vote_lines)
                        ),
                        color=Config.COLOR_SUCCESS,
                    )
                    await user.send(embed=embed)
                    logger.info("Sent daily vote reminder to user %s", Config.VOTE_REMINDER_USER_ID)
        except Exception as e:
            logger.error("Error sending vote reminder: %s", e)

    @_vote_reminder.before_loop
    async def _before_vote_reminder(self):
        await self.bot.wait_until_ready()

    async def cog_load(self):
        """Start background tasks when cog loads."""
        if Config.VOTE_REMINDER_USER_ID != 0:
            self._vote_reminder.start()


async def setup(bot: commands.Bot):
    await bot.add_cog(UtilityCog(bot))
