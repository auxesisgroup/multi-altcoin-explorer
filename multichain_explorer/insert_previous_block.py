__author__ = 'udasi'

# import time

import config
from wrap_core import *

db_conn = config.mongo_conn().rajchain_explorer
redis_conn = config.redis_conn()

block_counter = 0
current_block_height = getblockcount(config.testnet['btc_prefix'],config.payload)
print 'current_block_height:: %s' %current_block_height

# redis_conn.set('rajchain_block_count',current_block_height)


for i in range(int(redis_conn.get('rajchain_block_count')),int(current_block_height) + 1):#current_block_height + 1):
    insert_dict = {}
    print '----------------------------------- block number ----------------------------------------- %s' %i
    block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,i)
    block_info = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
    insert_dict['merkle'] = block_info['merkleroot']
    insert_dict['nonce'] = block_info['nonce']
    insert_dict['hash'] = block_info['hash']
    insert_dict['height'] = i
    insert_dict['difficulty'] = block_info['difficulty']
    if i is not 0:
        insert_dict['prev_block_hash'] = block_info['previousblockhash']
    if i is not current_block_height:
        insert_dict['next_block_hash'] = block_info['nextblockhash']
    insert_dict['confirmations'] = block_info['confirmations']
    insert_dict['size'] = block_info['size']
    insert_dict['no_of_tx'] = len(block_info['tx'])
    insert_dict['tx'] = block_info['tx']
    insert_dict['version'] = block_info['version']
    insert_dict['epoch'] = block_info['time']
    insert_dict['bits'] = int(block_info['bits'],16)
    output_total = 0
    if i is not 0:
        for transaction in block_info['tx']:
            tx_info = getrawtransaction(config.testnet['btc_prefix'],config.payload,str(transaction))
            print ':::::::::::::::::::::::::::::::::: transaction info :::::::::::::::::::::::::: %s' %tx_info
            vin = tx_info['vin']
            for tx_input in vin:
                if 'coinbase' in tx_input:
                    if 'addresses' in tx_info['vout'][0]['scriptPubKey']:
                        insert_dict['mining_reward_address'] = tx_info['vout'][0]['scriptPubKey']['addresses'][0]
                    else:
                        insert_dict['mining_reward_address'] = 'unparsed address'
                    insert_dict['mining_reward'] = int(tx_info['vout'][0]['value'])


            vout = tx_info['vout']
            for output_tx in vout:
                output_total += float(output_tx['value'])
        insert_dict['output_total'] = output_total
    else:
        insert_dict['mining_reward_address'] = 'NA'
        insert_dict['mining_reward'] = 'NA'
        insert_dict['output_total'] = 'NA'
    print '================================= block dict ===================================== %s' %insert_dict
    res = db_conn.block_details.insert(insert_dict)
    print res
