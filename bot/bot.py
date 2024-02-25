import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext, ButtonStyle
from discord_slash.utils.manage_commands import create_option
import datetime
import pytz
import requests
from datetime import datetime



bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)

@tasks.loop(hours=24)  # Run every 24 hours
async def send_daily_vote_reminder():
    now = datetime.now(pytz.timezone('Asia/Kolkata'))
    if now.hour == 18 and now.minute == 0:  # Check if it's 6:00 PM
        user_id = YOUR_USER_ID_HERE  
        user = await bot.fetch_user(user_id)
        if user:
            message = (
                "**Daily Vote Reminder**\n"
                "**Vote 1** = <https://vote.pika-network.net/1>\n"
                "**Vote 2** = <https://vote.pika-network.net/2>\n"
                "**Vote 3** = <https://vote.pika-network.net/3>\n"
                "**Vote 4** = <https://vote.pika-network.net/4>\n"
                "**Vote 5** = <https://vote.pika-network.net/5>\n"
                "**Vote 6** = <https://vote.pika-network.net/6>\n"
                "**Vote 7** = <https://vote.pika-network.net/7>\n"
            )
            await user.send(message)

@bot.event
async def on_ready():
    await update_presence(bot)
    send_daily_vote_reminder.start()  # Start the daily vote reminder task
    print(f'Logged in as {bot.user.name}')
    print('Bot is in the following guilds:')
    for guild in bot.guilds:
        print(f'- {guild.name} (ID: {guild.id}, Members: {guild.member_count})')

@slash.slash(
    name="daily-vote",
    description="Get the daily vote reminder",
)
async def daily_vote(ctx: SlashContext):
    user = ctx.author
    message = (
        "**Daily Vote Reminder**\n"
        "**Vote 1** = <https://vote.pika-network.net/1>\n"
        "**Vote 2** = <https://vote.pika-network.net/2>\n"
        "**Vote 3** = <https://vote.pika-network.net/3>\n"
        "**Vote 4** = <https://vote.pika-network.net/4>\n"
        "**Vote 5** = <https://vote.pika-network.net/5>\n"
        "**Vote 6** = <https://vote.pika-network.net/6>\n"
        "**Vote 7** = <https://vote.pika-network.net/7>\n"
    )
    await user.send(message)
    await ctx.send("Daily vote reminder sent!")


@bot.event
async def on_guild_join(guild):
    await update_presence(bot)

@bot.event
async def on_guild_remove(guild):
    await update_presence(bot)

async def update_presence(bot):
    servers = len(bot.guilds)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"/help | {servers} servers"))

def get_previous_guild_data(guild_name):
    return guild_data_cache.get(guild_name, {'members': []})

def time_since(dt):
    now = datetime.now()
    diff = now - dt
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days} days, {hours} hours, {minutes} minutes"

@slash.slash(
    name="guild-logs",
    description="Set up guild logs for a Pika Network guild",
    options=[
        create_option(
            name="guild_name",
            description="The name of the guild",
            option_type=3,
            required=True
        )
    ]
)
async def guild_logs(ctx: SlashContext, guild_name: str):
    global guild_data_cache
    await ctx.defer()

    url_guild = f'https://stats.pika-network.net/api/clans/{guild_name}'
    response_guild = requests.get(url_guild)
    if response_guild.status_code == 200:
        guild_data = response_guild.json()
        if guild_data:
            previous_guild_data = get_previous_guild_data(guild_name)
            previous_member_count = len(previous_guild_data.get('members', []))
            current_member_count = len(guild_data['members'])
            member_count_change = current_member_count - previous_member_count

            if member_count_change > 0:
                change_type = "Joined"
                member_list = guild_data['members'][-member_count_change:]
                emoji = ":green_circle:"  # Emoji for join
            elif member_count_change < 0:
                change_type = "Left"
                member_list = previous_guild_data['members'][:abs(member_count_change)]
                emoji = ":red_circle:"  # Emoji for leave
            else:
                return await ctx.send("No changes in member count.")

            guild_data_cache[guild_name] = guild_data

            embed = discord.Embed(
                title=f"{guild_name} Guild Logs | Pikachu's Stats Bot",
                color=discord.Color.blue()
            )
            embed.add_field(name=f"{emoji} {change_type}:", value="\n".join([f"{emoji} {member['user']['username']}" for member in member_list]), inline=False)
            embed.add_field(name=f":date: {change_type}:", value=f"{time_since(datetime.now())}\n{datetime.now().strftime('%B %d, %Y %I:%M %p')}", inline=False)
            embed.add_field(name=":members: Guild Members", value=f":add: {previous_member_count} -> {current_member_count}" if member_count_change > 0 else f":sub: {previous_member_count} -> {current_member_count}", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No information found for guild '{guild_name}'.")
    else:
        await ctx.send(f"Failed to fetch guild information for '{guild_name}'.")

    await ctx.send("Command successfully set up! Sit back, relax, and I'll let you know of any changes in the server.")


# Define other commands and functions here


# Define a function to get the profile info of a player
def get_profile_info(player_name):
    # Fetch additional player information
    url_info = f'https://stats.pika-network.net/api/profile/{player_name}'
    response_info = requests.get(url_info)
    if response_info.status_code == 200:
        data_info = response_info.json()
        rank_data = data_info.get('rank', {})
        rank_display_name = rank_data.get('displayName', 'N/A')
        level = rank_data.get('level', 'N/A')
        percentage = rank_data.get('percentage', 'N/A')
        last_seen_timestamp = data_info.get('lastSeen', 0)
        last_seen_datetime = datetime.fromtimestamp(last_seen_timestamp / 1000.0)
        now = datetime.now()
        time_difference = now - last_seen_datetime
        total_minutes = time_difference.total_seconds() // 60
        days = int(total_minutes // (24 * 60))
        hours = int((total_minutes % (24 * 60)) // 60)
        minutes = int(total_minutes % 60)

        last_seen_message = f"{days} days, {hours} hrs and {minutes} mins" if days > 0 else f"{hours} hrs and {minutes} mins"

        guild_info = ''
        if 'clan' in data_info and data_info['clan']:
            clan_data = data_info['clan']
            clan_name = clan_data.get('name', 'N/A')
            clan_tag = clan_data.get('tag', 'N/A')
            members_count = len(clan_data.get('members', []))
            guild_info = f"**Guild**: `{clan_tag}` ({clan_name})   **Members Count**: `{members_count}`\n" if clan_name != 'N/A' else ''

        profile_info = (
            f"> **{player_name}'s**\n"
            f"> **Rank**: `{rank_display_name}`\n"
            f"> **Level**: `{level}`\n"
            f"> **Percentage**: `{percentage}`\n"
            f"> {guild_info}"
            f"> **Last seen**:  `{last_seen_message}`\n"
        )
    else:
        profile_info = "Player info not available."
    return profile_info

# Define a function to get the game stats of a player
def get_game_stats(player_name, game_type, interval, mode):
    # Fetch player stats based on the interval and game type
    url_stats = f'https://stats.pika-network.net/api/profile/{player_name}/leaderboard?type={game_type}&interval={interval}&mode={mode}'
    response_stats = requests.get(url_stats)
    if response_stats.status_code == 200:
        stats_data = response_stats.json()

        # Construct the message with the stats
        stats_message = ""
        for stat_name, stat_data in stats_data.items():
            total = stat_data.get('metadata', {}).get('total', 'N/A')
            rank = stat_data.get('metadata', {}).get('rank', 'N/A')
            stats_message += f"> **{stat_name.capitalize()}**: `{total}`   **Rank**: `{rank}`\n"
    else:
        stats_message = "Game stats not available."
    return stats_message

# Define a slash command for skywars stats
@slash.slash(
    name="sw",
    description="Get Pika Network skywars stats",
    options=[
        create_option(
            name="player_name",
            description="The Pika Network username",
            option_type=3,
            required=True
        ),
        create_option(
            name="interval",
            description="The time interval for the stats",
            option_type=3,
            required=False,
            choices=[
                {"name": "Total", "value": "total"},
                {"name": "Monthly", "value": "monthly"},
                {"name": "Weekly", "value": "weekly"},
                {"name": "Daily", "value": "daily"}
            ]
        ),
        create_option(
            name="mode",
            description="The skywars mode for the stats",
            option_type=3,
            required=False,
            choices=[
                {"name": "Solo", "value": "solo"},
                {"name": "Doubles", "value": "doubles"},
                {"name": "Mega", "value": "mega"},
                {"name": "Ranked", "value": "ranked"}
            ]
        )
    ]
)
async def sw(ctx: SlashContext, player_name: str, interval: str = "total", mode: str = "solo"):
    await ctx.defer()

    # Get the profile info and the skywars stats of the player
    profile_info = get_profile_info(player_name)
    skywars_stats = get_game_stats(player_name, "skywars", interval, mode)

    # Send the message with the stats
    await ctx.send(
        embed=discord.Embed(
            title=f"{player_name}'s Skywars Stats",
            description=f"{profile_info}\n**Skywars Stats**\n**Interval**: `{interval.capitalize()}`\n**Mode**: `{mode.capitalize()}`\n{skywars_stats}",
            color=discord.Color.blue()
        )
    )

# Define a slash command for bedwars stats
@slash.slash(
    name="bw",
    description="Get Pika Network bedwars stats",
    options=[
        create_option(
            name="player_name",
            description="The Pika Network username",
            option_type=3,
            required=True
        ),
        create_option(
            name="interval",
            description="The time interval for the stats",
            option_type=3,
            required=False,
            choices=[
                {"name": "Total", "value": "total"},
                {"name": "Monthly", "value": "monthly"},
                {"name": "Weekly", "value": "weekly"},
                {"name": "Daily", "value": "daily"}
            ]
        ),
        create_option(
            name="mode",
            description="The bedwars mode for the stats",
            option_type=3,
            required=False,
            choices=[
                {"name": "Solo", "value": "solo"},
                {"name": "Doubles", "value": "doubles"},
                {"name": "3v3v3v3", "value": "3v3v3v3"},
                {"name": "4v4v4v4", "value": "4v4v4v4"},
                {"name": "Ranked", "value": "ranked"}
            ]
        )
    ]
)
async def bw(ctx: SlashContext, player_name: str, interval: str = "total", mode: str = "solo"):
    await ctx.defer()

    # Get the profile info and the bedwars stats of the player
    profile_info = get_profile_info(player_name)
    bedwars_stats = get_game_stats(player_name, "bedwars", interval, mode)

    # Send the message with the stats
    await ctx.send(
        embed=discord.Embed(
            title=f"{player_name}'s Bedwars Stats",
            description=f"{profile_info}\n**Bedwars Stats**\n**Interval**: `{interval.capitalize()}`\n**Mode**: `{mode.capitalize()}`\n{bedwars_stats}",
            color=discord.Color.blue()
        )
    )

@slash.slash(
    name="friends",
    description="List a player's friends",
    options=[
        create_option(
            name="player_name",
            description="The Pika Network username",
            option_type=3,
            required=True
        )
    ]
)
async def friends(ctx: SlashContext, player_name: str):
    await ctx.defer()

    # Fetch the player's profile from the API
    url_profile = f'https://stats.pika-network.net/api/profile/{player_name}'
    response_profile = requests.get(url_profile)
    if response_profile.status_code == 200:
        data_profile = response_profile.json()
        friends_data = data_profile.get('friends', [])

        # Extract usernames from the friends' data
        friends = [friend.get('username', 'Unknown') for friend in friends_data]

        # Construct the message with the list of friends
        friends_list = "\n".join(friends) if friends else "No friends found."

        # Send the message with the list of friends
        await ctx.send(
            embed=discord.Embed(
                title=f"{player_name}'s Friends",
                description=f"```{friends_list}```",
                color=discord.Color.blue()
            )
        )
    else:
        await ctx.send("Player info not available.")


@slash.slash(
    name="guild-info",
    description="Get information about a Pika Network guild",
    options=[
        create_option(
            name="guild_name",
            description="The name of the guild",
            option_type=3,
            required=True
        )
    ]
)
async def guild_info(ctx: SlashContext, guild_name: str):
    await ctx.defer()

    url_guild = f'https://stats.pika-network.net/api/clans/{guild_name}'
    response_guild = requests.get(url_guild)
    if response_guild.status_code == 200:
        guild_data = response_guild.json()
        if guild_data:
            creation_time = guild_data.get('creationTime', 'N/A')
            formatted_creation_time = datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%S').strftime('%B %d, %Y %I:%M %p')
            members_count = len(guild_data.get('members', []))
            level = guild_data.get('leveling', {}).get('level', 'N/A')
            creator_name = guild_data.get('owner', {}).get('username', 'Unknown')

            member_list = "\n".join([f":bust_in_silhouette: {member.get('user', {}).get('username', 'Unknown')}" for member in guild_data.get('members', [])])

            member_list = f":crown: {creator_name}\n{member_list}"
          
            await ctx.send(
                embed=discord.Embed(
                    title=f"{guild_name} Guild Information | Pikachu's Stats",
                    description=f":bar_chart: Level: {level} | :hourglass: Created: `{formatted_creation_time}`\n\nMembers({members_count}):\n{member_list}",
                    color=discord.Color.blue()
                )
            )
        else:
            await ctx.send(f"No information found for guild '{guild_name}'.")
    else:
        await ctx.send(f"Failed to fetch guild information for '{guild_name}'.")
bot.run('Paste your token')
