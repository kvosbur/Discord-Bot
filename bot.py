import os
import requests
import time

import discord
from dotenv import load_dotenv

test_affix_icons = {
    "Tyrannical": ":grinning:",
    "Fortified": ":smiley:",
    "Bolserting": ":smile:",
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
    "Tyrannical": "",
    "Fortified": "",
    "Bolserting": "",
    "Bursting": "",
    "Sanguine": "",
    "Spiteful": "",
    "Inspiring": "",
    "Raging": "",
    "Explosive": "",
    "Grievous": "",
    "Necrotic": "",
    "Volcanic": "",
    "Quaking": "",
    "Storming": "",
    "Encrypted": ""
}

affix_icons = test_affix_icons

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
    message_to_send = get_affix_data()
    print("data retrieved")
    print(message_to_send)
    client.run(token)


def get_affix_data():
    r = requests.get("https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en")
    affix_details = r.json()["affix_details"]
    messages = []
    for index, affix in enumerate(affix_details):
        icon = affix_icons.get(affix['name']) or ":grimacing:"
        messages.append(f"{icon} {affix['name']} {message_extras[index]['extra_text']} ({affix['wowhead_url']})")
    return '\n'.join(messages)


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
    message = await channel.send(content=message_to_send)
    print(f"sent message: {message}")
    await message.pin()
    print("message pinned")
    await remove_previous_pin_notify(channel)
    await client.close()

start_client()
