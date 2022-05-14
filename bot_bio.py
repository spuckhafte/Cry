class Behaviour:
    bot_token = ''
    bot_prefix = ''
    cry_factor = None  # number, showing the most average amount amount of cries (eg. 0.0000001)
    hash_sign = '' # text that should be in the start of every hash of a transaction (eg. 2005cc34trg35yt...)
    default_hash = '0000000000000000000000000000000000000000000000000000000000000000' # default hash, for the first block (first block can't have a prev hash)
    time_out = 0 # people can use 'cry-mine' in this time interval (minutes)
    default_amount = 0 # 'cries' sent to the first lucky user (genesis block)
    available_cats_channels = [] # channels and categories where the bot is allowed to be used
    unavailable_channels = [] # channels where bot is not allowed
    log_chnl_id = [] # channel where bot sends notifications for new "mine-able" strings and updated ledgers
