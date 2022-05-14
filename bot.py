import json
from datetime import datetime

import discord
from functions import bot_funcs
from bot_bio import Behaviour
from store import Store

TOKEN = Behaviour.bot_token
PREFIX = Behaviour.bot_prefix

AVL_CAT_CHN_ID = Behaviour.available_cats_channels
UNAVL_CHN_ID = Behaviour.unavailable_channels
LOG_IDS = Behaviour.log_chnl_id

client = discord.Client()

emoji_dict = {
    "food": ":apple:",
    "elect": ":computer:",
    "clothes": ":shirt:",
    "other": ":toothbrush:"
}

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(msg):
    member = False
    chnl = msg.channel

    if str(msg.channel.type) == 'private' and msg.guild is None:
        await bot_funcs.private(msg)

    if msg.content.startswith(PREFIX) and str(msg.channel.type) != 'private' and \
            (msg.channel.category.id in AVL_CAT_CHN_ID or msg.channel.id in AVL_CAT_CHN_ID) and \
            msg.channel.id not in UNAVL_CHN_ID:
        content = msg.content.split('-')
        content.remove('cry')
        content = '-'.join(content).lower()

        names = []
        with open('members.json', 'r') as users_info:
            users_info = json.load(users_info)
        for user in users_info['users']:
            names.append(user['username'])

        joining = False
        if content == 'join':
            await bot_funcs.join(msg)
            joining = True

        if not joining:
            if str(msg.author) in names or member is True:
                if content == 'ledger':  # get ledger
                    with open("functions/ledger.xlsx", 'rb') as file:
                        ledger = discord.File(file)
                        await msg.author.send("Public ledger:", file=ledger)

                elif content == 'mine':  # get details to mine
                    check_for_mine = await bot_funcs.check_for_mine()
                    if check_for_mine[0]:
                        await bot_funcs.send_unsigned_transaction(msg, client)
                    else:
                        await chnl.send(f'**Wait**: `{check_for_mine[1]}/5 minutes`')

                elif content.startswith('mined'):  # check the mined transactions
                    ledger_channels = [client.get_channel(LOG_ID) for LOG_ID in LOG_IDS ]
                    await bot_funcs.check_mine(msg, ledger_channels)

                elif content.startswith('me'):  # your info
                    with open('members.json', 'r') as details:
                        details = json.load(details)
                        if len(content.split('-')) == 1:
                            for user in details['users']:
                                if user['username'] == str(msg.author):
                                    items = user['items']
                                    if len(items.keys()) == 0:
                                        items = 'None'
                                    else:
                                        items_text = ''
                                        for item in items:
                                            items_text += f'{item}: {items[item]}\n'
                                        items = items_text

                                    embed = discord.Embed(title='User Detail')
                                    embed.add_field(name='**Username:**', value=f"`{user['username']}`", inline=False)
                                    embed.add_field(name='**Cries:**', value=f"`{user['cries']}`", inline=False)
                                    embed.add_field(name='**Items:**', value=f"`{items}`", inline=False)
                                    await msg.reply(embed=embed)
                                    break
                        else:
                            username = msg.content.split('-')[2]
                            for user in details['users']:
                                if user['username'] == username:
                                    items = user['items']
                                    if len(items.keys()) == 0:
                                        items = 'None'
                                    else:
                                        items_text = ''
                                        for item in items:
                                            items_text += f'{item}: {items[item]}\n'
                                        items = items_text

                                    embed = discord.Embed(title='User Detail')
                                    embed.add_field(name='**Username:**', value=f"`{user['username']}`", inline=False)
                                    embed.add_field(name='**Cries:**', value=f"`{user['cries']}`", inline=False)
                                    embed.add_field(name='**Items:**', value=f"`{items}`", inline=False)
                                    await msg.reply(embed=embed)
                                    break

                elif content.startswith('send'):  # send cries to another user
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
                                            for LOG_ID in LOG_IDS:
                                                await client.get_channel(LOG_ID).send(f'New String: ```{string}```')
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
                        for LOG_ID in LOG_IDS:
                            await client.get_channel(LOG_ID).send(f'String: ```{pending_string}```')

                elif content.startswith('store'):  # currently, working for this
                    content = content.split('-')
                    if len(content) == 1:
                        embed = discord.Embed(title=':shopping_bags: STORE')
                        embed.add_field(name='**:apple: Food**', value="`cry-store-food`")
                        embed.add_field(name='**:shirt: Clothing**', value="`cry-store-fabric`")
                        embed.add_field(name='**:computer: Electronics**', value="`cry-store-elect`")
                        embed.add_field(name='**:toothbrush: Others**', value="`cry-store-other`")
                        await chnl.send(embed=embed)
                    else:
                        content.pop(0)
                        title = ':shopping_bags: STORE'
                        genre = content[0]
                        text = ':exclamation:Wrong Genre'
                        if content[0].startswith('food'):
                            text = ''
                            foods = Store.food
                            for food in foods.keys():
                                text += f'**{food}:** `{foods[food]} cries`\n'
                        if content[0].startswith('fab'):
                            text = ''
                            clothes = Store.clothing
                            for cloth in clothes.keys():
                                text += f'**{cloth}:** `{clothes[cloth]} cries`\n'
                        if content[0].startswith('elec'):
                            text = ''
                            elect = Store.electronic
                            for elec in elect.keys():
                                text += f'**{elec}:** `{elect[elec]} cries`\n'
                        if content[0].startswith('other'):
                            text = ''
                            others = Store.other
                            for other in others.keys():
                                text += f'**{other}:** `{others[other]} cries`\n'
                        embed = discord.Embed(title=title)
                        try:
                            genre_ = genre
                            if genre.startswith('elec'):
                                genre_ = 'Electronics'
                                genre = 'elect'
                            if genre.startswith('fab'):
                                genre_ = 'Clothing'
                                genre = 'clothes'
                            if genre.startswith('food'):
                                genre_ = 'Food'
                                genre = 'food'
                            if genre.startswith('other'):
                                genre_ = 'Others'
                                genre = 'other'
                            embed.add_field(name=f'**{emoji_dict[genre]} {genre_}:**', value=text)
                        except KeyError:
                            embed.add_field(name=f'**{genre}:**', value=text)
                        await chnl.send(embed=embed)

                elif content.startswith('buy'):
                    content = content.split('-')
                    if len(content) == 2:
                        await bot_funcs.buy_item(msg, content[1], msg.author, client, LOG_IDS)

                elif content.startswith('minecode'):
                    with open('mine.py', 'rb') as send_code:
                        file = discord.File(send_code)
                        await chnl.send('**Code for mining hash:**', file=file)

                else:
                    await chnl.send('**Wrong or Misunderstood command**')

            elif content == 'update':  # update user
                proceed = True
                with open('members.json', 'r') as members:
                    members = json.load(members)
                for user in members['users']:
                    if user['username'] == str(msg.author):
                        proceed = False
                        break

                if proceed:
                    with open('editing_user.json', 'r') as inusers:
                        inusers = json.load(inusers)
                        inusers['update_users'].append(str(msg.author))
                    with open('editing_user.json', 'w') as outusers:
                        json.dump(inusers, outusers, indent=4)
                    await msg.author.send('**Password and Old Username:** *(format:**my_own_password,old_username**)*')
                    await msg.add_reaction('👍')
                else:
                    msg.reply('Already Up-To-Date!')

            else:
                await msg.reply('**You are not a member here\nIf your username got updated, use `cry-update`**')

client.run(TOKEN)
