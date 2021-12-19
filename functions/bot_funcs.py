import json

import discord

from functions import financial


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
        embed.add_field(name='Mine', value=f'`{unmined_string}`', inline=False)
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

    if user_mined_hash == user_mined_string_to_hash and user_mined_hash.startswith('~~2005c'):
        await message.channel.send(f'Eureka, First block created by {message.author.mention}')
