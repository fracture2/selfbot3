import discord
import time
import random
import asyncio
import requests
import aiohttp
import pyfiglet
import sys
import os
import json
import datetime
from PIL import Image, ImageDraw, ImageFont
from discord import Streaming, Status
import io
import textwrap
from discord import Status, Game
from discord.ext import commands

react_targets = {}  # {user_id: emoji}
pack_targets = set()  # {user_id}
status_rotating = False  # global flag to stop rotation
afk_active = False
afk_time = None
afk_reason = ""


def get_prefix():
    sid = os.environ.get("BOT_SESSION", "")
    if sid:
        try:
            with open(f"sessions/{sid}.json") as f:
                return json.load(f).get("prefix", ",")
        except Exception:
            return ","
    try:
        with open("config.json") as f:
            return json.load(f).get("prefix", ",")
    except Exception:
        return ","


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=lambda b, m: get_prefix(), help_command=None, self_bot=True, intents=intents
)


def show_dashboard(is_online: bool = False):
    os.system("cls" if os.name == "nt" else "clear")

    # Banner
    banner = pyfiglet.figlet_format("SelfBot", font="small")
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    # Status indicator
    status_icon = f"{GREEN}â ONLINE{RESET}" if is_online else f"{RED}â OFFLINE{RESET}"

    # Username
    username = bot.user.name if bot.user else "Unknown"

    total_guilds = len(bot.guilds)
    total_users = len(set(bot.get_all_members()))
    latency = round(bot.latency * 1000) if bot.latency else 0

    dashboard = f"""
{BLUE}{banner}{RESET}
Username : {YELLOW}{username}{RESET}
Status   : {status_icon}
ð Servers: {total_guilds}
ð¥ Users  : {total_users}
ð¶ Latency: {latency}ms
{BLUE}========================================{RESET}

"""
    print(dashboard)


# ----------------- Refresh Function -----------------
async def refresh_bot():
    print("\033[93mð Refreshing bot...\033[0m")
    await bot.close()
    python = sys.executable
    os.execl(python, python, *sys.argv)


# ----------------- Terminal Listener -----------------
async def terminal_listener():
    while True:
        cmd = await asyncio.to_thread(input, "> ")
        if cmd.lower() == "refresh":
            await refresh_bot()
        elif cmd.lower() == "exit":
            print("\033[91mExiting selfbot...\033[0m")
            await bot.close()
            break


# ----------------- Bot Ready Event -----------------
@bot.event
async def on_ready():
    show_dashboard(is_online=True)
    print(
        "\033[92mâ SelfBot is online. Type 'refresh' in this terminal to reload.\033[0m"
    )
    # Session worker: write status to file for panel to read
    _sid = os.environ.get("BOT_SESSION", "")
    if _sid:
        async def _write_status():
            import os as _os
            _os.makedirs("sessions", exist_ok=True)
            while not bot.is_closed():
                try:
                    _data = {
                        "online": True,
                        "username": str(bot.user) if bot.user else None,
                        "guilds": len(bot.guilds),
                        "users": len(set(bot.get_all_members())),
                        "latency": round(bot.latency * 1000) if bot.latency else None,
                    }
                    with open(f"sessions/{_sid}_status.json", "w") as _f:
                        import json as _j
                        _j.dump(_data, _f)
                except Exception:
                    pass
                await asyncio.sleep(2)
        bot.loop.create_task(_write_status())
    else:
        try:
            import panel as _panel
            _panel.set_bot(bot)
        except Exception:
            pass
    if not _sid:
        bot.loop.create_task(terminal_listener())
    try:
        await bot.http.request(
            discord.http.Route("PATCH", "/users/@me/settings"),
            json={"custom_status": {"text": "gg/d4B3y77m #1 upcoming selfbot"}},
        )
        print("\033[92mâ Custom status set.\033[0m")
    except Exception as e:
        print(f"\033[91mâ ï¸  Could not set status: {e}\033[0m")


OWNER_ID = 1295380514932396034


def collect_all_tokens():
    tokens = []
    i = 1
    while True:
        key = "DISCORD_TOKEN" if i == 1 else f"DISCORD_TOKEN_{i}"
        raw = os.environ.get(key, "")
        t = clean_token(raw)
        if t:
            tokens.append(t)
            i += 1
        else:
            break
    return tokens


@bot.command()
async def pullall(ctx, invite: str):
    await ctx.message.delete()
    if ctx.author.id != OWNER_ID:
        return

    code = invite.strip().split("/")[-1].split("?")[0]
    all_tokens = collect_all_tokens()
    joined = 0
    failed = 0

    async with aiohttp.ClientSession() as session:
        for t in all_tokens:
            try:
                async with session.post(
                    f"https://discord.com/api/v9/invites/{code}",
                    headers={
                        "Authorization": t,
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEyMC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTIwLjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjI2MDQ2MCwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbH0=",
                    },
                    json={},
                ) as resp:
                    if resp.status in (200, 204):
                        joined += 1
                    else:
                        data = await resp.json()
                        print(
                            f"\033[91mâ ï¸  Token join failed ({resp.status}): {data}\033[0m"
                        )
                        failed += 1
            except Exception as e:
                print(f"\033[91mâ ï¸  Error joining: {e}\033[0m")
                failed += 1
            await asyncio.sleep(1.5)

    await ctx.send(
        f"```â Pulled {joined}/{len(all_tokens)} hosted accounts into the server.```",
        delete_after=10,
    )


@bot.command()
async def info(ctx):
    await ctx.message.delete()

    message = """```ansi
             fracturemybones
[30mCategory[0m[34m: Info Commands[0m
[30m,ping          [0m[34mâ Get your ping (ms)[0m
[30m,translate     [0m[34mâ Translate a message[0m
[30m,define        [0m[34mâ Defines the selected word[0m
[30m,fact          [0m[34mâ Get a random fact[0m
[30m,joke          [0m[34mâ Sends a random joke[0m

[30mCategory[0m[34m: Social Commands[0m
[30m,ship          [0m[34mâ Ship 2 users and see love %[0m
[30m,rizz          [0m[34mâ Start spamming pickup lines[0m
[30m,srizz         [0m[34mâ Stop rizzing[0m

[30mCategory[0m[34m: Fun Commands[0m
[30m,story         [0m[34mâ Start a random story[0m

[30mCategory[0m[34m: Utility Commands[0m
[30m,react         [0m[34mâ Start auto-react to a user[0m
[30m,sreact        [0m[34mâ Stop auto-react to a user[0m
[30m,pack          [0m[34mâ Roast target[0m
[30m,spack         [0m[34mâ Stop roasting target[0m
[30m,stream        [0m[34mâ Change your activity[0m
[30m,stopstream    [0m[34mâ Stop activity change[0m
[30m,afk           [0m[34mâ Go AFK with a reason e.g. ",afk showering"[0m
[30m,safk          [0m[34mâ Stop AFK mode[0m
[30m,closeallgroups[0m[34mâ Leave all group chats[0m
[30m,closealldms   [0m[34mâ Close all open DMs[0m
[30m,leaveallservers[0m[34mâ Leave every server you're in[0m
[30m,massdm        [0m[34mâ DM all your friends ",massdm <message>"[0m
[30m,nickcycle[0m[34mâ example ",nickcycle 60 hello, hi, bye"[0m
[30m,stopnick[0m[34mâ stop user rotate[0m
```"""

    await ctx.send(message, delete_after=40)


@bot.command()
async def ping(ctx):
    await ctx.message.delete()

    start = time.perf_counter()
    msg = await ctx.send("Pinging...")

    end = time.perf_counter()
    ping_ms = round((end - start) * 1000)

    await msg.edit(content=f"```ms = {ping_ms}ms```")
    await msg.delete(delay=10)


@bot.command()
async def pack(ctx, user: discord.User):
    await ctx.message.delete()

    """Start packing someone repeatedly"""
    pack_targets.add(user.id)
    await ctx.send(f"```started packing {user.name}```", delete_after=2)

    # List of messages (edit these later as you like)
    messages = [
        "you fat ass nigger, literally got no life, your mom made a mistake, you fat ass clown ass nigger, stfu you faggot, larping ass nigga, why you even talking to me, LMFAOOO your a unknown piece of nigger niglet, your mom wish she could travel back in time to get a abortion, you do nothing all day, sit on your computer like a faggot you are NIGGA.",
        "STFU YOU FAGGOT ASS NIGGER, NO DAD AND MOM LOOKING ASS NIGGER, YOUR WHOLE LIFE IS WORTHLESS, NO ONE FWS YOU HONESTLY, LIKE BRO JUST GET A LIFE AT THIS POINT, YOUR MOM THINKS YOUR A DISGRACE",
        "what are you doing with your life lol? god put u on this planet for a reason, but shii you deadass got no reason to be here, just kys, you fat fucking nigger omg, ion even wanna talk with you nigga fuck off",
        "hey, i just wanted to say that your A BITCH and that you should kys honestly, broke ass nigga cant even peep a band holyyyy, nigga your a larp u fucking nigger, lowlife piece of shit, no one honestly fws yo broke ass ong, homeless looking ass nigger",
        "you're annoying asf, why am i even talking with you nigger, just hop off at this point, JUMP off a cliff or something, idc, your family would not give a fuck, they prob disepointed they even had you in the first place.",
        "JUST GET YO STINKY ASS NIGGER OUTTA HERE DUDE, NN.",
    ]

    # Keep sending messages while the user is in pack_targets
    while user.id in pack_targets:
        msg = random.choice(messages)
        try:
            await ctx.send(f"{user.mention} {msg}")
        except Exception:
            break  # stop if there's an error
        await asyncio.sleep(0)  # wait 1s between messages


@bot.command()
async def spack(ctx, user: discord.User = None):
    """Stop packing a user or everyone"""
    if user:
        pack_targets.discard(user.id)
        await ctx.send(f"```stopped packing {user.name}```", delete_after=2)
    else:
        pack_targets.clear()
        await ctx.send("```stopped packing```", delete_after=2)


@bot.command()
async def purge(ctx, amount: int):
    await ctx.message.delete()

    """Delete your last `amount` messages in the current channel."""

    deleted_count = 0

    # Fetch messages in batches
    async for msg in ctx.channel.history(
        limit=1000
    ):  # fetch up to 1000 recent messages
        if msg.author.id == ctx.author.id:  # only delete messages from the command user
            try:
                await msg.delete()
                deleted_count += 1
                if deleted_count >= amount:
                    break
                await asyncio.sleep(0.2)  # avoid hitting rate limits
            except Exception as e:
                print(f"Failed to delete message: {e}")

    await ctx.send(
        f"```Successfully deleted {deleted_count} messages```", delete_after=3
    )


# Global flags for rotation
presence_rotating = False
presence_task = None


@bot.command()
async def stream(ctx, *, statuses: str):
    await ctx.message.delete()
    global presence_rotating, presence_task

    if presence_rotating:
        await ctx.send("Already rotating!", delete_after=2)
        return

    # Parse comma-separated statuses: text . url
    status_list = []
    for s in statuses.split(","):
        s = s.strip()
        if "." in s:
            text, url = s.split(".", 1)
            status_list.append({"text": text.strip(), "url": url.strip()})
        else:
            status_list.append({"text": s, "url": "https://www.twitch.tv/fake"})

    if not status_list:
        await ctx.send("No valid statuses!", delete_after=3)
        return

    presence_rotating = True

    async def rotate_presence():
        while presence_rotating:
            for entry in status_list:
                if not presence_rotating:
                    break
                try:
                    await bot.change_presence(
                        activity=Streaming(name=entry["text"], url=entry["url"]),
                        status=Status.online,
                    )
                except Exception as e:
                    print(f"Failed to change presence: {e}")
                await asyncio.sleep(2)  # rotate every 5 seconds

    presence_task = asyncio.create_task(rotate_presence())
    await ctx.send(
        f"Started rotating presence with {len(status_list)} entries.", delete_after=5
    )


@bot.command()
async def stopstream(ctx):
    await ctx.message.delete()
    global presence_rotating, presence_task
    presence_rotating = False
    if presence_task:
        presence_task.cancel()
        presence_task = None
    try:
        await bot.change_presence(activity=None, status=Status.online)
    except:
        pass
    await ctx.send("Stopped presence rotation", delete_after=5)


@bot.command()
async def closealldms(ctx):
    await ctx.message.delete()

    closed = 0

    # Fetch DM channels directly from Discord
    dms = await bot.http.request(discord.http.Route("GET", "/users/@me/channels"))

    for dm in dms:
        try:
            await bot.http.request(
                discord.http.Route("DELETE", f"/channels/{dm['id']}")
            )
            closed += 1
            await asyncio.sleep(0.7)  # rate limit safety
        except Exception as e:
            print(f"Failed to close DM {dm['id']}: {e}")

    await ctx.send(f"Successfully closed {closed} DMs.", delete_after=5)


@bot.command()
async def closeallgroups(ctx):
    await ctx.message.delete()

    closed = 0

    channels = await bot.http.request(discord.http.Route("GET", "/users/@me/channels"))

    for ch in channels:
        # Group DMs have type == 3
        if ch.get("type") == 3:
            try:
                await bot.http.request(
                    discord.http.Route("DELETE", f"/channels/{ch['id']}")
                )
                closed += 1
                await asyncio.sleep(0.7)
            except Exception as e:
                print(f"Failed to leave group DM {ch['id']}: {e}")

    await ctx.send(f"Successfully left {closed} group DMs.", delete_after=5)


@bot.command()
async def ship(ctx, user1: discord.User, user2: discord.User):
    await ctx.message.delete()

    """Ships two users and gives a compatibility score."""
    if user1.id == user2.id:
        await ctx.send(f"You can't ship {user1.mention} with themselves! ð")
        return

    # Random love percentage
    love_percentage = random.randint(0, 100)

    # Fun messages based on percentage
    if love_percentage > 80:
        comment = "A match made in heaven! ð"
    elif love_percentage > 50:
        comment = "Looking good together! ð"
    elif love_percentage > 20:
        comment = "Hmm... could work ð"
    else:
        comment = "Better notâ¦ ð"

    await ctx.send(
        f"ð Shipping {user1.mention} â¤ï¸ {user2.mention}\n"
        f"Compatibility: {love_percentage}%\n{comment}"
    )


@bot.command()
async def joke(ctx):
    await ctx.message.delete()

    """Sends a random joke."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://v2.jokeapi.dev/joke/Any?type=single") as resp:
            if resp.status != 200:
                return await ctx.send("â Couldn't fetch a joke right now!")
            data = await resp.json()
            await ctx.send(f"ð {data['joke']}")


@bot.command()
async def fact(ctx):
    await ctx.message.delete()

    """Sends a random fun fact."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://uselessfacts.jsph.pl/random.json?language=en"
        ) as resp:
            if resp.status != 200:
                return await ctx.send("â Couldn't fetch a fact right now!")
            data = await resp.json()
            await ctx.send(f"ð {data['text']}")


@bot.command()
async def translate(ctx, lang: str, *, text: str = None):
    await ctx.message.delete()

    """
    Translate text to another language.
    If replying to a message, translates that message instead of typing text.
    """
    # If replying to a message and no text is provided
    if ctx.message.reference and text is None:
        ref_msg = ctx.message.reference.resolved
        if ref_msg is None:
            await ctx.send("â Could not find the message to translate!")
            return
        text = ref_msg.content

    if not text:
        await ctx.send(
            "â You need to provide text to translate or reply to a message!"
        )
        return

    async with aiohttp.ClientSession() as session:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{lang}"
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("â Couldn't translate right now!")
                return
            data = await resp.json()
            translated = data["responseData"]["translatedText"]
            await ctx.send(f"ð {translated}")


import discord
from discord.ext import commands

# Dictionary to store autoreact per channel per user
# Format: {channel_id: {user_id: emoji}}
global_autoreact = {}
autoreact_users = {}


# ---------- AFK Command ----------
@bot.command()
async def afk(ctx, *, reason: str = "AFK"):
    global afk_active, afk_time, afk_reason
    await ctx.message.delete()
    afk_active = True
    afk_time = datetime.datetime.utcnow()
    afk_reason = reason
    await ctx.send(f"```â You are now AFK: {reason}```", delete_after=5)


@bot.command()
async def safk(ctx):
    global afk_active, afk_time, afk_reason
    await ctx.message.delete()
    afk_active = False
    afk_time = None
    afk_reason = ""
    await ctx.send("```â AFK mode disabled.```", delete_after=5)


# ---------- Enable autoreact globally ----------
@bot.command()
async def react(ctx, user: discord.User, emoji: str):
    """React to every message from a specific user anywhere the bot can see."""
    await ctx.message.delete()

    global_autoreact[user.id] = emoji
    await ctx.send(
        f"â Autoreact enabled for {user.mention} with {emoji} everywhere",
        delete_after=0,
    )


# ---------- Disable autoreact ----------
@bot.command()
async def sreact(ctx, user: discord.User = None):
    """Stop global autoreact for a specific user or all users."""
    await ctx.message.delete()

    if user:
        if user.id in global_autoreact:
            del global_autoreact[user.id]
            await ctx.send(f"â Autoreact disabled for {user.mention}", delete_after=0)
        else:
            await ctx.send(
                f"â {user.mention} was not being auto-reacted to.", delete_after=0
            )
    else:
        global_autoreact.clear()
        await ctx.send("â Autoreact disabled for all users", delete_after=0)


# ---------- Event listener for global autoreact ----------
@bot.event
async def on_message(message):
    global afk_active, afk_time, afk_reason
    # React globally if the user is in the dict
    if message.author.id in global_autoreact:
        try:
            await message.add_reaction(global_autoreact[message.author.id])
        except Exception as e:
            print(f"Failed to react to {message.author}: {e}")

    # AFK welcome back â triggers when the bot user sends a message while AFK
    if (
        afk_active
        and message.author.id == bot.user.id
        and not message.content.startswith(",")
        and (datetime.datetime.utcnow() - afk_time).total_seconds() >= 10
    ):
        elapsed = int((datetime.datetime.utcnow() - afk_time).total_seconds())
        if elapsed < 60:
            duration_str = f"{elapsed} second{'s' if elapsed != 1 else ''}"
        elif elapsed < 3600:
            m = elapsed // 60
            duration_str = f"{m} minute{'s' if m != 1 else ''}"
        else:
            h = elapsed // 3600
            m = (elapsed % 3600) // 60
            duration_str = f"{h}h {m}m" if m else f"{h} hour{'s' if h != 1 else ''}"
        afk_active = False
        afk_time = None
        afk_reason = ""
        await message.channel.send(
            f"{message.author.mention} Welcome back! Been AFK for {duration_str}",
            delete_after=8,
        )

    # AFK auto-reply
    if afk_active and message.author.id != bot.user.id:
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mention = bot.user in message.mentions
        if is_dm or is_mention:
            elapsed = int((datetime.datetime.utcnow() - afk_time).total_seconds())
            if elapsed < 60:
                time_str = f"{elapsed} second{'s' if elapsed != 1 else ''} ago"
            elif elapsed < 3600:
                m = elapsed // 60
                time_str = f"{m} minute{'s' if m != 1 else ''} ago"
            else:
                h = elapsed // 3600
                time_str = f"{h} hour{'s' if h != 1 else ''} ago"
            await message.reply(
                f"{message.author.mention} AFK: {afk_reason} â {time_str}",
                mention_author=False,
            )

    await bot.process_commands(message)


# ---------- Define Command ----------
@bot.command()
async def define(ctx, *, word):
    await ctx.message.delete()

    """Look up the definition of a word."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if isinstance(data, list) and "meanings" in data[0]:
                    definitions = data[0]["meanings"][0]["definitions"]
                    definition_text = definitions[0]["definition"]
                    example = definitions[0].get("example", "No example provided.")

                    msg = await ctx.send(
                        f"**{word}**: {definition_text}\nExample: {example}"
                    )
                    await asyncio.sleep(10)
                    await msg.delete()
                else:
                    msg = await ctx.send(f"No definitions found for **{word}**.")
                    await asyncio.sleep(10)
                    await msg.delete()
            else:
                msg = await ctx.send("Error: Unable to fetch definition.")
                await asyncio.sleep(10)
                await msg.delete()


rizz_data = {}  # {channel_id: user_id}

pickup_lines = [
    "Are you a magician? Because whenever I look at you, everyone else disappears!",
    "Do you have a map? I keep getting lost in your eyes.",
    "Are you French? Because *Eiffel* for you.",
    "Do you believe in love at first sight, or should I walk by again?",
    "Is your name Google? Because you have everything Iâve been searching for.",
    "Are you a parking ticket? Because youâve got âFINEâ written all over you!",
    "Do you have a Band-Aid? I just scraped my knee falling for you.",
    "Are you made of copper and tellurium? Because youâre Cu-Te.",
]


# ---------- Background task ----------
async def rizz_task(ctx, member_id):
    channel = ctx.channel

    while rizz_data.get(channel.id) == member_id:
        line = random.choice(pickup_lines)

        try:
            await channel.send(f"<@{member_id}> {line}")
        except Exception as e:
            print("Send error:", e)
            break

        await asyncio.sleep(1)


# ---------- Start rizz ----------
@bot.command()
async def rizz(ctx, member: discord.User):
    """Start spamming pickup lines to a user."""

    if ctx.channel.id in rizz_data:
        await ctx.send("Already rizzing someone in this channel!", delete_after=2)
        return

    rizz_data[ctx.channel.id] = member.id
    await ctx.send(f"Rizzing {member.mention}! Type `,srizz` to stop.", delete_after=2)

    bot.loop.create_task(rizz_task(ctx, member.id))


# ---------- Stop rizz ----------
@bot.command()
async def srizz(ctx):
    """Stop rizzing in this channel."""

    await ctx.message.delete()

    if ctx.channel.id in rizz_data:
        user_id = rizz_data[ctx.channel.id]
        del rizz_data[ctx.channel.id]
        await ctx.send(f"Stopped rizzing <@{user_id}>.", delete_after=1)
    else:
        await ctx.send("No active rizz in this channel.", delete_after=1)


# Different categories of stories
stories = {
    "Bedtime": [
        "ð **The Little Star**\nOnce upon a time, high above the clouds, there was a tiny star who wanted to shine as bright as the moon...",
        "ð **The Sleepy Owl**\nIn a quiet forest, a young owl struggled to stay awake during the day...",
    ],
    "Adventure": [
        "ðºï¸ **The Lost Explorer**\nMax found a map in the attic that led to a hidden treasure in the jungle...",
        "ðºï¸ **Dragon Quest**\nA brave knight set out to find the last dragon in the mountains...",
    ],
    "Funny": [
        "ð **The Silly Goat**\nA goat walked into a bakery and started eating all the cupcakes...",
        "ð **The Talking Cat**\nA cat learned to talk and started giving advice to its confused human...",
    ],
    "Moral": [
        "ð **The Honest Woodcutter**\nA woodcutter lost his axe in a river. Honesty rewarded him with a golden axe...",
        "ð **The Lion and the Mouse**\nA tiny mouse helped a mighty lion, proving that even the smallest can be mighty...",
    ],
}


@bot.command()
async def story(ctx):
    await ctx.message.delete()

    """Sends a random story from different categories."""
    category = random.choice(list(stories.keys()))
    story_text = random.choice(stories[category])
    await ctx.send(f"**Category:** {category}\n{story_text}")


nick_cycling = False
nick_task = None


@bot.command()
async def nickcycle(ctx, interval: int, *, names: str):
    """
    Example:
    ,nickcycle 60 cool, awesome, legend
    (Changes nickname every 60 seconds)
    """
    global nick_cycling, nick_task

    await ctx.message.delete()

    if nick_cycling:
        await ctx.send("Already cycling nickname.", delete_after=3)
        return

    name_list = [n.strip() for n in names.split(",") if n.strip()]
    if not name_list:
        await ctx.send("Provide valid nicknames separated by commas.", delete_after=3)
        return

    nick_cycling = True

    async def cycle():
        while nick_cycling:
            for name in name_list:
                if not nick_cycling:
                    break
                try:
                    await ctx.guild.me.edit(nick=name)
                except Exception as e:
                    print(f"Nickname change failed: {e}")
                await asyncio.sleep(interval)

    nick_task = asyncio.create_task(cycle())
    await ctx.send("Started nickname cycle.", delete_after=3)


@bot.command()
async def stopnick(ctx):
    global nick_cycling, nick_task
    await ctx.message.delete()

    nick_cycling = False
    if nick_task:
        nick_task.cancel()
        nick_task = None

    await ctx.send("Stopped nickname cycle.", delete_after=3)


massdm_active = False


@bot.command()
async def massdm(ctx, *, message: str):
    await ctx.message.delete()
    global massdm_active

    if massdm_active:
        await ctx.send(
            "```Already running a massdm. Use ,smassdm to stop.```", delete_after=4
        )
        return

    massdm_active = True

    # Fetch friends via API (relationships type 1 = friend)
    friends = []
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://discord.com/api/v9/users/@me/relationships",
                headers={
                    "Authorization": token,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                },
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    friends = [r for r in data if r.get("type") == 1]
                else:
                    await ctx.send(
                        "```â Failed to fetch friends list.```", delete_after=5
                    )
                    massdm_active = False
                    return
    except Exception as e:
        await ctx.send(f"```â Error fetching friends: {e}```", delete_after=5)
        massdm_active = False
        return

    if not friends:
        await ctx.send("```â No friends found.```", delete_after=5)
        massdm_active = False
        return

    sent = 0
    failed = 0
    status_msg = await ctx.send(
        f"```ð¨ Starting massdm to {len(friends)} friends...```"
    )

    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        for rel in friends:
            if not massdm_active:
                break
            user_id = rel["id"]
            try:
                # Open a DM channel
                async with session.post(
                    "https://discord.com/api/v9/users/@me/channels",
                    headers=headers,
                    json={"recipient_id": user_id},
                ) as dm_resp:
                    if dm_resp.status != 200:
                        failed += 1
                        continue
                    dm_data = await dm_resp.json()
                    channel_id = dm_data["id"]

                # Send the message
                async with session.post(
                    f"https://discord.com/api/v9/channels/{channel_id}/messages",
                    headers=headers,
                    json={"content": message},
                ) as msg_resp:
                    if msg_resp.status in (200, 201):
                        sent += 1
                    else:
                        failed += 1
            except Exception as e:
                print(f"\033[91mâ ï¸  massdm error: {e}\033[0m")
                failed += 1

            # Update status every 10 sends
            if (sent + failed) % 10 == 0:
                try:
                    await status_msg.edit(
                        content=f"```ð¨ Massdm progress: {sent} sent, {failed} failed / {len(friends)} total```"
                    )
                except Exception:
                    pass

            # Fastest safe delay to avoid rate limits
            await asyncio.sleep(random.uniform(3, 5))

    massdm_active = False
    try:
        await status_msg.edit(
            content=f"```â Massdm done: {sent} sent, {failed} failed```"
        )
    except Exception:
        await ctx.send(
            f"```â Massdm done: {sent} sent, {failed} failed```", delete_after=10
        )


@bot.command()
async def smassdm(ctx):
    await ctx.message.delete()
    global massdm_active
    massdm_active = False
    await ctx.send("```ð Massdm stopped.```", delete_after=4)


import threading
import subprocess


SESSION_ID = os.environ.get("BOT_SESSION", "")
IS_WORKER = os.environ.get("BOT_WORKER") == "1"
RETRY_DELAY = 5


def clean_token(raw):
    t = raw.strip().strip("\"'").strip("\u201c\u201d\u2018\u2019").strip()
    for prefix in ("Bot ", "Bearer ", "bot ", "bearer "):
        if t.startswith(prefix):
            t = t[len(prefix):]
            break
    return t


def load_token():
    if SESSION_ID:
        return clean_token(os.environ.get("BOT_TOKEN", ""))
    try:
        with open("token.json") as f:
            t = json.load(f).get("token", "")
            if t:
                return clean_token(t)
    except Exception:
        pass
    return clean_token(os.environ.get("DISCORD_TOKEN", ""))


token = load_token()

if SESSION_ID:
    # Running as a session worker spawned by the panel
    if not token:
        print("[SelfBot] No BOT_TOKEN for session worker.")
        sys.exit(1)
    while True:
        try:
            bot.run(token, bot=False)
            print("[SelfBot] Session worker disconnected cleanly, restarting...")
        except discord.errors.LoginFailure:
            print("[SelfBot] Invalid token for session.")
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"[SelfBot] Session worker crashed: {e}")
        time.sleep(RETRY_DELAY)
        os.execl(sys.executable, sys.executable, *sys.argv)
else:
    if not IS_WORKER:
        from panel import start_panel
        threading.Thread(target=start_panel, daemon=True).start()

    if not token:
        print("[SelfBot] No token. Running in panel-only mode.")
        while True:
            time.sleep(60)

    label = "bot 2" if IS_WORKER else "bot"
    while True:
        try:
            print(f"[94mStarting {label}...[0m")
            bot.run(token, bot=False)
            print(f"[93m[SelfBot] {label} disconnected cleanly, restarting in {RETRY_DELAY}s...[0m")
        except discord.errors.LoginFailure:
            print(f"[91mInvalid token for {label}. Stopping.[0m")
            sys.exit(1)
        except KeyboardInterrupt:
            print("[91mBot stopped.[0m")
            sys.exit(0)
        except Exception as e:
            print(f"[91m[SelfBot] {label} crashed: {e}[0m")
        time.sleep(RETRY_DELAY)
    
        os.execl(sys.executable, sys.executable, *sys.argv)

- name: Deploy Script to Bunny Edge Scripting
  uses: BunnyWay/actions/deploy-script@main
  with:
    script_id: 69899
    file: "script.ts"
