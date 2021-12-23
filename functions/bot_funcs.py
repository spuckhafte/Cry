import json
import discord
from datetime import datetime
from bot_bio import Behaviour
from functions import financial

FACTOR = Behaviour.cry_factor
SIGN = Behaviour.hash_sign
TIMEOUT = Behaviour.time_out


async def join(message):
    chnl = message.channel
    user_info = {
        'username': str(message.author),
        'cries': '0',
        'able': '1',
        'pending-string': ''
    }

    with open('members.json', 'r') as members_list_read:
        users_info = json.load(members_list_read)

    for user in users_info['users']:
        if user['username'] == str(message.author):
            await chnl.send("Already a member!")
            return

    users_info['users'].append(user_info)

    json_users_info = json.dumps(users_info, indent=4)
    with open("members.json", "w") as member_list_write:
        member_list_write.write(json_users_info)

    await chnl.send('**Welcome, Public ledger has been sent to you privately**')


async def send_unsigned_transaction(message):
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
        if financial.max_row() == 0:
            await message.channel.send('This is the `Genesis Block`, **first block of the chain**')


async def check_mine(message):
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
    user_mined_string = '/'.join(user_mined_string)
    user_mined_string_to_hash = f'~~{financial.EncDeEnc(deEncrypted=user_mined_string).hash_encrypt()}'

    with open('members.json', 'r') as infile:
        infile = json.load(infile)
    current_hash = infile['current-unmined-string'][0].split('/')
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
            if '?' not in user_mined_string:
                if str(message.author) in user_mined_string.split('/')[1].split(':')[0]:
                    for user in infile['users']:
                        if user['username'] == str(message.author):
                            user['pending-string'] = ''
                            user['able'] = "1"
            json.dump(infile, outfile, indent=4)

        with open("functions/ledger.xlsx", 'rb') as file:
            ledger = discord.File(file)
            await message.channel.send("Public ledger - updated:", file=ledger)
    else:
        await message.channel.send('**Wrong Hash**')


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
    index, amount, from_, to_, event = financial.max_row()+1, data['cries'], data['from'], data['to'], data['event']
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

