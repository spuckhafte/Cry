import json
from datetime import datetime

import discord
from functions import bot_funcs, financial
from bot_bio import Behaviour

TOKEN = Behaviour.bot_token
PREFIX = Behaviour.bot_prefix
GEN_CAT_ID = Behaviour.general_channel_category_id
HELP_ID = Behaviour.help_chnl_id
LOG_ID = Behaviour.log_chnl_id
client = discord.Client()


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")


@client.event
async def on_message(msg):
    member = False
    chnl = msg.channel

    if str(msg.channel.type == 'private') and int(msg.channel.id) != HELP_ID:
        with open('editing_user.json', 'r') as infile:
            infile = json.load(infile)
        if str(msg.author) in infile['update_users']:
            if msg.content != 'cry-help-stop' or msg.content.startswith('cry-help-mod') is False:
                try:
                    password = financial.EncDeEnc(deEncrypted=msg.content.split(',')[0]).hash_encrypt()
                    old_name = msg.content.split(',')[1]
                    user_found = False
                    with open('members.json', 'r') as members:
                        members = json.load(members)
                    for user in members['users']:
                        if user['password'] == password and user['username'] == old_name:
                            user_found = True
                            user['username'] = str(msg.author)
                            break
                    with open('members.json', 'w') as outfile:
                        json.dump(members, outfile, indent=4)

                    if user_found:
                        with open('editing_user.json', 'r') as infile_2:
                            infile_2 = json.load(infile_2)
                        infile_2['update_users'].remove(str(msg.author))
                        with open('editing_user.json', 'w') as outfile_2:
                            json.dump(infile_2, outfile_2, indent=4)
                        await msg.author.send('Username updated!')
                    else:
                        with open('editing_user.json', 'r') as infile_2:
                            infile_2 = json.load(infile_2)
                        infile_2['update_users'].remove(str(msg.author))
                        with open('editing_user.json', 'w') as outfile_2:
                            json.dump(infile_2, outfile_2, indent=4)
                        await chnl.send('**Wrong password/old_username, or you never existed in this ecosystem**')
                        await chnl.send('Process Terminated!!!')

                except:
                    with open('editing_user.json', 'r') as infile_2:
                        infile_2 = json.load(infile_2)
                    infile_2['update_users'].remove(str(msg.author))
                    with open('editing_user.json', 'w') as outfile_2:
                        json.dump(infile_2, outfile_2, indent=4)
                    await chnl.send('Process Terminated')

            if msg.content == 'cry-help-stop':
                with open('editing_user.json', 'r') as infile_2:
                    infile_2 = json.load(infile_2)
                infile_2['update_users'].remove(str(msg.author))
                with open('editing_user.json', 'w') as outfile_2:
                    json.dump(infile_2, outfile_2, indent=4)
                await chnl.send('Process Terminated!')

            if msg.content.startswith('cry-help-mod'):
                with open('editing_user.json', 'r') as infile_2:
                    infile_2 = json.load(infile_2)
                infile_2['update-users'].remove(str(msg.author))
                with open('editing_user.json', 'w') as outfile_2:
                    json.dump(infile_2, outfile_2, indent=4)
                msg_arr = msg.content.split('-')
                if len(msg_arr) > 3:
                    query = msg_arr.pop()
                    channel = client.get_channel(HELP_ID)
                    await channel.send(f'{str(msg.author.mention)} says, **\"{query}\"** ')
                    await msg.add_reaction('👍')
                await chnl.send('Process Terminated')

        if str(msg.author) in infile['password_candidates']:
            if msg.content.startswith('cry-pass-'):
                password_arr = msg.content.split('-')
                password_arr.remove('cry')
                password_arr.remove('pass')
                password_string = ''.join(password_arr)
                password = financial.EncDeEnc(deEncrypted=password_string).hash_encrypt()

                proceed = True
                with open('members.json', 'r') as infile:
                    infile = json.load(infile)
                for user in infile['users']:
                    if user['password'] == password:
                        proceed = False
                        break

                if len(password_string) < 4:
                    proceed = False

                if proceed:
                    await msg.channel.send(f'Your password: {password_string}')
                    user_info = {
                        'username': str(msg.author),
                        'cries': '0',
                        'password': password,
                        'able': '1',
                        'pending-string': ''
                    }

                    with open('members.json', 'r') as members_list_read:
                        users_info = json.load(members_list_read)

                    users_info['users'].append(user_info)

                    json_users_info = json.dumps(users_info, indent=4)
                    with open("members.json", "w") as member_list_write:
                        member_list_write.write(json_users_info)

                    with open('editing_user.json', 'r') as infile:
                        infile = json.load(infile)
                    infile['password_candidates'].remove(str(msg.author))
                    with open('editing_user.json', 'w') as outfile:
                        json.dump(infile, outfile, indent=4)

                    with open("functions/ledger.xlsx", 'rb') as file:
                        ledger = discord.File(file)
                        await msg.channel.send("**Welcome, this is the Public Ledger:**", file=ledger)
                else:
                    with open('editing_user.json', 'r') as infile:
                        infile = json.load(infile)
                    infile['password_candidates'].remove(str(msg.author))
                    with open('editing_user.json', 'w') as outfile:
                        json.dump(infile, outfile, indent=4)

                    if len(password_string) < 4:
                        await chnl.send('Password should have **4 or more characters** and should **not contain dashes(-)**\n**Process Terminated!**')
                    else:
                        await chnl.send('This password is already being used by someone.\n**Process Terminated!**')

            if msg.content == 'cry-help-stop':
                with open('editing_user.json', 'r') as infile_2:
                    infile_2 = json.load(infile_2)
                infile_2['password_candidates'].remove(str(msg.author))
                with open('editing_user.json', 'w') as outfile_2:
                    json.dump(infile_2, outfile_2, indent=4)
                await chnl.send('Process Terminated!')

            if msg.content.startswith('cry-help-mod'):
                with open('editing_user.json', 'r') as infile_2:
                    infile_2 = json.load(infile_2)
                infile_2['password_candidates'].remove(str(msg.author))
                with open('editing_user.json', 'w') as outfile_2:
                    json.dump(infile_2, outfile_2, indent=4)
                msg_arr = msg.content.split('-')
                if len(msg_arr) > 3:
                    query = msg_arr.pop()
                    channel = client.get_channel(HELP_ID)
                    await channel.send(f'{str(msg.author.mention)} says, **\"{query}\"** ')
                    await msg.add_reaction('👍')
                await chnl.send('Process Terminated')

    if msg.content.startswith(PREFIX) and str(msg.channel.type) != 'private' and msg.channel.category.id != GEN_CAT_ID:
        content = msg.content.split('-')
        content.remove('cry')
        content = ''.join(content).lower()

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
                if content == 'ledger':
                    with open("functions/ledger.xlsx", 'rb') as file:
                        ledger = discord.File(file)
                        await msg.author.send("Public ledger:", file=ledger)

                elif content == 'mine':
                    check_for_mine = await bot_funcs.check_for_mine()
                    if check_for_mine[0]:
                        await bot_funcs.send_unsigned_transaction(msg, client)
                    else:
                        await chnl.send(f'**Wait**: `{check_for_mine[1]}/5 minutes`')

                elif content.startswith('mined'):
                    ledger_channel = client.get_channel(LOG_ID)
                    await bot_funcs.check_mine(msg, ledger_channel)

                elif content.startswith('me'):
                    with open('members.json', 'r') as details:
                        details = json.load(details)
                    for user in details['users']:
                        if user['username'] == str(msg.author):
                            embed = discord.Embed(title='User Detail')
                            embed.add_field(name='**Username:**', value=f"`{user['username']}`", inline=False)
                            embed.add_field(name='**Cries:**', value=f"`{user['cries']}`", inline=False)
                            await msg.reply(embed=embed)
                            break

                elif content.startswith('send'):
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
                        await client.get_channel(LOG_ID).send(f'String: ```{pending_string}```')

                elif content.startswith('minecode'):
                    with open('mine.py', 'rb') as send_code:
                        file = discord.File(send_code)
                        await chnl.send('**Code for mining hash:**', file=file)

                else:
                    await chnl.send('**Wrong or Misunderstood command**')

            elif content == 'update':
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
