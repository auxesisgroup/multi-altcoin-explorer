__author__ = 'udasi'
import config
from wrap_core import *
import time
import logging
import datetime
import sys

db_conn = config.mongo_conn().rajchain_explorer
redis_conn = config.redis_conn()

str_date = datetime.datetime.now().strftime('%Y%m%d')
logger = config.logger
_file = logger['path'] + 'multichain_addressv4_%s' % str_date
logging.basicConfig(filename=_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
_logging = logging.getLogger('explorer')
_logging.addHandler(logging.StreamHandler(sys.stdout))


class exec_time():
    def __init__(self):
        self.start_epoch = time.time()

    def get_duration(self):
        self.end_epoch = time.time()
        duration = self.end_epoch - self.start_epoch
        return duration


# current_block_height = getblockcount(config.testnet['btc_prefix'], config.payload)
current_block_height = custom_rpc('getblockcount')
# print current_block_height
logging.info('crawling blocks upto height:::: %s' % current_block_height)
set_current_block_height_in_redis = redis_conn.set('multichain_current_block_height', current_block_height)
if set_current_block_height_in_redis is True:
    logging.info('setting current blockheight in redis::: %s' % set_current_block_height_in_redis)
else:
    logging.info('setting current blockheight in redis failed' % set_current_block_height_in_redis)

crawled_block_height = int(redis_conn.get('masschain_crawled_block_height'))
logging.info('blocks crawled upto height::: %s' % crawled_block_height)


def get_txs(block_height):
    # block_hash = getblockhash(config.testnet['btc_prefix'], config.payload, block_height)
    # block_details = getblock(config.testnet['btc_prefix'], config.payload, block_hash)
    block_hash = custom_rpc('getblockhash',[block_height])
    block_details = custom_rpc('getblock',[block_hash])
    transactions_list = block_details['tx']
    logging.info('crawling block height:: %s, with transactions length:: %s, and transactions:: %s' % (
        block_height, len(transactions_list), transactions_list))
    return transactions_list


def address_crawler_1():
    for block_height in xrange(crawled_block_height, current_block_height + 1):
        block_start_time = exec_time()
        redis_conn.set('masschain_crawled_block_height', block_height)
        logging.debug('crawling block :: %s', block_height)
        transaction_list = get_txs(str(block_height))
        for transaction in transaction_list:
            logging.info('crawling transaction:: %s' % transaction)

            start_time = exec_time()
            # transaction_details = getrawtransaction(config.testnet['btc_prefix'], config.payload, transaction)
            transaction_details = custom_rpc('getrawtransaction',[transaction,1])
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
                        exists_flag = db_conn.address_details_v3.find_one({"txs":{"$elemMatch":{"eq":vout_update_dict}}})
                        # if exists_flag:
                        # print '1111111111111111111111111 %s' %exists_flag
                        if not exists_flag:
                            vout_update_result = db_conn.address_details_v3.update({'address': address},
                                                                                   {"$push": {"txs": vout_update_dict}},
                                                                                   True)
                            logging.info('updated vout of address:: %s, inserted vout_dict:: %s, result is:: %s' % (
                            address, vout_update_dict, vout_update_result))
                        else:
                            logging.info('not updating vout of address:: %s, not inserted vout_dict:: %s' % (
                            address, vout_update_dict))
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
                    vin_update_result = db_conn.address_details_v3.update(update_query, {"$set": update_params})
                    logging.info('updated vin matching params:: %s, updating params:: %s, result is:: %s' % (
                                update_query, update_params, vin_update_result))
            end_time = start_time.get_duration()
            logging.debug('time taken for transaction:: %s is:: %s' % (transaction, end_time))
        block_end_time = block_start_time.get_duration()
        print 'time taken to crawl block: %s, with transactions: %s, is:::: %s' \
              % (block_height, len(transaction_list), block_end_time)
        logging.debug('time taken to crawl block: %s, with transactions: %s, is:::: %s' \
                      % (block_height, len(transaction_list), block_end_time))


address_crawler_1()