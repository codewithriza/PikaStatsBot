import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
import datetime
import pytz
import requests
from utils import update_presence, get_profile_info, get_game_stats, get_previous_guild_data, time_since

bot = commands.Bot(command_prefix='!')
slash = SlashCommand(bot, sync_commands=True)

@tasks.loop(hours=24)  # Run every 24 hours
async def send_daily_vote_reminder():
    ...

@bot.event
async def on_ready():
    ...

@slash.slash(
    name="daily-vote",
    description="Get the daily vote reminder",
)
async def daily_vote(ctx: SlashContext):
    ...

@bot.event
async def on_guild_join(guild):
    ...

@bot.event
async def on_guild_remove(guild):
    ...

bot.run('YOUR_TOKEN_HERE')
