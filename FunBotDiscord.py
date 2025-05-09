import discord
from urllib.parse import quote_plus
import json
import LeagueOfLegends
from hell_let_loose import HLL_View
from discord.ext import commands, tasks
import asyncio
import sqlite3
from datetime import datetime, timedelta
import re
import cv2
import numpy as np
import os
import aiohttp

intents = discord.Intents.all()
f = open("botToken.txt", "r")
TOKEN = f.read()
bot = commands.Bot(command_prefix="/", intents=intents)
VALID_CLIP_EXTENSIONS = ['.mp4', '.webm', '.mov']
CLIP_CHANNEL_ID = 1326956425762570240
AUTHORIZED_USER_ID = 999736048596816014
MY_USER_ID = 262347377476632577
LEAGUE_USER_ID1 = 299335372859768852
LEAGUE_USER_ID2 = 368913296771776512

def setup_database():
    # Connect to SQLite database
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()

    # Create table if it does not exist
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY, message TEXT, due_date DATETIME, channel_id INTEGER)''')
    conn.commit()
    return conn, c

conn, c = setup_database()

class Google(discord.ui.View):
    def __init__(self, query: str):
        super().__init__()
        # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus(query)
        url = f'https://www.google.com/search?q={query}'

        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(discord.ui.Button(label='Click Here', url=url))

@bot.event
async def on_ready():
    print("Ready to go")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)
    check_due_reminders.start()  # Start the reminders background task

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.hybrid_command(name="ping")
async def hello(ctx: commands.Context):
    """Pings the Bot"""
    await ctx.send(f'pong') 
    
@bot.hybrid_command(name="google")
async def google(ctx: commands.Context, *, query: str):
    """Returns a google link for a query"""
    await ctx.send(f'Google Result for: `{query}`', view=Google(query))

@bot.hybrid_command(name="hll")
async def survey(ctx):
    view = HLL_View()
    await ctx.send(view=view)
    await view.wait()
    await ctx.send(view.answer1)

@bot.command(name="reminder")
async def reminder(ctx, *, time_and_message: str):
    try:
        message_pattern = r'"([^"]+)"'  # Extract message within quotes
        message_match = re.search(message_pattern, time_and_message)
        if not message_match:
            await ctx.send('Invalid format. Use `!reminder <time> "<message>"` with time units being day(s), hour(s), or minute(s).')
            return

        message = message_match.group(1)
        time_str = time_and_message.replace(f'"{message}"', '').strip()
        due_date = calculate_due_date(time_str)

        if due_date is None:
            await ctx.send('Invalid time format. Use units like day(s), hour(s), or minute(s).')
            return

        c.execute("INSERT INTO reminders (message, due_date, channel_id) VALUES (?, ?, ?)",
                  (message, due_date, ctx.channel.id))
        conn.commit()
        await ctx.send(f'Scheduled a reminder: "{message}" at {due_date}.')
    except Exception as e:
        await ctx.send(f'Error: {str(e)}')

def calculate_due_date(time_string):
    time_units = re.findall(r'(\d+)\s*(day|days|hour|hours|minute|minutes)', time_string)
    if not time_units:
        return None

    due_date = datetime.now()

    for amount, unit in time_units:
        amount = int(amount)
        if unit in ['day', 'days']:
            due_date += timedelta(days=amount)
        elif unit in ['hour', 'hours']:
            due_date += timedelta(hours=amount)
        elif unit in ['minute', 'minutes']:
            due_date += timedelta(minutes=amount)

    return due_date

@tasks.loop(minutes=1)
async def check_due_reminders():
    now = datetime.now()
    c.execute("SELECT * FROM reminders WHERE due_date <= ?", (now,))
    due_reminders = c.fetchall()
    for reminder in due_reminders:
        _, message, due_date, channel_id = reminder
        channel = bot.get_channel(channel_id)
        await send_reminder(channel, message)
        c.execute("DELETE FROM reminders WHERE id = ?", (reminder[0],))
    conn.commit()

async def send_reminder(channel, message):
    await channel.send(f'Reminder: {message}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello, {message.author.display_name}!')

    if message.content.lower() == 'hey jared':
        await message.channel.send('that guy sucks dont talk to him!')

    # Check if the message contains attachments
    if message.attachments and message.channelID != CLIP_CHANNEL_ID:
        for attachment in message.attachments:
            # Check if the attachment is a valid clip (based on file extension)
            if any(attachment.filename.endswith(ext) for ext in VALID_CLIP_EXTENSIONS):
                # Forward the message content and original author info
                embed = discord.Embed(
                description=f"**{message.author.name}** shared a clip!\n{message.content}",
                color=discord.Color.blue())
        await clip_channel.send(embed=embed, file=await attachment.to_file())

    if message.attachments and message.author.id in [AUTHORIZED_USER_ID]:
        for attachment in message.attachments:
            # Check if the attachment is a valid clip (based on file extension)
            if any(attachment.filename.lower().endswith(ext) for ext in
                   ['png']):  # Validate image format
                image = await download_image(attachment.url)
                if image is not None:
                    print('image at ' + attachment.url)
                    answer = LeagueOfLegends.find_best_match(image, "AllLeagueChampions")
                    hp_and_atk = get_value_from_json(answer)
                    answer = answer.replace('_', ' ')
                    answer += "\nhp = %s\natk = %s" % (hp_and_atk["hp"],hp_and_atk["atk"])
                    user = await bot.fetch_user(MY_USER_ID)
                    await user.send(answer)
                    user = await bot.fetch_user(LEAGUE_USER_ID1)
                    await user.send(answer)
                    user = await bot.fetch_user(LEAGUE_USER_ID2)
                    await user.send(answer)
                else:
                    await message.channel.send("Failed to process the image.")
    await bot.process_commands(message)

async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                image_bytes = await resp.read()
                image_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
                return cv2.imdecode(image_array, cv2.IMREAD_COLOR)  # Decode image for OpenCV
    return None

def get_value_from_json(name: str):
    """
    Retrieves the value associated with a given name (key) from a JSON file.

    :param file_path: Path to the JSON file.
    :param name: The key whose value needs to be retrieved.
    :return: The value associated with the key, or None if key is not found.
    """
    try:
        with open("league_values.json", 'r', encoding='utf-8') as file:
            data = json.load(file)

        return data.get(name, None)  # Returns None if key is not found
    except FileNotFoundError:
        print(f"Error: The file was not found.")
    except json.JSONDecodeError:
        print("Error: The file is not a valid JSON.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None
    # Don't forget to process commands if the bot has any

bot.run(TOKEN)
