__author__ = 'udasi'
import config
from wrap_core import *
import time

db_conn = config.mongo_conn().explorer
redis_conn = config.redis_conn()

t_time = time.time()

class exec_time():
    def __init__(self):
        self.start_epoch = time.time()
    def get_duration(self):
        self.end_epoch = time.time()
        duration = self.end_epoch - self.start_epoch
        return duration

block_list = db_conn.block_details.find({"height": {"$ne": 0}}, no_cursor_timeout=True)
def address_crawler_1():
    for block in block_list:
        transactions_in_block = len(block['tx'])
        block_start_time = exec_time()
        for transaction in block['tx']:
            start_time = exec_time()
            transaction_details = getrawtransaction(config.testnet['btc_prefix'], config.payload, transaction)
            epoch = transaction_details['time']
            vout_details = transaction_details['vout']
            vin_details = transaction_details['vin']
            for vout in vout_details:
                if 'scriptPubKey' in vout:
                    if 'addresses' in vout['scriptPubKey']:
                        address = vout['scriptPubKey']['addresses'][0]
                        balance = vout['value']
                        index = vout['n']
                        vout_update_dict = {
                            'txid': transaction,
                            'balance': balance,
                            'index': index,
                            'spent': False,
                            'epoch': epoch
                        }
                        db_conn.address_details_v3.update({'address': address},
                                                          {"$push": {"txs": vout_update_dict}}, True)
            for vin in vin_details:
                if 'coinbase' in vin:
                    pass
                if 'txid' in vin:
                    vin_txid = vin['txid']
                    vin_index = vin['vout']
                    update_query = {
                        "txs.txid": vin_txid,
                        "txs.index": vin_index
                    }
                    update_params = {
                        'txs.$.spent': True,
                        'txs.$.spent_txid': transaction
                    }
                    db_conn.address_details_v3.update(update_query, {"$set": update_params})
            end_time = start_time.get_duration()
            print end_time
        block_end_time = block_start_time.get_duration()
        print 'time taken to crawl block: %s, with transactions: %s, is:::: %s' \
              %(block['height'],transactions_in_block,block_end_time)

address_crawler_1()
