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
    print('i can see this')
    print(message.content)
    if message.author == client.user:
        return

    if message.content.lower() == 'hello':
        await message.channel.send(f'Hello, {message.author.display_name}!')

    if message.content == 'hey jared':
        await message.channel.send('that guy sucks dont talk to him!')


client.run(TOKEN)