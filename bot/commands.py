from discord_slash.utils.manage_commands import create_option

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
        ...
    ]
)
async def sw(ctx: SlashContext, player_name: str, interval: str = "total", mode: str = "solo"):
    ...

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
    ...

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
    ...
