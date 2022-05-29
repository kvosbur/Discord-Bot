import os
import requests
import time

import discord
from dotenv import load_dotenv

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
    return '\n'.join([f"{affix['name']} ({affix['wowhead_url']})" for affix in affix_details])


def get_channel(channels, target_name):
    for channel in channels:
        if channel.name == target_name:
            return channel
    return None


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
    await client.close()
    print("client closed")

start_client()
