# KSA Free BOT

**Author:** KSAGlory

**Community:** [discord.gg/ksahub](https://discord.gg/ksahub)

KSA Free BOT is a free, beginner-friendly Discord bot foundation. It includes useful slash commands, simple local storage, clear configuration, and optional one-click start and stop scripts.

This project was created after seeing children and adults with little coding experience get scammed while looking for a personal Discord bot. Some people receive unsafe downloads, hidden code, stolen tokens, or bots designed with malicious intentions. KSA Free BOT offers a small and readable starting point that people can inspect, understand, and build upon without paying for unnecessary features.

The project does not collect passwords, private messages, email addresses, birth years, or ages. It uses only the Discord permissions required by its commands.

## What You Get

- Twelve top-level slash commands with fourteen command actions
- A private birthday feature that stores only the month and day
- Button polls that remember votes after the bot restarts
- An administrator-only embed command
- Local JSON storage with no external database
- A protected `.env` file for the bot token
- `start.bat` and `stop.bat` for Windows
- A small codebase that can be used as a foundation for future updates

## Commands

### Information commands

- `/ping` shows the bot's current Discord connection latency.
- `/uptime` shows how long the bot has been online.
- `/userinfo [user]` shows basic account and server information. Leave the user option empty to view yourself.
- `/avatar [user]` displays a member's profile picture.
- `/serverinfo` shows basic information about the current server.

### Fun commands

- `/choose options` chooses from a comma-separated list, such as `pizza, burgers, pasta`.
- `/coinflip` returns Heads or Tails.
- `/roll [sides]` rolls a die. The number of sides can be between 2 and 1000.

### Message command

- `/embedmessage` sends a clean embed through the bot. Only server administrators can use it.

### Poll commands

- `/poll create` starts a poll with two to four choices.
- `/poll end` ends a poll and displays the final totals. Only the poll creator or a server administrator can end it.

### Birthday commands

- `/birthday set` privately saves your birthday month and day.
- `/birthday view` privately displays the birthday you saved.

### Help command

- `/help` displays the available command categories and the project credit.

## Requirements

Before starting, you need:

- Windows 10 or Windows 11
- Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
- A Discord account
- A Discord server where you have permission to add a bot

During the Python installation, select **Add Python to PATH**.

## Step 1: Create a Discord Application

1. Open the [Discord Developer Portal](https://discord.com/developers/applications).
2. Select **New Application**.
3. Enter a name for your bot and create the application.
4. Open **Bot** from the menu on the left.
5. Select **Reset Token** or **View Token**, then copy the bot token.

Your token works like a password. Do not send it to friends, post it in screenshots, paste it into support chats, or save it directly inside `bot.py`. If anyone sees the token, reset it immediately in the Discord Developer Portal.

KSA Free BOT does not require Message Content, Server Members, or Presence privileged intents.

## Step 2: Invite the Bot to Your Server

1. Open **OAuth2** in the Discord Developer Portal.
2. Find the **OAuth2 URL Generator**.
3. Under Scopes, select `bot` and `applications.commands`.
4. Under Bot Permissions, select:
   - View Channels
   - Send Messages
   - Embed Links
   - Read Message History
5. Copy the generated URL shown at the bottom of the page.
6. Paste the URL into your browser.
7. Choose your server, select **Continue**, and then select **Authorize**.

You do not need to add a redirect, enable Public Client, or use the Client Secret. The bot itself does not need Administrator permission. A person must already be a server administrator to use `/embedmessage`.

The bot will appear offline until you start it on your computer.

## Step 3: Copy Your Server ID

1. Open Discord.
2. Go to **User Settings**, then **Advanced**.
3. Enable **Developer Mode**.
4. Right-click your server icon.
5. Select **Copy Server ID**.

The server ID is a long number. It is different from your user ID, channel ID, and application ID.

## Step 4: Configure KSA Free BOT

1. Open the KSA Free BOT folder.
2. Double-click `start.bat`.
3. The first run creates `.env` and opens it in Notepad.
4. Replace `paste_your_bot_token_here` with your bot token.
5. Replace `paste_your_server_id_here` with your server ID.
6. Save the file and close Notepad.

The finished `.env` file should have this format:

```env
DISCORD_TOKEN=your_real_bot_token
DISCORD_GUILD_ID=your_server_id
```

Do not add quotation marks around either value.

## Step 5: Start the Bot

Double-click `start.bat` again. On the first proper start, the script creates a private Python environment and installs the two required packages. This can take a minute depending on your internet connection.

Keep the Command Prompt window open while the bot is running. When the window says **KSA Free BOT is online**, open Discord and run `/help`.

Commands are synchronized only to the server ID in `.env`, so they normally appear quickly.

## Stopping the Bot

Double-click `stop.bat`. You can also focus the bot's Command Prompt window and press `Ctrl+C`.

The shutdown script checks the saved process ID and the path to `bot.py` before stopping anything. It will not intentionally stop unrelated Python programs.

## Creating and Ending a Poll

Run `/poll create`, enter a question, and provide two to four choices. Members vote by selecting one of the buttons. They can change their vote until the poll ends.

To end a poll:

1. Make sure Discord Developer Mode is enabled.
2. Right-click the poll message.
3. Select **Copy Message ID**.
4. Run `/poll end` and paste the message ID.

The completed poll message shows the number of votes for each choice. Active polls and their votes are restored when the bot restarts.

## Birthday Privacy

`/birthday set` stores only a month and day. The bot does not ask for a birth year or calculate anyone's age. The confirmation and `/birthday view` response are private to the person using the command.

## Local Files and Privacy

The bot creates `data/ksa-free-bot.json` on your computer. This file can contain Discord user IDs, birthday month and day values, poll details, and poll votes. It does not contain your bot token.

The bot token is stored in `.env`. Both `.env` and the local JSON data are excluded from Git by `.gitignore`, so they are not included when the project is published correctly.

## Testing Checklist

After the bot comes online, check the following:

1. Run `/help` and confirm that the help message appears privately.
2. Run `/ping` and `/uptime`.
3. Try `/userinfo`, `/avatar`, and `/serverinfo`.
4. Try `/choose`, `/coinflip`, and `/roll`.
5. Use `/embedmessage` from an administrator account.
6. Create a poll, vote, change your vote, and end the poll.
7. Save and view a birthday.
8. Restart the bot and confirm that an active poll still accepts votes.

## Common Problems

### The commands do not appear

- Confirm that `DISCORD_GUILD_ID` contains the server ID, not your user ID.
- Invite the bot with both the `bot` and `applications.commands` scopes.
- Restart Discord if its command list is cached.
- Check the bot window for a setup or connection error.

### The bot cannot log in

The token may be missing, expired, or copied incorrectly. Reset it on the Developer Portal's Bot page, then replace the token in `.env`.

### A poll cannot be ended

Make sure you copied the poll message ID. The bot also needs View Channels and Read Message History permission in the channel containing the poll.

### The bot goes offline when the window closes

KSA Free BOT runs on your computer. Your computer and the bot's Command Prompt window must remain on. Be careful with websites offering free bot hosting, especially if they ask for your token without clearly explaining how it is stored and protected.

## Project Files

- `bot.py` contains the Discord client, slash commands, poll buttons, and error handling.
- `storage.py` manages the local birthday and poll data.
- `start.bat` prepares the Python environment and starts the bot.
- `stop.bat` safely runs the shutdown helper.
- `stop-bot.ps1` verifies and stops only this bot's Python process.
- `.env.example` shows the required configuration values.
- `requirements.txt` lists the required Python packages.
- `SECURITY.md` contains the security guidance for users and contributors.

## Building on This Foundation

The code is intentionally small enough for a beginner to follow. You can change the bot colour, adjust the help text, or add new commands by following the existing command examples.

Before adding code from another person or website, read it carefully. Avoid code that asks for extra Discord permissions, downloads unknown files, sends information to external websites, or requests a token through a message or web form.

## Credit and Community

KSA Free BOT was created by **KSAGlory**.

For project news and community support, visit [discord.gg/ksahub](https://discord.gg/ksahub).

## License

KSA Free BOT is released under the MIT License. You may use, study, modify, and share it under the terms in the `LICENSE` file.
