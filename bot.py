import json
from datetime import datetime

import discord
from functions import bot_funcs, financial
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

            if content.startswith('me'):
                with open('members.json', 'r') as details:
                    details = json.load(details)
                for user in details['users']:
                    if user['username'] == str(msg.author):
                        embed = discord.Embed(title='User Detail')
                        embed.add_field(name='**Username:**', value=f"`{user['username']}`", inline=False)
                        embed.add_field(name='**Cries:**', value=f"`{user['cries']}`", inline=False)
                        await msg.reply(embed=embed)
                        break

            if content.startswith('send'):
                able = False
                pending_string = None
                with open('members.json', 'r') as able_or_not:
                    infile = json.load(able_or_not)
                for user in infile['users']:
                    if user['username'] == str(msg.author):
                        if user['able'] == "1":
                            able = True
                    if user['pending-string'] != '':
                        pending_string = user['pending-string']

                if able:
                    content = msg.content.split('-')
                    var = datetime.now()
                    amount = content[2]
                    from_ = str(msg.author)
                    to_ = content[3]
                    event = f'{var.day}{var.month}{var.year}{var.hour}'
                    export_details = {
                        'cries': amount, 'from': from_, 'to': to_, 'event': event
                    }

                    if from_ != to_:
                        with open('members.json', 'r') as infile:
                            infile = json.load(infile)
                        for user in infile['users']:
                            if user['username'] == str(msg.author):
                                if float(user['cries']) >= float(amount):
                                    string = await bot_funcs.cries_transaction(export_details)
                                    embed = discord.Embed(title='Transaction Successful')
                                    embed.add_field(name='**From:**', value=f'`{from_}`')
                                    embed.add_field(name='**To:**', value=f'`{to_}`')
                                    embed.add_field(name='**Cries: **', value=f'`{amount}`', inline=False)
                                    embed.add_field(name='**Mine:**', value=f'`{string}`', inline=False)
                                    await msg.reply(embed=embed)
                                    break
                                else:
                                    await msg.reply('**You do not have the required `cries`**')
                                    break
                    else:
                        await msg.reply('**You cannot send `cries` to yourself**')
                else:
                    embed = discord.Embed(title='Pending Invalidated Transaction')
                    embed.add_field(name='**Username:**', value=f'`{msg.author}`', inline=False)
                    embed.add_field(name='**Mine:**', value=f'`{pending_string}`', inline=False)
                    await msg.reply(embed=embed)


        else:
            await msg.reply('**You are not a member here**')

client.run(TOKEN)
