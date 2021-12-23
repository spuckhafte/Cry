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
            if content == 'ledger':
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
                user_not_found = True
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
                    content.remove('cry')
                    content.remove('send')
                    var = datetime.now()
                    to_ = content.pop()
                    from_ = str(msg.author)
                    amount = '-'.join(content)
                    event = f'{var.day}{var.month}{var.year}{var.hour}'
                    export_details = {
                        'cries': amount, 'from': from_, 'to': to_, 'event': event
                    }

                    is_floatable = False
                    try:
                        float(amount)
                        is_floatable = True
                    except ValueError:
                        is_floatable = False

                    if from_ != to_:
                        with open('members.json', 'r') as infile:
                            infile = json.load(infile)

                        for user in infile['users']:
                            if user['username'] == to_:
                                user_not_found = False

                        if user_not_found is False and is_floatable:
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
                                        await chnl.send(f'```{string}```')
                                        break
                                    else:
                                        await msg.reply('**You do not have the required `cries`**')
                                        break
                        if user_not_found:
                            await msg.reply(f'**No such user: `{to_}`**')
                        if is_floatable is False:
                            await msg.reply('**Cries you requested for transaction are not valid, not a number**')
                    else:
                        await msg.reply('**You cannot send `cries` to yourself**')

                else:
                    embed = discord.Embed(title='Pending Invalidated Transaction')
                    embed.add_field(name='**Username:**', value=f'`{msg.author}`', inline=False)
                    embed.add_field(name='**Mine:**', value=f'`{pending_string}`', inline=False)
                    await msg.reply(embed=embed)

            if content.startswith('minecode'):
                with open('mine.py', 'rb') as send_code:
                    file = discord.File(send_code)
                    await chnl.send('**Code for mining hash:**', file=file)
        else:
            await msg.reply('**You are not a member here**')

client.run(TOKEN)
