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
from PIL import Image, ImageDraw, ImageFont
from discord import Streaming, Status
import io
import textwrap
from discord import Status, Game
from discord.ext import commands
react_targets = {} # {user_id: emoji}
pack_targets = set()  # {user_id}
status_rotating = False  # global flag to stop rotation
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=",", intents=intents)
intents = discord.Intents.default()
intents.messages = True     # allows reading messages
intents.guilds = True       # allows receiving guild eventst



bot = commands.Bot(command_prefix=",", help_command=None, self_bot=True, intents=intents)







def show_dashboard(is_online: bool = False):
    os.system('cls' if os.name == 'nt' else 'clear')

    # Banner
    banner = pyfiglet.figlet_format("SelfBot", font="small")
    GREEN = "\033[92m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    # Status indicator
    status_icon = f"{GREEN}✅ ONLINE{RESET}" if is_online else f"{RED}❌ OFFLINE{RESET}"

    # Username
    username = bot.user.name if bot.user else "Unknown"

    total_guilds = len(bot.guilds)
    total_users = len(set(bot.get_all_members()))
    latency = round(bot.latency * 1000) if bot.latency else 0

    dashboard = f"""
{BLUE}{banner}{RESET}
Username : {YELLOW}{username}{RESET}
Status   : {status_icon}
🌐 Servers: {total_guilds}
👥 Users  : {total_users}
📶 Latency: {latency}ms
{BLUE}========================================{RESET}

"""
    print(dashboard)


# ----------------- Refresh Function -----------------
async def refresh_bot():
    print("\033[93m🔄 Refreshing bot...\033[0m")
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
    print("\033[92m✅ SelfBot is online. Type 'refresh' in this terminal to reload.\033[0m")
    bot.loop.create_task(terminal_listener())



@bot.command()
async def info(ctx):
    await ctx.message.delete()

    message = """```ansi
             fracturemybones
[30mCategory[0m[34m: Info Commands[0m
[30m,ping          [0m[34m→ Get your ping (ms)[0m
[30m,translate     [0m[34m→ Translate a message[0m
[30m,define        [0m[34m→ Defines the selected word[0m
[30m,fact          [0m[34m→ Get a random fact[0m
[30m,joke          [0m[34m→ Sends a random joke[0m

[30mCategory[0m[34m: Social Commands[0m
[30m,ship          [0m[34m→ Ship 2 users and see love %[0m
[30m,rizz          [0m[34m→ Start spamming pickup lines[0m
[30m,srizz         [0m[34m→ Stop rizzing[0m

[30mCategory[0m[34m: Fun Commands[0m
[30m,story         [0m[34m→ Start a random story[0m

[30mCategory[0m[34m: Utility Commands[0m
[30m,react         [0m[34m→ Start auto-react to a user[0m
[30m,sreact        [0m[34m→ Stop auto-react to a user[0m
[30m,pack          [0m[34m→ Roast target[0m
[30m,spack         [0m[34m→ Stop roasting target[0m
[30m,stream        [0m[34m→ Change your activity[0m
[30m,stopstream    [0m[34m→ Stop activity change[0m
[30m,afk           [0m[34m→ Go AFK with a reason (SOON)[0m
[30m,closeallgroups[0m[34m→ Leave all group chats[0m
[30m,closealldms   [0m[34m→ Close all open DMs[0m
[30m,leaveallservers[0m[34m→ Leave every server you're in[0m
[30m,massdm[0m[34m→ (SOON).[0m
[30m,nickcycle[0m[34m→ example ",nickcycle 60 hello, hi, bye"[0m
[30m,stopnick[0m[34m→ stop user rotate[0m
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
        "JUST GET YO STINKY ASS NIGGER OUTTA HERE DUDE, NN."
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
    async for msg in ctx.channel.history(limit=1000):  # fetch up to 1000 recent messages
        if msg.author.id == ctx.author.id:  # only delete messages from the command user
            try:
                await msg.delete()
                deleted_count += 1
                if deleted_count >= amount:
                    break
                await asyncio.sleep(0.2)  # avoid hitting rate limits
            except Exception as e:
                print(f"Failed to delete message: {e}")
    
    await ctx.send(f"```Successfully deleted {deleted_count} messages```", delete_after=3)



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
                        status=Status.online
                    )
                except Exception as e:
                    print(f"Failed to change presence: {e}")
                await asyncio.sleep(2)  # rotate every 5 seconds

    presence_task = asyncio.create_task(rotate_presence())
    await ctx.send(f"Started rotating presence with {len(status_list)} entries.", delete_after=5)


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
    dms = await bot.http.request(
        discord.http.Route("GET", "/users/@me/channels")
    )

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

    channels = await bot.http.request(
        discord.http.Route("GET", "/users/@me/channels")
    )

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
        await ctx.send(f"You can't ship {user1.mention} with themselves! 💔")
        return

    # Random love percentage
    love_percentage = random.randint(0, 100)

    # Fun messages based on percentage
    if love_percentage > 80:
        comment = "A match made in heaven! 💖"
    elif love_percentage > 50:
        comment = "Looking good together! 💕"
    elif love_percentage > 20:
        comment = "Hmm... could work 😅"
    else:
        comment = "Better not… 💔"

    await ctx.send(
        f"💞 Shipping {user1.mention} ❤️ {user2.mention}\n"
        f"Compatibility: {love_percentage}%\n{comment}"
    )


@bot.command()
async def joke(ctx):
    await ctx.message.delete()


     
    """Sends a random joke."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://v2.jokeapi.dev/joke/Any?type=single") as resp:
            if resp.status != 200:
                return await ctx.send("❌ Couldn't fetch a joke right now!")
            data = await resp.json()
            await ctx.send(f"😂 {data['joke']}")

@bot.command()
async def fact(ctx):
    await ctx.message.delete()

    
    """Sends a random fun fact."""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as resp:
            if resp.status != 200:
                return await ctx.send("❌ Couldn't fetch a fact right now!")
            data = await resp.json()
            await ctx.send(f"📚 {data['text']}")



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
            await ctx.send("❌ Could not find the message to translate!")
            return
        text = ref_msg.content

    if not text:
        await ctx.send("❌ You need to provide text to translate or reply to a message!")
        return

    async with aiohttp.ClientSession() as session:
        url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{lang}"
        async with session.get(url) as resp:
            if resp.status != 200:
                await ctx.send("❌ Couldn't translate right now!")
                return
            data = await resp.json()
            translated = data['responseData']['translatedText']
            await ctx.send(f"🌐 {translated}")



import discord
from discord.ext import commands

# Dictionary to store autoreact per channel per user
# Format: {channel_id: {user_id: emoji}}
global_autoreact = {}
autoreact_users = {}

# ---------- Enable autoreact globally ----------
@bot.command()
async def react(ctx, user: discord.User, emoji: str):
    """React to every message from a specific user anywhere the bot can see."""
    await ctx.message.delete()
    
    global_autoreact[user.id] = emoji
    await ctx.send(f"✅ Autoreact enabled for {user.mention} with {emoji} everywhere", delete_after=0)

# ---------- Disable autoreact ----------
@bot.command()
async def sreact(ctx, user: discord.User = None):
    """Stop global autoreact for a specific user or all users."""
    await ctx.message.delete()
    
    if user:
        if user.id in global_autoreact:
            del global_autoreact[user.id]
            await ctx.send(f"✅ Autoreact disabled for {user.mention}", delete_after=0)
        else:
            await ctx.send(f"❌ {user.mention} was not being auto-reacted to.", delete_after=0)
    else:
        global_autoreact.clear()
        await ctx.send("✅ Autoreact disabled for all users", delete_after=0)

# ---------- Event listener for global autoreact ----------
@bot.event
async def on_message(message):
    # React globally if the user is in the dict
    if message.author.id in global_autoreact:
        try:
            await message.add_reaction(global_autoreact[message.author.id])
        except Exception as e:
            print(f"Failed to react to {message.author}: {e}")
    
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
                    
                    msg = await ctx.send(f"**{word}**: {definition_text}\nExample: {example}")
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
    "Is your name Google? Because you have everything I’ve been searching for.",
    "Are you a parking ticket? Because you’ve got ‘FINE’ written all over you!",
    "Do you have a Band-Aid? I just scraped my knee falling for you.",
    "Are you made of copper and tellurium? Because you’re Cu-Te."
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
        "🌙 **The Little Star**\nOnce upon a time, high above the clouds, there was a tiny star who wanted to shine as bright as the moon...",
        "🌙 **The Sleepy Owl**\nIn a quiet forest, a young owl struggled to stay awake during the day..."
    ],
    "Adventure": [
        "🗺️ **The Lost Explorer**\nMax found a map in the attic that led to a hidden treasure in the jungle...",
        "🗺️ **Dragon Quest**\nA brave knight set out to find the last dragon in the mountains..."
    ],
    "Funny": [
        "😂 **The Silly Goat**\nA goat walked into a bakery and started eating all the cupcakes...",
        "😂 **The Talking Cat**\nA cat learned to talk and started giving advice to its confused human..."
    ],
    "Moral": [
        "📖 **The Honest Woodcutter**\nA woodcutter lost his axe in a river. Honesty rewarded him with a golden axe...",
        "📖 **The Lion and the Mouse**\nA tiny mouse helped a mighty lion, proving that even the smallest can be mighty..."
    ]
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














bot.run("MTI5NTM4MDUxNDkzMjM5NjAzNA.G2b9wi.f8uIAMKxc6TQ_uMxSLQdjno8uiWiVEqt1SqU74", bot=False)
