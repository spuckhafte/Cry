import random
from datetime import datetime
import json
from bot_bio import Behaviour
import openpyxl as xl
from cryptography.fernet import Fernet
import hashlib

key = Fernet.generate_key()
fernet = Fernet(key)

# loading the ledger
try:
    with open('functions/ledger.xlsx', 'rb') as outfile:
        ledger_wb = xl.load_workbook(outfile)
except FileNotFoundError:
    with open('ledger.xlsx', 'rb') as outfile:
        ledger_wb = xl.load_workbook(outfile)
ledger_sheet = ledger_wb['Sheet1']

# 1 CryCoin = $100 = Rs.7601

# value of the entity
info = {
    'Cr.1': '$.100',
    'Format': '1/10?:CryCoin(1812210)/0000000000000000000000000000000000000000000000000000000000000000/1157551/--2005ca051baeb3b0557ee056c28ec3f0e76e25bf3a2fafd14227b6a3c2bae2ae'
}


class EncDeEnc:
    def __init__(self, deEncrypted='', Encrypted=b''):
        self.enc = Encrypted
        self.deEnc = deEncrypted

    def value_encrypt(self):
        enc_value = fernet.encrypt(self.deEnc.encode())
        return enc_value

    def value_decrypt(self):
        de_enc_value = fernet.decrypt(self.enc).decode()
        return de_enc_value

    def hash_encrypt(self):
        enc = hashlib.sha256(self.deEnc.encode()).hexdigest()
        return enc


def mine(transaction_data):
    array_transaction_data = transaction_data.split('/')
    if len(array_transaction_data) > 3:
        array_transaction_data.pop()
    i = 0

    while True:
        if len(array_transaction_data) > 3:
            array_transaction_data.pop()

        array_transaction_data.append(str(i))
        new_transaction_data = '/'.join(array_transaction_data)
        encryption_on_data = EncDeEnc(deEncrypted=new_transaction_data).hash_encrypt()

        if encryption_on_data.startswith('2005c'):
            new_transaction_data += f'/~~{encryption_on_data}'
            return [new_transaction_data, encryption_on_data]
        else:
            i += 1


def max_row():
    return ledger_sheet.max_row-1


def genesis_block():
    day, month, year, hour = str(datetime.now().day), str(datetime.now().month), str(datetime.now().year), str(datetime.now().hour)
    datetime_str = day+month+year+hour
    prev_hash = None
    to = 'CryCoin'
    from_ = '?'
    amount = '0'
    if max_row() == 0:
        fac = Behaviour.cry_factor
        with open('members.json', 'r') as infile:
            infile = json.load(infile)
        members = [user['username'] for user in infile['users']]
        cries = [int(user['cries'])*fac if int(user['cries']) != 0 else fac for user in infile['users']]

        amount = '10'
        to = random.choices(members, cries)[0]
        prev_hash = '0000000000000000000000000000000000000000000000000000000000000000'

    details = [str(max_row()+1), amount, from_, to, datetime_str, f'{prev_hash}', 'nonce']
    raw_transaction_string = f"{details[0]}/{details[1]}{details[2]}:{details[3]}({details[4]})/{details[5]}/{details[6]}"

    with open('members.json', 'r') as file:
        hash_trans_string = json.load(file)

    hash_trans_string['current-unmined-string'].append(raw_transaction_string)
    var = datetime.now()
    hash_trans_string['last-activity'] = f'{var.year}/{var.month}/{var.day} {var.hour}:{var.minute}:{var.second}'

    with open('members.json', 'w') as file:
        json.dump(hash_trans_string, file, indent=4)


# print(mine('1/10?:spuckhafte_ferwirklung#7109(2012202123)/0000000000000000000000000000000000000000000000000000000000000000/nonce'))
