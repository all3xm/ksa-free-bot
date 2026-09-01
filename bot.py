from __future__ import annotations

import calendar
import logging
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import discord
from discord import app_commands
from dotenv import load_dotenv

from storage import JsonStorage


__author__ = "KSAGlory"

PROJECT_NAME = "KSA Free BOT"
COMMUNITY = "discord.gg/ksahub"
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
PID_FILE = DATA_DIR / "bot.pid"
ALLOWED_MENTIONS = discord.AllowedMentions.none()
COLOUR = discord.Colour.from_rgb(88, 101, 242)


class ConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class Config:
    token: str
    guild_id: int


def load_config() -> Config:
    load_dotenv(PROJECT_DIR / ".env")
    token = os.getenv("DISCORD_TOKEN", "").strip()
    guild_text = os.getenv("DISCORD_GUILD_ID", "").strip()
    if not token or token == "paste_your_bot_token_here":
        raise ConfigurationError("Add your bot token to the .env file.")
    try:
        guild_id = int(guild_text)
    except ValueError as error:
        raise ConfigurationError("DISCORD_GUILD_ID must be your numeric Discord server ID.") from error
    if guild_id <= 0:
        raise ConfigurationError("DISCORD_GUILD_ID must be a positive number.")
    return Config(token=token, guild_id=guild_id)


def timestamp(value: datetime | None) -> str:
    if value is None:
        return "Not available"
    return discord.utils.format_dt(value, style="F")


def duration(seconds: float) -> str:
    total = max(0, int(seconds))
    days, remainder = divmod(total, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def get_bot(interaction: discord.Interaction) -> "KSAFreeBot":
    client = interaction.client
    if not isinstance(client, KSAFreeBot):
        raise RuntimeError("Unexpected Discord client type.")
    return client


def poll_embed(poll: dict[str, object], *, ended: bool = False) -> discord.Embed:
    options = list(poll["options"])
    votes = dict(poll.get("votes", {}))
    totals = [0] * len(options)
    for raw_index in votes.values():
        index = int(raw_index)
        if 0 <= index < len(totals):
            totals[index] += 1

    embed = discord.Embed(
        title=str(poll["question"]),
        colour=discord.Colour.green() if ended else COLOUR,
    )
    if ended:
        lines = [f"**{index + 1}. {option}**: {totals[index]} vote(s)" for index, option in enumerate(options)]
        embed.description = "\n".join(lines) or "No options"
        embed.set_footer(text=f"Poll ended • {sum(totals)} total vote(s)")
    else:
        embed.description = "\n".join(f"**{index + 1}.** {option}" for index, option in enumerate(options))
        embed.set_footer(text="Choose one option below. You can change your vote until the poll ends.")
    return embed


class PollView(discord.ui.View):
    def __init__(self, bot: "KSAFreeBot", message_id: int, options: list[str], *, disabled: bool = False) -> None:
        super().__init__(timeout=None)
        self.bot = bot
        self.message_id = message_id
        styles = (
            discord.ButtonStyle.primary,
            discord.ButtonStyle.success,
            discord.ButtonStyle.secondary,
            discord.ButtonStyle.danger,
        )
        for index, option in enumerate(options):
            button = discord.ui.Button(
                label=f"{index + 1}. {option}"[:80],
                style=styles[index % len(styles)],
                custom_id=f"ksa_free_poll:{message_id}:{index}",
                disabled=disabled,
            )

            async def vote_callback(interaction: discord.Interaction, selected: int = index) -> None:
                poll = self.bot.storage.vote(self.message_id, interaction.user.id, selected)
                if poll is None:
                    await interaction.response.send_message("This poll has already ended.", ephemeral=True)
                    return
                selected_option = str(poll["options"][selected])
                await interaction.response.send_message(
                    f"Your vote is saved for **{selected_option}**.",
                    ephemeral=True,
                    allowed_mentions=ALLOWED_MENTIONS,
                )

            button.callback = vote_callback
            self.add_item(button)


@app_commands.command(name="ping", description="Show the bot's current connection latency.")
async def ping(interaction: discord.Interaction) -> None:
    latency = round(interaction.client.latency * 1000)
    await interaction.response.send_message(f"Pong! **{latency} ms**")


@app_commands.command(name="uptime", description="Show how long the bot has been online.")
async def uptime(interaction: discord.Interaction) -> None:
    bot = get_bot(interaction)
    await interaction.response.send_message(f"I have been online for **{duration(time.monotonic() - bot.started_at)}**.")


@app_commands.command(name="userinfo", description="Show simple information about a server member.")
@app_commands.describe(user="The member to view (leave empty to view yourself).")
async def userinfo(interaction: discord.Interaction, user: discord.Member | None = None) -> None:
    member = user or interaction.user
    if not isinstance(member, discord.Member):
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    embed = discord.Embed(title=member.display_name, colour=member.colour if member.colour.value else COLOUR)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="User ID", value=str(member.id), inline=True)
    embed.add_field(name="Account created", value=timestamp(member.created_at), inline=False)
    embed.add_field(name="Joined this server", value=timestamp(member.joined_at), inline=False)
    embed.add_field(name="Roles", value=str(max(0, len(member.roles) - 1)), inline=True)
    await interaction.response.send_message(embed=embed, allowed_mentions=ALLOWED_MENTIONS)


@app_commands.command(name="avatar", description="Show a member's profile picture.")
@app_commands.describe(user="The member whose avatar you want to see.")
async def avatar(interaction: discord.Interaction, user: discord.Member | None = None) -> None:
    member = user or interaction.user
    embed = discord.Embed(title=f"{member.display_name}'s avatar", colour=COLOUR)
    embed.set_image(url=member.display_avatar.url)
    await interaction.response.send_message(embed=embed, allowed_mentions=ALLOWED_MENTIONS)


@app_commands.command(name="serverinfo", description="Show simple information about this Discord server.")
async def serverinfo(interaction: discord.Interaction) -> None:
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    embed = discord.Embed(title=guild.name, colour=COLOUR)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Server ID", value=str(guild.id), inline=True)
    embed.add_field(name="Members", value=str(guild.member_count or "Not available"), inline=True)
    embed.add_field(name="Channels", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="Created", value=timestamp(guild.created_at), inline=False)
    await interaction.response.send_message(embed=embed)


@app_commands.command(name="choose", description="Let the bot choose between comma-separated options.")
@app_commands.describe(options="Example: pizza, burgers, pasta")
async def choose(interaction: discord.Interaction, options: str) -> None:
    choices = [item.strip() for item in options.split(",") if item.strip()]
    if len(choices) < 2:
        await interaction.response.send_message("Please give me at least two options separated by commas.", ephemeral=True)
        return
    if len(choices) > 20:
        await interaction.response.send_message("Please use 20 options or fewer.", ephemeral=True)
        return
    await interaction.response.send_message(
        f"I choose: **{random.choice(choices)[:200]}**",
        allowed_mentions=ALLOWED_MENTIONS,
    )


@app_commands.command(name="coinflip", description="Flip a coin.")
async def coinflip(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(f"The coin landed on **{random.choice(('Heads', 'Tails'))}**!")


@app_commands.command(name="roll", description="Roll a die with your chosen number of sides.")
@app_commands.describe(sides="Number of sides, from 2 to 1000.")
async def roll(interaction: discord.Interaction, sides: app_commands.Range[int, 2, 1000] = 6) -> None:
    await interaction.response.send_message(f"You rolled **{random.randint(1, sides)}** on a d{sides}.")


@app_commands.command(name="embedmessage", description="Send a clean embed message as the bot (admins only).")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(title="Embed title", message="Embed message", colour="blue, green, orange, purple, or red")
async def embedmessage(
    interaction: discord.Interaction,
    title: app_commands.Range[str, 1, 256],
    message: app_commands.Range[str, 1, 4000],
    colour: str = "blue",
) -> None:
    colours = {
        "blue": COLOUR,
        "green": discord.Colour.green(),
        "orange": discord.Colour.orange(),
        "purple": discord.Colour.purple(),
        "red": discord.Colour.red(),
    }
    selected = colours.get(colour.lower())
    if selected is None:
        await interaction.response.send_message("Colour must be blue, green, orange, purple, or red.", ephemeral=True)
        return
    embed = discord.Embed(title=title, description=message, colour=selected)
    embed.set_footer(text=f"Sent by {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed, allowed_mentions=ALLOWED_MENTIONS)


birthday_group = app_commands.Group(name="birthday", description="Save or view your birthday.")


@birthday_group.command(name="set", description="Save your birthday privately (month and day only).")
@app_commands.describe(month="Birthday month, from 1 to 12", day="Birthday day, from 1 to 31")
async def birthday_set(
    interaction: discord.Interaction,
    month: app_commands.Range[int, 1, 12],
    day: app_commands.Range[int, 1, 31],
) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try:
        datetime(2000, month, day)
    except ValueError:
        await interaction.response.send_message("That month and day are not a valid date.", ephemeral=True)
        return
    get_bot(interaction).storage.set_birthday(interaction.guild_id, interaction.user.id, month, day)
    await interaction.response.send_message(
        f"Saved! Your birthday is **{calendar.month_name[month]} {day}**.",
        ephemeral=True,
    )


@birthday_group.command(name="view", description="View the birthday you saved.")
async def birthday_view(interaction: discord.Interaction) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    birthday = get_bot(interaction).storage.get_birthday(interaction.guild_id, interaction.user.id)
    if birthday is None:
        await interaction.response.send_message("You have not saved a birthday yet. Use `/birthday set`.", ephemeral=True)
        return
    await interaction.response.send_message(
        f"Your saved birthday is **{calendar.month_name[birthday['month']]} {birthday['day']}**.",
        ephemeral=True,
    )


poll_group = app_commands.Group(name="poll", description="Create or end a button poll.")


@poll_group.command(name="create", description="Create a poll with two to four choices.")
@app_commands.describe(
    question="The poll question",
    option1="First choice",
    option2="Second choice",
    option3="Optional third choice",
    option4="Optional fourth choice",
)
async def poll_create(
    interaction: discord.Interaction,
    question: app_commands.Range[str, 1, 256],
    option1: app_commands.Range[str, 1, 80],
    option2: app_commands.Range[str, 1, 80],
    option3: app_commands.Range[str, 1, 80] | None = None,
    option4: app_commands.Range[str, 1, 80] | None = None,
) -> None:
    if interaction.guild_id is None or interaction.channel_id is None:
        await interaction.response.send_message("This command can only be used in a server channel.", ephemeral=True)
        return
    options = [value for value in (option1, option2, option3, option4) if value]
    if len({value.casefold() for value in options}) != len(options):
        await interaction.response.send_message("Each poll option must be different.", ephemeral=True)
        return
    poll = {"question": question, "options": options, "votes": {}}
    await interaction.response.send_message(embed=poll_embed(poll), allowed_mentions=ALLOWED_MENTIONS)
    message = await interaction.original_response()
    bot = get_bot(interaction)
    bot.storage.create_poll(
        message.id,
        interaction.guild_id,
        interaction.channel_id,
        interaction.user.id,
        question,
        options,
    )
    await message.edit(view=PollView(bot, message.id, options))


@poll_group.command(name="end", description="End one of your polls and show its results.")
@app_commands.describe(message_id="Right-click the poll, Copy Message ID, and paste it here.")
async def poll_end(interaction: discord.Interaction, message_id: str) -> None:
    if interaction.guild_id is None:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
        return
    try:
        poll_id = int(message_id)
    except ValueError:
        await interaction.response.send_message("Message ID must contain numbers only.", ephemeral=True)
        return
    bot = get_bot(interaction)
    poll = bot.storage.get_poll(poll_id)
    if poll is None or int(poll["guild_id"]) != interaction.guild_id:
        await interaction.response.send_message("I could not find an active poll with that message ID.", ephemeral=True)
        return
    if poll.get("ended", False):
        await interaction.response.send_message("That poll has already ended.", ephemeral=True)
        return
    is_admin = isinstance(interaction.user, discord.Member) and interaction.user.guild_permissions.administrator
    if interaction.user.id != int(poll["creator_id"]) and not is_admin:
        await interaction.response.send_message("Only the poll creator or an administrator can end it.", ephemeral=True)
        return
    channel = bot.get_channel(int(poll["channel_id"]))
    if not isinstance(channel, discord.TextChannel | discord.Thread):
        await interaction.response.send_message("I can no longer access the channel containing that poll.", ephemeral=True)
        return
    try:
        message = await channel.fetch_message(poll_id)
    except (discord.NotFound, discord.Forbidden):
        await interaction.response.send_message("I could not access that poll message.", ephemeral=True)
        return
    ended = bot.storage.end_poll(poll_id)
    if ended is None:
        await interaction.response.send_message("That poll has already ended.", ephemeral=True)
        return
    await message.edit(embed=poll_embed(ended, ended=True), view=PollView(bot, poll_id, list(ended["options"]), disabled=True))
    await interaction.response.send_message("Poll ended and results posted.", ephemeral=True)


@app_commands.command(name="help", description="Show every command and what it does.")
async def help_command(interaction: discord.Interaction) -> None:
    embed = discord.Embed(
        title=f"{PROJECT_NAME} Help",
        description="A useful set of everyday commands. Commands marked 🔒 require Administrator permission.",
        colour=COLOUR,
    )
    embed.add_field(name="Information", value="`/ping` `/uptime` `/userinfo` `/avatar` `/serverinfo`", inline=False)
    embed.add_field(name="Fun", value="`/choose` `/coinflip` `/roll`", inline=False)
    embed.add_field(name="Messages", value="`/embedmessage` 🔒", inline=False)
    embed.add_field(name="Polls", value="`/poll create` `/poll end`", inline=False)
    embed.add_field(name="Birthday", value="`/birthday set` `/birthday view`", inline=False)
    embed.set_footer(text=f"Created by {__author__} | Community: {COMMUNITY}")
    await interaction.response.send_message(embed=embed, ephemeral=True)


TOP_LEVEL_COMMANDS = (
    ping,
    uptime,
    userinfo,
    avatar,
    serverinfo,
    choose,
    coinflip,
    roll,
    embedmessage,
    birthday_group,
    poll_group,
    help_command,
)


class KSACommandTree(app_commands.CommandTree):
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.MissingPermissions):
            message = "You need Administrator permission to use this command."
        elif isinstance(error, app_commands.CommandOnCooldown):
            message = f"Please wait {error.retry_after:.1f} seconds and try again."
        else:
            logging.error(
                "Command failed: %s",
                type(error).__name__,
                exc_info=(type(error), error, error.__traceback__),
            )
            message = "Something went wrong while running that command."
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            logging.exception("Could not send the command error message")


class KSAFreeBot(discord.Client):
    def __init__(self, config: Config) -> None:
        intents = discord.Intents.none()
        intents.guilds = True
        super().__init__(intents=intents, activity=discord.Game(name=f"/help | {PROJECT_NAME}"))
        self.config = config
        self.tree = KSACommandTree(self)
        self.guild = discord.Object(id=config.guild_id)
        self.storage = JsonStorage(DATA_DIR / "ksa-free-bot.json")
        self.started_at = time.monotonic()
        for command in TOP_LEVEL_COMMANDS:
            self.tree.add_command(command, guild=self.guild)

    async def setup_hook(self) -> None:
        for message_id, poll in self.storage.active_polls():
            self.add_view(PollView(self, message_id, list(poll["options"])), message_id=message_id)
        synced = await self.tree.sync(guild=self.guild)
        print(f"Ready: synchronized {len(synced)} top-level commands.")

    async def on_ready(self) -> None:
        if self.user:
            print(f"Logged in as {self.user} ({self.user.id})")
            print(f"{PROJECT_NAME} is online. Keep this window open.")
            print(f"Created by {__author__} | Community: {COMMUNITY}")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        config = load_config()
        bot = KSAFreeBot(config)
    except (ConfigurationError, RuntimeError) as error:
        print(f"Setup error: {error}")
        return 2

    DATA_DIR.mkdir(exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="ascii")
    try:
        bot.run(config.token, log_handler=None)
    except discord.LoginFailure:
        print("Login failed. Check the token in your .env file.")
        return 3
    except KeyboardInterrupt:
        print("Bot stopped.")
    finally:
        try:
            PID_FILE.unlink(missing_ok=True)
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
