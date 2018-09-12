_sdfsdf_author__ = "parin"

import config
import hashlib
import time
import re

db_conn = config.mongo_conn().rajchain_explorer
db_conn_wallet = config.mongo_conn().user_wallet


"""  ---------------------------------------- Explorer Models -------------------------------------------- """
def get_block_info_model(block_hash):
    res = db_conn.block_details.find_one({'hash':block_hash},{'_id':0})
    return res

def get_transaction_info_model(txid):
    res = db_conn.transaction_details.find_one({'txid':txid},{'_id':0})
    if res is None:
        res = db_conn.mempool_transaction_details.find_one({'txid':txid},{'_id':0})
    return res

def get_address_info_model(address):
    res = db_conn.address_details_v5.find({'address':address},{'_id':0})
    return res

def latest_nextblock_height_model():
    res = db_conn.block_details.find_one({'next_block_hash':{'$exists':False}},{'height':1})
    return res['height']

def update_nextblockhash(height,next_block_hash):
    res = db_conn.block_details.update({'height':height},{'next_block_hash':next_block_hash})
    return res

def get_block_hash_model(height):
    res = db_conn.block_details.find_one({'height':int(height)},{'_id':0})
    return res







