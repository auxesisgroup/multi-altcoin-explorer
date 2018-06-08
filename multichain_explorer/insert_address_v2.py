__author__ = 'udasi'

import config
from wrap_core import *

db_conn = config.mongo_conn().explorer
redis_conn = config.redis_conn()

block_list = db_conn.block_details.find({"height": {"$ne": 0,"$lte":4110}}, no_cursor_timeout=True)

for block in block_list:
    transaction_list = block['tx']
    vin_list = []
    vout_list = []
    for transaction in transaction_list:
        transaction_details = getrawtransaction(config.testnet['btc_prefix'], config.payload, transaction)
        vout_details = transaction_details['vout']
        vin_details = transaction_details['vin']
        for vout in vout_details:
            if 'scriptPubKey' in vout:
                if 'addresses' in vout['scriptPubKey']:
                    address = vout['scriptPubKey']['addresses'][0]
                    balance = vout['value']
                    index = vout['n']
                    push_str = '%s,%s,%s' % (transaction, balance, index)
                    # res = db_conn.address_details_v2.find_one({'address': address})
                    # if res:
                    # new_balance = res['balance'] + balance
                    # else:
                    #     new_balance = balance
                    # print '----- updating vout_list of address %s, appending transaction:: %s, new balance:: %s' % (
                        # address, transaction, new_balance)
                    # db_conn.address_details_v2.update({'address': address},
                    #                                {"$push": {"vout_list": transaction},
                    #                                 "$set": {'balance': new_balance}},upsert=True)
                    print 'updating vout_list::: %s' %push_str
                    db_conn.address_details_v2.update({'address': address}, {"$push": {"vout_list": push_str}},
                                                      upsert=True)
                    unspent_tx_flag = db_conn.unspent_tx.find_one({'tx': transaction})
                    if not unspent_tx_flag:
                        print 'adding transaction to unspent::::: %s' % transaction
                        db_conn.unspent_tx.insert({'tx': transaction})
        for vin in vin_details:
            if 'txid' in vin:
                vin_txid = vin['txid']
                vin_n = vin['vout']
                vin_res = db_conn.unspent_tx.find_one({'tx': vin_txid})
                if vin_res:
                    if vin_txid in vin_res['tx']:
                        vin_transaction_details = getrawtransaction(config.testnet['btc_prefix'], config.payload,
                                                                    vin_txid)
                        vin_outputs = vin_transaction_details['vout']
                        for inner_vout in vin_outputs:
                            balance = inner_vout['value']
                            index = inner_vout['n']
                            vin_push_str = '%s,%s,%s' %(vin_txid,balance,index)
                            if inner_vout.__contains__('scriptPubKey'):
                                if 'addresses' in inner_vout['scriptPubKey']:
                                    inner_address = inner_vout['scriptPubKey']['addresses']






                                    #     inner_address, vin_txid, new_balance)
                                    # db_conn.address_details_v2.update({'address': inner_address},

                                    #                                 "$set": {"balance": balance}},upsert=True)
                                    print 'updating vin list:::::: %s' %vin_push_str
                                    db_conn.address_details_v2.find_and_modify(
                                        query={'address': inner_address},
                                        update={"$push": {'vin_list': vin_push_str}},
                                        upsert=True
                                    )
                            print '------ removing transaction:: %s from unspent_tx ----' % vin_txid
                            db_conn.unspent_tx.remove({'tx': vin_txid})



#commented out
