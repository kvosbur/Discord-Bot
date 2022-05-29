import os
import requests
import time
import datetime

import discord
from dotenv import load_dotenv

test_affix_icons = {
    "Tyrannical": ":grinning:",
    "Fortified": ":smiley:",
    "Bolstering": ":smile:",
    "Bursting": ":sweat_smile:",
    "Sanguine": ":joy:",
    "Spiteful": ":relaxed:",
    "Inspiring": ":blush:",
    "Raging": ":innocent:",
    "Explosive": ":wink:",
    "Grievous": ":relieved:",
    "Necrotic": ":heart_eyes:",
    "Volcanic": ":kissing:",
    "Quaking": ":yum:",
    "Storming": ":stuck_out_tongue:",
    "Encrypted": ":disappointed:"
}

actual_affix_icons = {
    "Tyrannical": ":MTyrannical:",
    "Fortified": ":MFortified:",
    "Bolstering": ":MBolstering:",
    "Bursting": ":MBursting:",
    "Sanguine": ":MSanguine:",
    "Spiteful": ":MSpiteful:",
    "Inspiring": ":MInspiring",
    "Raging": ":MRaging:",
    "Explosive": ":MExplosive:",
    "Grievous": ":MGrevious:",
    "Necrotic": ":MNecrotic:",
    "Volcanic": ":MVolcanic",
    "Quaking": ":MQuaking:",
    "Storming": ":MStorming:",
    "Encrypted": ":MEncrypted:"
}

affix_icons = actual_affix_icons

message_extras = [
    { "extra_text": "+2" },
    { "extra_text": "+4" },
    { "extra_text": "+7" },
    { "extra_text": "+10" }
]

load_dotenv()

token = os.getenv("DISCORD_TOKEN")
server = os.getenv("TARGET_SERVER_NAME")
target_channel = os.getenv("TARGET_CHANNEL_NAME")
message_to_send = ""

client = discord.Client()

def start_client():
    global message_to_send
    print(time.time())
    client.run(token)


def get_affix_data():
    r = requests.get("https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en")
    affix_details = r.json()["affix_details"]
    messages = []
    for index, affix in enumerate(affix_details):
        icon = affix_icons.get(affix['name']) or ":grimacing:"
        messages.append(f"{icon} {affix['name']} ({message_extras[index]['extra_text']})")
    return messages

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def generate_message():
    today = datetime.date.today()
    end = next_weekday(today, 0)
    print(today)
    date_message = f"**For the week of:** {today.strftime('%m/%d/%y')} - {end.strftime('%m/%d/%y')}"
    messages = get_affix_data()
    return "\n".join([date_message] + messages)


def get_channel(channels, target_name):
    for channel in channels:
        if channel.name == target_name:
            return channel
    return None

async def remove_previous_pin_notify(channel):
    if channel.name == target_channel:
        try:
            temp = await channel.fetch_message(channel.last_message_id)
            if temp.author.bot and temp.author.id == client.user.id and temp.type.value == 6:
                print("delete message that pin was added")
                await temp.delete()
        except Exception as e:
            print("Had issue removing pin", e)


@client.event
async def on_guild_channel_pins_update(channel, last_pin):
    await remove_previous_pin_notify(channel)

@client.event
async def on_ready():
    global target_channel
    print("client readied")
    for guild in client.guilds:
        if guild.name == server:
            break

    print(f"guild: {guild}")
    channel = get_channel(guild.channels, target_channel)

    # remove existing pins
    pinned_messages = await channel.pins()
    for m in pinned_messages:
        if m.author.id == client.user.id:
            print(f"unpinning message: {m}")
            await m.unpin()

    # pin new message
    message_to_send = generate_message()
    print(message_to_send)
    message = await channel.send(content=message_to_send)
    print(f"sent message: {message}")
    await message.pin()
    print("message pinned")
    await remove_previous_pin_notify(channel)
    await client.close()

start_client()
