import discord
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

@bot.hybrid_command(name="reminder", description="Set a reminder")
@discord.app_commands.describe(time="Time for the reminder in the format '1 day', '2 hours', etc.", message="The message for the reminder")
async def reminder(ctx: commands.Context, time: str, message: str):
    try:
        due_date = calculate_due_date(time)

        if due_date is None:
            await ctx.send(f'Error: No time associated with reminder, use day(s), hour(s), or minute(s), followed by a number. Example: /reminder time:1 day message:Hello World')
            return

        c.execute("INSERT INTO reminders (message, due_date, channel_id) VALUES (?, ?, ?)",
                  (message, due_date, ctx.channel.id))
        conn.commit()
        await ctx.send(f'Scheduled a reminder: "{message}" for {due_date}.')
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
