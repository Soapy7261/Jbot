# This example requires the 'message_content' intent.

import discord
from data_handler import *
import time
from discord.ext import tasks
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

def is_less_than_24h_away(target_date):
    current_date = datetime.now()
    time_delta = target_date - current_date
    return time_delta < timedelta(days=1)

@tasks.loop(seconds=1)
async def update_notifications():
    users = user_dict()
    jinf  = get_jaminfo()
    next_jam_time = datetime.strptime(jinf["start_date"], '%m-%d-%Y').timestamp()
    for user in users["users"]:
        uinf = users["users"][user]
        if is_less_than_24h_away(datetime.fromtimestamp(next_jam_time)) and time.time() - uinf["last_notification_time"] >= 5:
            add_or_config_user(user, {
                "num_jams": uinf["num_jams"],
                "date_joined": uinf["date_joined"],
                "last_notification_time": time.time(),
            })
            print(user)
            print(await send_dm(user, f"{jinf['name']} starts in 24 hours!"))

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    update_notifications.start()

async def reply(message, text):
    await message.reply(text)

async def add_role(user_id, role_name, guild):
    member = await guild.fetch_member(user_id)
    role = discord.utils.get(guild.roles, name=role_name)
    if role is not None:
        await member.add_roles(role)
        return f"{member.mention} has been added to the {role_name} role."
    else:
        return f"{role_name} role not found."
    
async def remove_role(user_id, role_name, guild):
    member = await guild.fetch_member(user_id)
    role = discord.utils.get(guild.roles, name=role_name)
    if role is not None:
        await member.remove_roles(role)
        return f"{member.mention} has been removed from the {role_name} role."
    else:
        return f"{role_name} role not found."


async def send_dm(username: str, message: str):
    print(username.strip('@')[:-5], username.strip('@')[-4:])
    print(client.users)
    user = discord.utils.get(client.users, name=username.strip('<@!>')[:-5], discriminator=username.strip('<@!>')[-4:])
    if user is None:
        return 'User not found.'
    try:
        await user.send(message)
        return f"Message sent to {user.name}#{user.discriminator}"
    except discord.Forbidden:
        return "I don't have permission to DM that user."

async def handle_command(command, arguments, message):
    if (command == "join"):
        if str(message.author) in get_users():
            await reply(message, "You are already signed up for notifications about game jams!")
        else:
            add_or_config_user(str(message.author), {
                "num_jams": 0,
                "date_joined": time.strftime("%m-%d-%Y")
            })
            print(await add_role(message.author.id, "Homies Scratch Jam participant", client.guilds[0]))
            await reply(message, "You are now signed up for notifications about game jams!")
    elif (command == "jaminfo"):
        jaminfo = get_jaminfo()
        if jaminfo["active"]:
            name, embed = get_jam_embed()
            await message.channel.send(f"***{name}***", embed=embed)
        else:
            await message.channel.send(embed=discord.Embed(title="No active jams", description=f"Sorry, the scratch jam isn't happening right now. {'You are signed up for notifications and will receive a DM when a jam is happening.' if str(message.author) in get_users() else 'You are not signed up for notifications. Run `j?join` to sign up.'}", color=0xFF0000))
    elif (command == "leave"):
        if str(message.author) in get_users():
            remove_user(str(message.author))
            print(await remove_role(message.author.id, "Homies Scratch Jam participant", client.guilds[0]))
            await reply(message, "You have been removed from the notification list. :sob:")
        else:
            await reply(message, "You're not signed up for notifications.")
    
    else:
        await reply(message, f"Command not found: `{command}`")
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    text = message.content.lower()

    if text.startswith('j?'):
        command = text.split()[0][2:]
        argstr = text[text.find(' ')+1:]
        args = [""]
        parsing_string = False
        for chr in argstr:
            if chr.isspace() and not parsing_string:
                if args[-1] != "":
                    args.append("")
            elif chr == '"':
                parsing_string = not parsing_string
            else:
                args[-1] += chr
        
        await handle_command(command, args, message)

client.run('MTEwNDQ5MjQ2MjA1NzIwOTg5Nw.GrX7Rz.pCbuRFRcrGRflnz2Gp-Kk1DaAvX8uDs7xKFrvc')