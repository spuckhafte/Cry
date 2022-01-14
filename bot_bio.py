class Behaviour:
    bot_token = ''
    bot_prefix = ''
    cry_factor = None  # number, showing the most average amount amount of cries (eg. 0.0000001)
    hash_sign = '' # text that should be in the start of every hash of a transaction (eg. 2005cc34trg35yt...)
    default_hash = '0000000000000000000000000000000000000000000000000000000000000000' # default hash, for the first block (first block can't have a prev hash)
    time_out = 0 # people can use 'cry-mine' in this time interval (minutes)
    default_amount = 0 # 'cries' sent to the first lucky user (genesis block)
    new_string_channel_id = 0 # id of a channel where all new "minable" strings could be sent
    general_channel_category_id = 0 # id of "General" Category in the official server (people chill in this category)
    test_category_id = 0 # id of a category in server named "Bot Testing"
    help_chnl_id = 0 # id of a channel where users can seek help from the moderators
    log_chnl_id = 0 # == new_string_channel_id (both the id are of the same channel, did it by mistake lol)
