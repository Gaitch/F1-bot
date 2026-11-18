import os
import discord
import data
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import tasks


load_dotenv()
token = os.getenv("DISCORD_TOKEN")

CHANNEL_ID = 1559537211391868961
REMINDER_INTERVAL_S = 60

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
client.tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    if not remind.is_running():
        remind.start()
        print('reminder started')



reminded = False
@tasks.loop(seconds=REMINDER_INTERVAL_S)
async def remind():
    global reminded
    channel = client.get_channel(CHANNEL_ID)

    session = data.get_upcoming_session()

    delta_s = session[2]

    if delta_s < 60*60 and not reminded:
        s = f"{session[0]} starts in less than an hour" 
        reminded = True
    if delta_s < REMINDER_INTERVAL_S +10:
        s = f"{session[0]} is starting now"
        reminded = False

    await channel.send(s)
    print('message sent')

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

