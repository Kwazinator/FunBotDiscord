import discord
from urllib.parse import quote_plus
from discord.ext import commands, tasks
import asyncio
import sqlite3
from datetime import datetime, timedelta
import re

intents = discord.Intents.all()
f = open("botToken.txt", "r")
TOKEN = f.read()
bot = commands.Bot(command_prefix="/", intents=intents)

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

@bot.hybrid_command(name="ping")
async def hello(ctx: commands.Context):
    await ctx.send('pong') 
    
@bot.command()
async def google(ctx: commands.Context, *, query: str):
    """Returns a google link for a query"""
    await ctx.send(f'Google Result for: `{query}`', view=Google(query))

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

    if '??' in message.content:
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')

    await bot.process_commands(message)

bot.run(TOKEN)
