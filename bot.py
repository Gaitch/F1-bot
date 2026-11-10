import os
import discord
import data
from dotenv import load_dotenv
from discord import app_commands


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

channel_id = 1559537211391868961

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
client.tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('f1-standings'):
        standings = data.get_driver_standings()
        await message.channel.send(standings)

    if message.content.startswith('f1-nextevent'):
        event = data.get_next_event()
        await message.channel.send(event)

    if message.content.startswith('f1-results'):
        print('getting race results...\n')
        events = data.get_last_race_results()
        await message.channel.send(events)


client.run(token)

