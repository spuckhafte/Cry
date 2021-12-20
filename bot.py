import json
import discord
from functions import bot_funcs
from bot_bio import Behaviour

TOKEN = Behaviour.bot_token
PREFIX = Behaviour.bot_prefix
client = discord.Client()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(msg):
    member = False
    chnl = msg.channel
    if msg.content.lower().startswith(PREFIX):
        content = msg.content.split('-')
        content.remove('cry')
        content = ''.join(content).lower()

        names = []
        with open('members.json', 'r') as users_info:
            users_info = json.load(users_info)
        for user in users_info['users']:
            names.append(user['username'])

        if content == 'join':
            await bot_funcs.join(msg)
            with open("functions/ledger.xlsx", 'rb') as file:
                ledger = discord.File(file)
                await msg.author.send("This is the public ledger:", file=ledger)
                member = True

        if str(msg.author) in names or member is True:
            if content == 'send ledger':
                with open("functions/ledger.xlsx", 'rb') as file:
                    ledger = discord.File(file)
                    await msg.author.send("Public ledger:", file=ledger)

            if content == 'mine':
                check_for_mine = await bot_funcs.check_for_mine()
                if check_for_mine[0]:
                    await bot_funcs.send_unsigned_transaction(msg)
                else:
                    await chnl.send(f'**Wait**: `{check_for_mine[1]}/5 minutes`')

            if content.startswith('mined'):
                await bot_funcs.check_mine(msg)
        else:
            await msg.reply('**You are not a member here**')

client.run(TOKEN)
