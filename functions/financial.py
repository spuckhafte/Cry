import random
from datetime import datetime
import json
from bot_bio import Behaviour
import openpyxl as xl
from cryptography.fernet import Fernet
import hashlib

SIGN = Behaviour.hash_sign
DEF_AMOUNT = Behaviour.default_amount

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
    'Format': '1/10,?:CryCoin(1812210)/0000000000000000000000000000000000000000000000000000000000000000/1157551/--2005ca051baeb3b0557ee056c28ec3f0e76e25bf3a2fafd14227b6a3c2bae2ae'
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

        if encryption_on_data.startswith(SIGN):
            new_transaction_data += f'/~~{encryption_on_data}'
            return [new_transaction_data, encryption_on_data]
        else:
            i += 1


def max_row():
    return ledger_sheet.max_row - 1


def previous_hash():
    row = max_row()
    prev = ledger_sheet.cell(row+1, 8).value if row != 0 else Behaviour.default_hash
    return prev


def genesis_block():
    day, month, year, hour = str(datetime.now().day), str(datetime.now().month), str(datetime.now().year), str(
        datetime.now().hour)
    datetime_str = day + month + year + hour

    from_ = '?'

    fac = Behaviour.cry_factor
    with open('members.json', 'r') as infile:
        infile = json.load(infile)
    members = [user['username'] for user in infile['users']]
    cries = [float(user['cries']) * fac if float(user['cries']) != 0 else 1/fac for user in infile['users']]

    amount = float(DEF_AMOUNT) if max_row() == 0 else float(1/fac)
    to = random.choices(members, cries)[0]
    prev_hash = previous_hash()

    details = [str(max_row() + 1), amount, from_, to, datetime_str, f'{prev_hash}', 'nonce']
    raw_transaction_string = f"{details[0]}/{details[1]},{details[2]}:{details[3]}({details[4]})/{details[5]}/{details[6]}"

    with open('members.json', 'r') as file:
        hash_trans_string = json.load(file)

    hash_trans_string['current-unmined-string'].append(raw_transaction_string)
    var = datetime.now()
    hash_trans_string['last-activity'] = f'{var.year}/{var.month}/{var.day} {var.hour}:{var.minute}:{var.second}'

    with open('members.json', 'w') as file:
        json.dump(hash_trans_string, file, indent=4)

    export_data = {
        'cries': amount,
        'to': to,
        'from': from_
    }

    return export_data


def sync_xl(data):
    dumping_data = [max_row() + 1, data['amount'], data['from'], data['to'], data['event'], data['last-hash'],
                    data['string'], data['hash']]

    row = max_row()+2
    for index in range(1, len(dumping_data)+1):
        ledger_sheet.cell(row, index).value = dumping_data[index-1]
    ledger_wb.save('./functions/ledger.xlsx')


# print(mine('3/1e-15,?:spuckhafte_ferwirklung#7109(2212202119)/2005cc89e900928d541c57c0776992efb60b6a60a3566780d531bbcdb974f23e/nonce'))