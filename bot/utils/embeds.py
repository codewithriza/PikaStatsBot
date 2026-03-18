"""
Embed builder utilities for consistent, beautiful Discord embeds.
"""

import discord
from datetime import datetime
from typing import Optional

from bot.config import Config


def base_embed(
    title: str,
    description: str = "",
    color: int = Config.COLOR_PRIMARY,
    thumbnail_url: Optional[str] = None,
    image_url: Optional[str] = None,
    footer_text: str = "PikaStatsBot • pika-network.net",
) -> discord.Embed:
    """Create a base embed with consistent styling."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text=footer_text, icon_url="https://pika-network.net/favicon.ico")
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    if image_url:
        embed.set_image(url=image_url)
    return embed


def error_embed(title: str = "❌ Error", description: str = "") -> discord.Embed:
    """Create an error embed."""
    return base_embed(title=title, description=description, color=Config.COLOR_ERROR)


def success_embed(title: str = "✅ Success", description: str = "") -> discord.Embed:
    """Create a success embed."""
    return base_embed(title=title, description=description, color=Config.COLOR_SUCCESS)


def loading_embed(message: str = "Fetching data from Pika Network...") -> discord.Embed:
    """Create a loading embed."""
    return base_embed(
        title="⏳ Loading...",
        description=message,
        color=Config.COLOR_INFO,
    )


def profile_embed(
    player_name: str,
    profile_data: dict,
    avatar_url: Optional[str] = None,
) -> discord.Embed:
    """Build a rich player profile embed."""
    rank_data = profile_data.get("rank", {})
    rank_display = rank_data.get("rankDisplay", "&7")
    level = rank_data.get("level", 0)
    experience = rank_data.get("experience", 0)
    percentage = rank_data.get("percentage", 0)

    # Parse last seen
    last_seen_ts = profile_data.get("lastSeen", 0)
    if last_seen_ts:
        last_seen_dt = datetime.fromtimestamp(last_seen_ts / 1000.0)
        now = datetime.now()
        diff = now - last_seen_dt
        total_mins = int(diff.total_seconds() // 60)
        days = total_mins // (24 * 60)
        hours = (total_mins % (24 * 60)) // 60
        minutes = total_mins % 60
        if days > 0:
            last_seen_str = f"{days}d {hours}h {minutes}m ago"
        elif hours > 0:
            last_seen_str = f"{hours}h {minutes}m ago"
        else:
            last_seen_str = f"{minutes}m ago"
        if total_mins < 5:
            last_seen_str = "🟢 Online now"
    else:
        last_seen_str = "Unknown"

    # Build progress bar for level
    filled = int(percentage / 10)
    progress_bar = "█" * filled + "░" * (10 - filled)

    # Clan info
    clan_info = "None"
    if profile_data.get("clan"):
        clan = profile_data["clan"]
        clan_name = clan.get("name", "Unknown")
        clan_tag = clan.get("tag", "")
        members = len(clan.get("members", []))
        clan_info = f"[{clan_tag}] {clan_name} ({members} members)"

    # Verification badges
    badges = []
    if profile_data.get("discord_verified"):
        badges.append("🔗 Discord")
    if profile_data.get("email_verified"):
        badges.append("📧 Email")
    if profile_data.get("discord_boosting"):
        badges.append("💎 Booster")
    badges_str = " • ".join(badges) if badges else "None"

    # Rank color mapping
    rank_colors = {
        "&7": Config.COLOR_PRIMARY,    # Default
        "&a": 0x55FF55,                # VIP
        "&b": 0x55FFFF,                # MVP
        "&6": 0xFFAA00,                # Legend
        "&c": 0xFF5555,                # Champion
        "&d": 0xFF55FF,                # Titan
    }
    color = rank_colors.get(rank_display, Config.COLOR_PRIMARY)

    # Rank name mapping
    rank_names = {
        "&7": "Default",
        "&a": "VIP",
        "&b": "MVP",
        "&6": "Legend",
        "&c": "Champion",
        "&d": "Titan",
        "&e": "Immortal",
    }
    rank_name = rank_names.get(rank_display, rank_display)

    # Check for special ranks from ranks list
    ranks = profile_data.get("ranks", [])
    if ranks:
        rank_name = ", ".join(ranks) if isinstance(ranks[0], str) else rank_name

    embed = base_embed(
        title=f"👤 {profile_data.get('username', player_name)}'s Profile",
        color=color,
        thumbnail_url=avatar_url,
    )

    embed.add_field(
        name="📊 General Info",
        value=(
            f"**Rank:** `{rank_name}`\n"
            f"**Level:** `{level}` ({percentage}%)\n"
            f"**EXP:** `{experience:,}`\n"
            f"`{progress_bar}` {percentage}%"
        ),
        inline=True,
    )

    embed.add_field(
        name="🕐 Status",
        value=(
            f"**Last Seen:** {last_seen_str}\n"
            f"**Badges:** {badges_str}"
        ),
        inline=True,
    )

    embed.add_field(
        name="🏰 Guild",
        value=clan_info,
        inline=False,
    )

    friends = profile_data.get("friends", [])
    embed.add_field(
        name="👥 Friends",
        value=f"`{len(friends)}` friends",
        inline=True,
    )

    return embed


def stats_embed(
    player_name: str,
    game_type: str,
    stats_data: dict,
    interval: str,
    mode: str,
    avatar_url: Optional[str] = None,
) -> discord.Embed:
    """Build a rich game stats embed with calculated ratios."""
    from bot.utils.api import PikaAPI

    game_config = Config.GAME_TYPES.get(game_type, {})
    game_display = game_config.get("display", game_type.capitalize())
    game_emoji = game_config.get("emoji", "🎮")
    game_color = game_config.get("color", Config.COLOR_PRIMARY)
    mode_display = game_config.get("modes", {}).get(mode, mode.capitalize())
    interval_display = Config.INTERVALS.get(interval, interval.capitalize())

    embed = base_embed(
        title=f"{game_emoji} {player_name}'s {game_display} Stats",
        description=f"**Mode:** `{mode_display}` • **Interval:** `{interval_display}`",
        color=game_color,
        thumbnail_url=avatar_url,
    )

    # Core stats
    stats_lines = []
    for stat_name, stat_data in stats_data.items():
        total = stat_data.get("metadata", {}).get("total", 0)
        rank = stat_data.get("metadata", {}).get("rank", None)
        rank_str = f" (#{rank})" if rank else ""
        stats_lines.append(f"**{stat_name}:** `{total:,}`{rank_str}")

    # Split stats into two columns if there are many
    if len(stats_lines) > 6:
        mid = len(stats_lines) // 2
        col1 = "\n".join(stats_lines[:mid])
        col2 = "\n".join(stats_lines[mid:])
        embed.add_field(name="📊 Statistics", value=col1, inline=True)
        embed.add_field(name="📈 More Stats", value=col2, inline=True)
    else:
        embed.add_field(
            name="📊 Statistics",
            value="\n".join(stats_lines) if stats_lines else "No stats available.",
            inline=False,
        )

    # Calculate ratios for PvP game types
    kills = PikaAPI.get_stat_value(stats_data, "Kills")
    deaths = PikaAPI.get_stat_value(stats_data, "Deaths")
    wins = PikaAPI.get_stat_value(stats_data, "Wins")
    losses = PikaAPI.get_stat_value(stats_data, "Losses")
    final_kills = PikaAPI.get_stat_value(stats_data, "Final kills")
    final_deaths = PikaAPI.get_stat_value(stats_data, "Final deaths")

    ratios = []
    if kills or deaths:
        kdr = PikaAPI.calculate_ratio(kills, deaths)
        ratios.append(f"**KDR:** `{kdr}`")
    if wins or losses:
        wlr = PikaAPI.calculate_ratio(wins, losses)
        ratios.append(f"**WLR:** `{wlr}`")
    if final_kills or final_deaths:
        fkdr = PikaAPI.calculate_ratio(final_kills, final_deaths)
        ratios.append(f"**FKDR:** `{fkdr}`")

    # Arrow accuracy
    arrows_shot = PikaAPI.get_stat_value(stats_data, "Arrows shot")
    arrows_hit = PikaAPI.get_stat_value(stats_data, "Arrows hit")
    if arrows_shot > 0:
        accuracy = (arrows_hit / arrows_shot) * 100
        ratios.append(f"**Arrow Accuracy:** `{accuracy:.1f}%`")

    if ratios:
        embed.add_field(
            name="📐 Ratios & Analysis",
            value="\n".join(ratios),
            inline=False,
        )

    return embed


def guild_embed(guild_name: str, guild_data: dict) -> discord.Embed:
    """Build a rich guild information embed."""
    creation_time = guild_data.get("creationTime", "")
    try:
        formatted_time = datetime.strptime(
            creation_time, "%Y-%m-%dT%H:%M:%S"
        ).strftime("%B %d, %Y at %I:%M %p")
    except (ValueError, TypeError):
        formatted_time = str(creation_time)

    members = guild_data.get("members", [])
    members_count = len(members)
    level_data = guild_data.get("leveling", {})
    level = level_data.get("level", 0) if isinstance(level_data, dict) else 0
    owner = guild_data.get("owner", {})
    owner_name = owner.get("username", "Unknown") if isinstance(owner, dict) else "Unknown"
    tag = guild_data.get("tag", "")

    embed = base_embed(
        title=f"🏰 [{tag}] {guild_name}",
        color=Config.COLOR_INFO,
    )

    embed.add_field(
        name="📊 Guild Info",
        value=(
            f"**Owner:** 👑 `{owner_name}`\n"
            f"**Level:** `{level}`\n"
            f"**Members:** `{members_count}`\n"
            f"**Created:** `{formatted_time}`"
        ),
        inline=False,
    )

    # Member list (show first 20, then indicate more)
    if members:
        member_names = []
        for m in members[:20]:
            user = m.get("user", {})
            username = user.get("username", "Unknown")
            member_names.append(f"• {username}")
        member_list = "\n".join(member_names)
        if members_count > 20:
            member_list += f"\n*...and {members_count - 20} more*"
        embed.add_field(
            name=f"👥 Members ({members_count})",
            value=f"```\n{chr(10).join([m.get('user', {}).get('username', '?') for m in members[:25]])}\n```"
            if members_count <= 25
            else member_list,
            inline=False,
        )

    return embed


def compare_embed(
    player1: str,
    player2: str,
    stats1: dict,
    stats2: dict,
    game_type: str,
    interval: str,
    mode: str,
    avatar1_url: Optional[str] = None,
    avatar2_url: Optional[str] = None,
) -> discord.Embed:
    """Build a player comparison embed."""
    from bot.utils.api import PikaAPI

    game_config = Config.GAME_TYPES.get(game_type, {})
    game_display = game_config.get("display", game_type.capitalize())
    game_emoji = game_config.get("emoji", "🎮")
    game_color = game_config.get("color", Config.COLOR_PRIMARY)
    mode_display = game_config.get("modes", {}).get(mode, mode.capitalize())
    interval_display = Config.INTERVALS.get(interval, interval.capitalize())

    embed = base_embed(
        title=f"{game_emoji} {player1} vs {player2} — {game_display}",
        description=f"**Mode:** `{mode_display}` • **Interval:** `{interval_display}`",
        color=game_color,
    )

    # Collect all stat names from both players
    all_stats = set(list(stats1.keys()) + list(stats2.keys()))

    p1_lines = []
    p2_lines = []
    comparison_lines = []

    for stat_name in sorted(all_stats):
        val1 = PikaAPI.get_stat_value(stats1, stat_name)
        val2 = PikaAPI.get_stat_value(stats2, stat_name)

        if val1 > val2:
            indicator = "🟢"
            indicator2 = "🔴"
        elif val2 > val1:
            indicator = "🔴"
            indicator2 = "🟢"
        else:
            indicator = "🟡"
            indicator2 = "🟡"

        comparison_lines.append(
            f"{indicator} **{stat_name}:** `{val1:,}` vs `{val2:,}` {indicator2}"
        )

    # Split into chunks if too many
    if len(comparison_lines) > 10:
        mid = len(comparison_lines) // 2
        embed.add_field(
            name=f"⚔️ {player1} vs {player2}",
            value="\n".join(comparison_lines[:mid]),
            inline=False,
        )
        embed.add_field(
            name="⚔️ Continued",
            value="\n".join(comparison_lines[mid:]),
            inline=False,
        )
    else:
        embed.add_field(
            name=f"⚔️ {player1} vs {player2}",
            value="\n".join(comparison_lines) if comparison_lines else "No stats to compare.",
            inline=False,
        )

    # Ratio comparison
    kills1 = PikaAPI.get_stat_value(stats1, "Kills")
    deaths1 = PikaAPI.get_stat_value(stats1, "Deaths")
    kills2 = PikaAPI.get_stat_value(stats2, "Kills")
    deaths2 = PikaAPI.get_stat_value(stats2, "Deaths")
    wins1 = PikaAPI.get_stat_value(stats1, "Wins")
    losses1 = PikaAPI.get_stat_value(stats1, "Losses")
    wins2 = PikaAPI.get_stat_value(stats2, "Wins")
    losses2 = PikaAPI.get_stat_value(stats2, "Losses")

    ratio_lines = []
    if kills1 or deaths1 or kills2 or deaths2:
        kdr1 = PikaAPI.calculate_ratio(kills1, deaths1)
        kdr2 = PikaAPI.calculate_ratio(kills2, deaths2)
        ratio_lines.append(f"**KDR:** `{kdr1}` vs `{kdr2}`")
    if wins1 or losses1 or wins2 or losses2:
        wlr1 = PikaAPI.calculate_ratio(wins1, losses1)
        wlr2 = PikaAPI.calculate_ratio(wins2, losses2)
        ratio_lines.append(f"**WLR:** `{wlr1}` vs `{wlr2}`")

    if ratio_lines:
        embed.add_field(
            name="📐 Ratio Comparison",
            value="\n".join(ratio_lines),
            inline=False,
        )

    embed.set_footer(text=f"🟢 = Better • 🔴 = Worse • 🟡 = Tied | PikaStatsBot")
    return embed


def friends_embed(
    player_name: str,
    friends_list: list,
    avatar_url: Optional[str] = None,
) -> discord.Embed:
    """Build a friends list embed."""
    embed = base_embed(
        title=f"👥 {player_name}'s Friends ({len(friends_list)})",
        color=Config.COLOR_PRIMARY,
        thumbnail_url=avatar_url,
    )

    if not friends_list:
        embed.description = "This player has no friends. 😢"
        return embed

    # Show friends in pages of 25
    friend_names = [f.get("username", "Unknown") for f in friends_list[:50]]
    if len(friend_names) <= 25:
        embed.add_field(
            name="Friends",
            value="```\n" + "\n".join(friend_names) + "\n```",
            inline=False,
        )
    else:
        mid = len(friend_names) // 2
        embed.add_field(
            name="Friends (1/2)",
            value="```\n" + "\n".join(friend_names[:mid]) + "\n```",
            inline=True,
        )
        embed.add_field(
            name="Friends (2/2)",
            value="```\n" + "\n".join(friend_names[mid:]) + "\n```",
            inline=True,
        )

    if len(friends_list) > 50:
        embed.set_footer(text=f"Showing 50 of {len(friends_list)} friends | PikaStatsBot")

    return embed


def skin_embed(
    player_name: str,
    uuid: str,
    avatar_url: Optional[str] = None,
) -> discord.Embed:
    """Build a player skin display embed."""
    from bot.utils.api import PikaAPI

    embed = base_embed(
        title=f"🎨 {player_name}'s Skin",
        color=Config.COLOR_PRIMARY,
        thumbnail_url=PikaAPI.get_avatar_url(uuid, size=128),
        image_url=PikaAPI.get_body_url(uuid),
    )

    embed.add_field(
        name="🔗 Download Links",
        value=(
            f"[Full Skin]({PikaAPI.get_skin_url(uuid)}) • "
            f"[Head Render]({PikaAPI.get_head_url(uuid)}) • "
            f"[Body Render]({PikaAPI.get_body_url(uuid)})"
        ),
        inline=False,
    )

    return embed
