#!/usr/bin/env python3
# Work with Python 3.7+

from discord.ext import tasks
import discord
import logging
import json
import asyncio


logging.basicConfig(format="%(asctime)s | %(levelname)s:%(name)s:%(message)s",
                    filename='veniamin.log', level=logging.INFO)
logging.info('----- Started -----')

with open("auth.json") as data_file:
    auth = json.load(data_file)
with open("links.json") as data_file:
    data = json.load(data_file)


TOKEN = auth["token"]
BOT_PREFIX = "!"


intents = discord.Intents(messages=True, guilds=True)
intents.reactions = True
intents.members = True
intents.emojis = True
intents.presences = True
intents.typing = False

client = discord.Client(intents=intents)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


@tasks.loop(minutes=15)
# task runs every 15 minutes
async def update_members():
    await client.wait_until_ready() and logging.info(f'Client is ready for members update!')
    logging.info(f'Calling Members update')
    guild = client.get_guild(667002471440449539)
    total_channel = client.get_channel(888706799484694570)
    online_channel = client.get_channel(888707284832747541)
    while not client.is_closed():
        widget = await guild.widget()
        online_members = len(widget.members)
        total_members = guild.member_count
        await total_channel.edit(name=f"Total Members: {total_members}") and logging.info(f'Changed Total Members: {total_members}')
        await online_channel.edit(name=f"Online Members: {online_members}") and logging.info(f'Changed Online Members: {online_members}')


@client.event
async def on_message(msg):
    # We do not want the bot to respond to Bots or Webhooks
    if msg.author.bot:
        return
    # We want the bot to not answer to messages that have no content
    # (example only attachment messages)
    # Bot checks BOT_PREFIX
    if not msg.content or msg.content[0] != BOT_PREFIX:
        return
    # Bot ignore all system messages
    if msg.type is not discord.MessageType.default:
        return

    args = msg.content[1:].split()
    cmd = args[0].lower()

    # Bot runs in #🤖-bot-commands channel and private channels for everyone
    # Bot runs in all channels for specific roles
    if not (
        isinstance(msg.channel, discord.DMChannel)
        or msg.channel.name == "bot-commands"
        or "core-team" in [role.name for role in msg.author.roles]
        or "moderator" in [role.name for role in msg.author.roles]
        or "team" in [role.name for role in msg.author.roles]
    ):
        message = f"{data['default']}"
        await msg.channel.send(message)
        return

    # -------- <help> --------
    elif cmd == "help":
        message = "\n".join(data["help"])
    # -------- <about> --------
    elif cmd == "about":
        message = "\n".join(data["about"])
    # -------- <ban(Amitabha only)> --------
    elif (
        cmd == "ban"
        and isinstance(msg.channel, discord.TextChannel)
        and (msg.author.id == 359782573066551320 or msg.author.id == 401412050678710273)

    ):
        if len(args) < 2:
            message = (
                f"Input a substring of users to ban, like `!ban CryPh` will ban all users containing"
                + f" `CryPh` in their names (_fuction is case-sensitive_)."
            )
            await msg.channel.send(message)
            return
        cmd1 = args[1]
        member = discord.utils.find(
            lambda m: cmd1 in m.name, msg.channel.guild.members)
        if member is None:
            count = 0
        else:
            count = 1
        while not (member is None):
            await msg.channel.guild.ban(member)
            member = discord.utils.find(
                lambda m: cmd1 in m.name, msg.channel.guild.members)
            if not (member is None):
                count += 1
        message = f"Banned {count} members! Nice!"
    # -------- <del(Amitabha only)> --------
    elif (
        cmd == "del"
        and isinstance(msg.channel, discord.TextChannel)
        and (msg.author.id == 359782573066551320 or msg.author.id == 401412050678710273)
    ):
        if len(args) < 2:
            message = "Enter the number of messages to delete"
            await msg.channel.send(message)
            return
        cmd1 = args[1]
        deleted = await msg.channel.purge(limit=int(cmd1))
        message = f"Deleted {len(deleted)} message(s)"

    else:
        message = f"{data['unknown']}"

    await msg.channel.send(message)


@client.event
async def on_raw_reaction_add(payload):
    guild = client.get_guild(667002471440449539)
    role = guild.get_role(888689373938339880)
    mbr = guild.get_member(payload.user_id)

    if (payload.message_id == 888715676775239690 and payload.emoji.name == "apocryph"):
        await mbr.add_roles(role)


@client.event
async def on_raw_reaction_remove(payload):
    guild = client.get_guild(667002471440449539)
    role = guild.get_role(888689373938339880)
    mbr = guild.get_member(payload.user_id)

    if (payload.message_id == 888715676775239690 and payload.emoji.name == "apocryph"):
        await mbr.remove_roles(role)


@client.event
async def on_member_join(mbr):
    for ban_word in data["banned_words"]:
        if mbr.guild.get_member(mbr.id) is not None and ban_word in mbr.name:
            await mbr.ban()
            logging.warning(f'Banned {mbr.name} with id: {mbr.id}')
            return


@client.event
async def on_member_update(before, after):
    # Bot ignore all members that have MEMBER_ID in ignored_ids list
    if after.id in data["ignored_ids"]:
        return
    for ban_word in data["banned_words"]:
        if after.guild.get_member(after.id) is not None and ban_word in after.name:
            await after.ban()
            logging.warning(f'Banned {after.name} with id: {after.id}')
            return


@client.event
async def on_ready():
    print(f"Logged in as: {client.user.name} {{{client.user.id}}}")

update_members.start()
client.run(TOKEN)
logging.info('----- Finished -----')
