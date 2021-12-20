import json
import discord
from datetime import datetime

from functions import financial

FACTOR = 10**15


async def join(message):
    chnl = message.channel
    user_info = {
        'username': str(message.author),
        'cries': '0'
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
    total_transactions = financial.max_row()
    genesis = False
    with open('members.json', 'r') as file_transactions:
        check_transactions = json.load(file_transactions)
        if int(int(check_transactions['total-transactions']) == total_transactions == 0):
            financial.genesis_block()
            genesis = True

    if genesis:
        with open('members.json', 'r') as file_transactions:
            file_transactions = json.load(file_transactions)
            unmined_string = file_transactions['current-unmined-string']

        embed = discord.Embed(title='Mining')
        embed.add_field(name='Mine', value=f'`{unmined_string[0]}`', inline=False)
        embed.add_field(name='Format', value=f'`Index/Details/Previous-Hash/Nonce`')
        embed.add_field(name='Suffix for the string', value='`/~~mined-Hash`')
        embed.add_field(name='Hash Signature', value='`2005c`')

        await message.channel.send(embed=embed)
        await message.channel.send('** **')
        await message.channel.send('This is the `Genesis Block`, **first block of the chain**')


async def check_mine(message):
    user_mined_string = message.content.split('-')
    user_mined_string.remove('cry')
    user_mined_string.remove('mined')
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

    if user_mined_hash == user_mined_string_to_hash and user_mined_hash.startswith('~~2005c') \
            and user_mined_string.startswith(current_hash):
        await message.channel.send(f'Eureka, First block created by {message.author.mention}')
        export_data = {
            'transaction_string': user_mined_string,
            'author': str(message.author),
            'hash': user_mined_hash,
        }
        await award_user(export_data)


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


async def check_for_mine():
    with open('members.json', 'r') as infile:
        check_last = json.load(infile)
    if check_last['last-activity'] != "":
        last = check_last['last-activity']
        var = datetime.now()
        time_difference = datetime(var.year, var.month, var.day, var.hour, var.minute, var.second) - datetime.strptime(last, '%Y/%m/%d %H:%M:%S')
        if time_difference.seconds/60 < 5:
            return [False, round(time_difference.seconds/60)]
        else:
            return [True]
    else:
        return [True]
