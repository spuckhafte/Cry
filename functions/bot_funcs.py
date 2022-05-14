import json
import discord
from datetime import datetime
from bot_bio import Behaviour
from functions import financial
from store import Store

FACTOR = Behaviour.cry_factor
SIGN = Behaviour.hash_sign
TIMEOUT = Behaviour.time_out
STRING_CHANNEL_IDS = Behaviour.log_chnl_id


async def join(message):
    proceed = True
    with open('members.json', 'r') as infile:
        infile = json.load(infile)
    for user in infile['users']:
        if user['username'] == str(message.author):
            proceed = False
            break

    if proceed:
        with open('editing_user.json', 'r') as infile:
            infile = json.load(infile)
        infile['password_candidates'].append(str(message.author))
        with open('editing_user.json', 'w') as outfile:
            json.dump(infile, outfile)
        await message.author.send('**Create password** (more than 4 characters)\n`cry-pass-your_password` *password should not have dashes(-)*')
        await message.add_reaction('👍')
    else:
        await message.reply('Already a member!')


async def send_unsigned_transaction(message, Client):
    genesis = False
    string = None
    with open('members.json', 'r') as file_transactions:
        check_transactions = json.load(file_transactions)
        diff = await difference_in_time() if await difference_in_time() is not None else TIMEOUT+1

        if len(check_transactions['current-unmined-string']) == 0 and diff > TIMEOUT:
            import_data = financial.genesis_block()
            await transaction(import_data)
            with open('members.json', 'r') as temp_open:
                temp_open = json.load(temp_open)
                string = temp_open['current-unmined-string'][0]
            genesis = True

        if len(check_transactions['current-unmined-string']) != 0:
            string = check_transactions['current-unmined-string'][0]
            var = datetime.now()
            with open('members.json', 'r') as temp_open:
                temp_open = json.load(temp_open)
                temp_open['last-activity'] = f'{var.year}/{var.month}/{var.day} {var.hour}:{var.minute}:{var.second}'
            with open('members.json', 'w') as outfile:
                json.dump(temp_open, outfile, indent=4)
            genesis = True

    if genesis:
        embed = discord.Embed(title='Mining')
        embed.add_field(name='Mine', value=f'`{string}`', inline=False)
        embed.add_field(name='Format', value=f'`Index/Details/Previous-Hash/Nonce`')
        embed.add_field(name='Suffix for the string', value='`/~~mined-Hash`')
        embed.add_field(name='Hash Signature', value=f'`{SIGN}`')
        await message.channel.send(embed=embed)
        await message.channel.send(f'```{string}```')
        for STRING_CHANNEL_ID in STRING_CHANNEL_IDS:
            await Client.get_channel(STRING_CHANNEL_ID).send(f'New string:```{string}```')
        if financial.max_row() == 0:
            await message.channel.send('This is the `Genesis Block`, **first block of the chain**')


async def check_mine(message, ledger_channels):
    user_mined_string = message.content.split('-')
    user_mined_string.remove('cry')
    user_mined_string.remove('mined')
    user_mined_string = ''.join(user_mined_string)
    if user_mined_string.index('e') < user_mined_string.index(':') and \
            user_mined_string[user_mined_string.index('e')-1].isalpha() is False:
        user_mined_string = list(user_mined_string)
        user_mined_string.insert(user_mined_string.index('e') + 1, '-')
        user_mined_string = ''.join(user_mined_string)
    user_mined_string = user_mined_string.split('/')

    user_mined_hash = user_mined_string.pop()

    check_availability = list(user_mined_hash)
    check_availability.remove('~')
    check_availability.remove('~')
    check_availability = ''.join(check_availability)

    user_mined_string = '/'.join(user_mined_string)
    user_mined_string_to_hash = f'~~{financial.EncDeEnc(deEncrypted=user_mined_string).hash_encrypt()}'

    if await financial.check_hash_availiblity(check_availability):
        with open('members.json', 'r') as infile:
            infile = json.load(infile)

        current_string = infile['current-unmined-string'][0]
        current_hash = current_string.split('/')
        current_hash.pop()
        current_hash = '/'.join(current_hash)

        if user_mined_hash == user_mined_string_to_hash and user_mined_hash.startswith(f'~~{SIGN}') \
                and user_mined_string.startswith(current_hash):
            if financial.max_row() == 0:
                await message.channel.send(f'Eureka, First block created by {message.author.mention}')

            details = ''.join(user_mined_string.split('/')[1]).split(':')
            amount, from_ = ''.join(details[0]).split(',')[0], ''.join(details[0]).split(',')[1]
            to_, event = ''.join(details[1]).split('(')[0], ''.join(details[1]).split('(')[1].split(')')[0]
            last_hash = financial.previous_hash()
            user_mined_hash = list(user_mined_hash)
            user_mined_hash.remove('~')
            user_mined_hash.remove('~')
            user_mined_hash = ''.join(user_mined_hash)
            export_data = {
                'transaction_string': user_mined_string,
                'author': str(message.author),
                'amount': str(amount), 'to': to_, 'from': from_, 'event': event,
                'last-hash': last_hash, 'string': user_mined_string, 'hash': user_mined_hash
            }
            cries = await award_user(export_data)
            await message.channel.send(f'{message.author.mention} **Congo, You got: `{float(cries)} cries`**')
            financial.sync_xl(export_data)

            with open('members.json', 'r') as infile:
                infile = json.load(infile)
            with open('members.json', 'w') as outfile:
                for string in infile['current-unmined-string']:
                    string = string.split('/')
                    string.pop()
                    string = '/'.join(string)
                    if user_mined_string.startswith(string):
                        infile['current-unmined-string'].remove(string+'/nonce')

                if '?' not in user_mined_string.split(':')[0]:
                    for user in infile['users']:
                        if user['username'] in user_mined_string.split(':')[0]:
                            if user['able'] == '0':
                                user['able'] = '1'
                                user['pending-string'] = ""
                json.dump(infile, outfile, indent=4)

            with open("functions/ledger.xlsx", 'rb') as file:
                ledger = discord.File(file)
                for ledger_channel in ledger_channels:
                    await ledger_channel.send("Public ledger - updated:", file=ledger)
        else:
            if not user_mined_string.startswith(current_hash):
                await message.channel.send(f'Wrong string mined.\nMine: `{current_string}`\n*Order for mining is being followed here*')
            await message.channel.send('**Wrong Hash**')
    else:
        await message.channel.send('**Hash is already mined**')


async def buy_item(msg, item, user, client, LOG_IDS):
    all_items = Store.clothing
    all_items.update(Store.other)
    all_items.update(Store.food)
    all_items.update(Store.electronic)
    if item in all_items.keys():
        item_price = all_items[item]
        with open('members.json', 'r') as infile:
            infile = json.load(infile)
        for user_ in infile['users']:
            if user_['username'] == str(user):
                if user_['able'] == "1":
                    if float(user_['cries']) >= float(item_price):
                        user_['cries'] = str(float(user_['cries']) - float(item_price))
                        if len(user_['items'].keys()) == 0:
                            user_['items'] = {item: 1}
                        else:
                            if item in user_['items'].keys():
                                user_['items'][item] += 1
                            else:
                                user_['items'][item] = 1

                        var = datetime.now()
                        event = f'{var.day}{var.month}{var.year}{var.hour}'
                        export_data = {
                            "cries": item_price,
                            "from": str(user),
                            "to": "?",
                            "event": event
                        }
                        with open('members.json', 'w') as outfile:
                            json.dump(infile, outfile, indent=4)
                        await cries_transaction(export_data)
                        await msg.channel.send(f'{user.mention} **Congo, You got: `{item}` for `{item_price} cries`**')
                        break
                    else:
                        await msg.reply(f'{user} you do not have enough cries to buy {item}')
                        break
                else:
                    pending_string = user_['pending-string']
                    embed = discord.Embed(title='Pending Invalidated Transaction')
                    embed.add_field(name='**Username:**', value=f'`{msg.author}`', inline=False)
                    embed.add_field(name='**Mine:**', value=f'`{pending_string}`', inline=False)
                    await msg.reply(embed=embed)
                    for LOG_ID in LOG_IDS:
                        await client.get_channel(LOG_ID).send(f'String: ```{pending_string}```')
                    break
    else:
        await msg.reply(f'{item} is not available')


async def award_user(data):
    nonce = data['transaction_string'].split('/')
    nonce = nonce.pop()

    cries = float(int(nonce) / FACTOR)

    with open('members.json', 'r') as file:
        cry_file = json.load(file)
    for index in range(0, len(cry_file['users'])):
        if cry_file['users'][index]['username'] == data['author']:
            cry_file['users'][index]['cries'] = str(float(cry_file['users'][index]['cries']) + cries)
            break

    with open('members.json', 'w') as outfile:
        json.dump(cry_file, outfile, indent=4)

    return cries


async def check_for_mine():
    time_difference = await difference_in_time()
    if time_difference is not None:
        if time_difference / 60 < TIMEOUT:
            return [False, round(time_difference / 60, 1)]
        else:
            return [True]
    else:
        return [True]


async def transaction(data):
    amount = data['cries']
    to_ = data['to']
    from_ = data['from']

    with open('members.json', 'r') as read_only:
        read_only = json.load(read_only)
    if to_ != '?':
        for user in read_only['users']:
            if user['username'] == to_:
                user['cries'] = str(float(user['cries']) + float(amount))
                break
        if from_ != '?':
            for user in read_only['users']:
                if user['username'] == from_:
                    user['cries'] = str(float(user['cries']) - float(amount))

    with open('members.json', 'w') as outfile:
        json.dump(read_only, outfile, indent=4)


async def difference_in_time():
    with open('members.json', 'r') as infile:
        check_last = json.load(infile)
    if check_last['last-activity'] != '':
        last = check_last['last-activity']
        var = datetime.now()
        diff = datetime(var.year, var.month, var.day, var.hour, var.minute, var.second) - datetime.strptime(last,
                                                                                                            '%Y/%m/%d %H:%M:%S')
        return diff.seconds
    else:
        return None


async def extract_data_from_string(transaction_string):
    transaction_array = transaction_string.split('/')
    details = transaction_array[1].split(':')
    amount = details[0].split(',')[0]
    from_ = details[0].split(',')[1]
    to_ = details[1].split('(')[0]
    event = details[1].split['('][1].split(')')[0]
    prev_hash = transaction_array[2]
    string = transaction_string
    cur_hash = transaction_array.pop()

    export_info = {
        'amount': amount, 'from': from_, 'to': to_, 'event': event,
        'last-hash': prev_hash, 'string': string, 'hash': cur_hash
    }
    return export_info


async def cries_transaction(data):
    with open('members.json', 'r') as infile:
        infile = json.load(infile)
    if len(infile['current-unmined-string']) != 0:
        last_string = infile['current-unmined-string'].pop()
        last_index = last_string.split('/')[0]
        index = int(last_index) + 1
    else:
        index = financial.max_row() + 1

    index, amount, from_, to_, event = index, data['cries'], data['from'], data['to'], data['event']
    prev_hash = financial.previous_hash()
    transaction_string = f'{index}/{amount},{from_}:{to_}({event})/{prev_hash}/nonce'

    var = datetime.now()
    last_activity = f'{var.year}/{var.month}/{var.day} {var.hour}:{var.minute}:{var.second}'

    with open('members.json', 'r') as edit_current_strings:
        infile = json.load(edit_current_strings)
    infile['current-unmined-string'].append(transaction_string)
    infile['last-activity'] = f'{last_activity}'
    for user in infile['users']:
        if user['username'] == from_:
            user['pending-string'] = transaction_string
            user['able'] = "0"

    with open('members.json', 'w') as outfile:
        json.dump(infile, outfile, indent=4)

    await transaction(data)
    return transaction_string


async def private(msg):
    chnl = msg.channel
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
                    'pending-string': '',
                    'items': {}
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
                    await chnl.send(
                        'Password should have **4 or more characters** and should **not contain dashes(-)**\n**Process Terminated!**')
                else:
                    await chnl.send('This password is already being used by someone.\n**Process Terminated!**')

        if msg.content == 'cry-help-stop':
            with open('editing_user.json', 'r') as infile_2:
                infile_2 = json.load(infile_2)
            infile_2['password_candidates'].remove(str(msg.author))
            with open('editing_user.json', 'w') as outfile_2:
                json.dump(infile_2, outfile_2, indent=4)
            await chnl.send('Process Terminated!')
