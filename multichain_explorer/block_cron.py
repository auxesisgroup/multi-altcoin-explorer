__author__ = 'udasi'

import config
from models import *
from wrap_core import *

db_conn = config.mongo_conn().explorer
redis_conn = config.redis_conn()


crawled_block_height = int(redis_conn.get('current_block_height'))
current_block_height = getblockcount(config.testnet['btc_prefix'],config.payload)


def crawl_new_blocks():
    if crawled_block_height == current_block_height:
        print 'no new blocks'
        pass
    else:
        #   ----------- update previous blocks next_block_hash ------------
        latest_nextblock_height = latest_nextblock_height_model()
        for i in range(latest_nextblock_height,crawled_block_height + 1):
            block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,i)
            block_info = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
            if 'nextblockhash' in block_info:
                response = update_nextblockhash(i,block_info['nextblockhash'])
                print '====== nextblockhash update response ======== %s' %response
            else:
                pass

        # for i in range()


        blocks_to_crawl = current_block_height - crawled_block_height
        print blocks_to_crawl
        redis_conn.set('current_block_height',current_block_height)
        for i in range(crawled_block_height + 1,current_block_height + 1):#current_block_height + 1):
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
            if 'nextblockhash' in block_info:
                insert_dict['next_block_hash'] = block_info['nextblockhash']
            # todo crawl mempool
            insert_dict['confirmations'] = block_info['confirmations']
            insert_dict['size'] = block_info['size']
            insert_dict['no_of_tx'] = len(block_info['tx'])
            insert_dict['tx'] = block_info['tx']
            insert_dict['version'] = block_info['version']
            insert_dict['epoch'] = block_info['time']
            insert_dict['bits'] = int(block_info['bits'],16)
            insert_dict['no_of_tx'] = get_transaction_info_model()
            output_total = 0
            if i is not 0:
                for transaction in block_info['tx']:
                    tx_info = getrawtransaction(config.testnet['btc_prefix'],config.payload,str(transaction))
                    # print ':::::::::::::::::::::::::::::::::: transaction info :::::::::::::::::::::::::: %s' %tx_info
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


            # update transactions
            for tx in insert_dict['tx']:
                update_transaction(tx)


def update_transaction(tx):
    print '=================== transaction : %s ====================' %tx
    insert_dict_1 = {}
    vin_address = []
    vin_inputs = []
    input_scripts = []
    vout_address = []
    vout_outputs = []
    output_scripts = []

    transaction_detail = getrawtransaction(config.testnet['btc_prefix'],
                          config.payload, tx)
    print 'ttttt %s' %transaction_detail
    insert_dict_1['txid'] = transaction_detail['txid']
    insert_dict_1['blockhash'] = transaction_detail['blockhash']
    insert_dict_1['vin_address'] = vin_address
    insert_dict_1['vin_inputs'] = vin_inputs
    insert_dict_1['input_scripts'] = input_scripts
    insert_dict_1['vout_address'] = vout_address
    insert_dict_1['vout_outputs'] = vout_outputs
    insert_dict_1['output_scripts'] = output_scripts
    vin = transaction_detail['vin']
    vout = transaction_detail['vout']
    insert_dict_1['input_length'] = len(vin)
    insert_dict_1['output_length'] = len(vout)
    insert_dict_1['block_epoch'] = transaction_detail['blocktime']
    insert_dict_1['confirmations'] = transaction_detail['confirmations']
    insert_dict_1['size'] = transaction_detail['size']
    insert_dict_1['version'] = transaction_detail['version']

    for input_tx in vin:
        print 'iii %s' %input_tx
        if 'coinbase' in input_tx:
            insert_dict_1['coinbase'] = input_tx['coinbase']
            insert_dict_1['mining_flag'] = True
            if 'addresses' in transaction_detail['vout'][0]['scriptPubKey']:
                insert_dict_1['address'] = transaction_detail['vout'][0]['scriptPubKey']['addresses'][0]
                # insert_dict_1['output'] = vout[0]['value']
            else:
                insert_dict_1['address'] = 'Unparsed Address'
                # insert_dict_1['output'] = 'NA'
        else:
            input_scripts.append(input_tx['scriptSig']['asm'])
            vin_transaction_info = getrawtransaction(config.testnet['btc_prefix'],config.payload,input_tx['txid'])
            sequence = input_tx['vout']
            vout_of_input = vin_transaction_info['vout']
            for transaction in vout_of_input:
                n = transaction['n']
                if n != sequence:
                    pass
                else:
                    print '!!!!!!!!!!!!!!!! inner transaction: %s !!!!!!!!!!!!!!!!' %transaction
                    if 'addresses' in transaction['scriptPubKey']:
                        vin_address.append(transaction['scriptPubKey']['addresses'][0])
                        vin_inputs.append(float(transaction['value']))
                        insert_dict_1['vin_address'] = vin_address
                        insert_dict_1['vin_inputs'] = vin_inputs
                    else:
                        vin_address.append('Unparsed Address')
                        vin_inputs.append('NA')
                        insert_dict_1['vin_address'] = vin_address
                        insert_dict_1['vin_inputs'] = vin_inputs
            input_transaction_info = getrawtransaction(config.testnet['btc_prefix'],
                    config.payload, input_tx['txid'])
            input_transaction_vout = input_transaction_info['vout']
            print 'qqqqqqqqqqqqqq %s' %insert_dict_1

    for outputs in vout:
        if 'addresses' in outputs['scriptPubKey']:
            vout_address.append(outputs['scriptPubKey']['addresses'][0])
            vout_outputs.append(float(outputs['value']))
        else:
            vout_address.append('Unparsed Address')
            vout_outputs.append('NA')
        output_scripts.append(outputs['scriptPubKey']['asm'])

    for transaction in transaction_detail:
        update_address(transaction)


def update_address(transaction):
    address_list = get_address(transaction)
    txid = transaction['txid']
    print '----------- address list: %s ---------------' %address_list
    for address in address_list:
        print '========= address: %s ==============' %address
        if address == 'Unparsed Address':
            pass
        else:
            match_dict = {'address':address}
            if 'address' in transaction:
                update_dict = {}
                update_dict['mined_transactions'] = txid
                update_dict['mined_tx_epoch'] = transaction['block_epoch']
                update_dict['mined_output_values'] = transaction['vout_outputs'][0]
                db_conn.address_details.update(match_dict,{'$push':update_dict},upsert=True)
            else:
                if address in transaction['vin_address']:
                    update_dict = {}
                    update_dict['vin_transactions'] = txid
                    update_dict['vin_tx_epoch'] = transaction['block_epoch']
                    update_dict['vin_input_values'] = transaction['vin_inputs'][transaction['vin_address'].index(address)]
                    db_conn.address_details.update(match_dict,{'$push':update_dict},upsert=True)
                if address in transaction['vout_address']:
                    update_dict = {}
                    update_dict['vout_transactions'] = txid
                    update_dict['vout_tx_epoch'] = transaction['block_epoch']
                    update_dict['vout_output_values'] = transaction['vout_outputs'][transaction['vout_address'].index(address)]
                    db_conn.address_details.update(match_dict,{'$push':update_dict},upsert=True)



def get_address(tx):
    address_list = []
    if 'address' in tx:
        address_list.append(tx['address'])
    else:
        for address in tx['vin_address']:
            address_list.append(address)
        for address in tx['vout_address']:
            address_list.append(address)
    return address_list

crawl_new_blocks()
