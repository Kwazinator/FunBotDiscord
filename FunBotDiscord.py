import discord

intents = discord.Intents.all()
f = open("botToken.txt", "r")
TOKEN = f.read()
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have successfully loggged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello, {message.author.display_name}!')

    if message.content.lower() == 'hey jared':
        await message.channel.send('that guy sucks dont talk to him!')

    if '??' in message.content:
        await message.add_reaction('\N{THUMBS UP SIGN}')
        await message.add_reaction('\N{THUMBS DOWN SIGN}')


client.run(TOKEN)
