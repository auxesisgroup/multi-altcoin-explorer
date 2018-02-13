__author__ = 'udasi'
import config
from wrap_core import *
import time
import logging
import datetime
import sys

# db_conn = config.mongo_conn().explorer
redis_conn = config.redis_conn()

str_date = datetime.datetime.now().strftime('%Y%m%d')
logger = config.logger
_file = logger['mempool']['path'] + 'rajchain_latest_transactions_%s' % str_date
logging.basicConfig(filename=_file,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
_logging = logging.getLogger('explorer')
_logging.addHandler(logging.StreamHandler(sys.stdout))
mongo_conn = config.mongo_conn()
db_conn = mongo_conn.rajchain_explorer


def insert_transactions_in_redis():
    start_time = int(time.time())
    logging.info('script started at::: %s' %start_time)
    print redis_conn.exists('raj_key')
    if redis_conn.exists('raj_key') is not True:
        redis_conn.set('raj_key',True)
        # redis_conn.set('rajchain_assets_count',len(custom_rpc('listassets')))
        # print 'tyty %s' %custom_rpc('liststreams')
        # redis_conn.set('rajchain_streams_count',len(custom_rpc('liststreams')))
        run_flag = True
        while run_flag is True:
            end_time = int(time.time())
            if end_time - start_time >= 60:
                logging.info('ending script')
                run_flag = False
            latest_transactions_list = custom_rpc('getrawmempool')
            logging.info('latest_mempool_list is::: %s, length is:: %s' %(latest_transactions_list,len(latest_transactions_list)))
            redis_conn.set('rajchain_block_count',custom_rpc('getinfo')['blocks'])
            for latest_transaction in latest_transactions_list:
                if redis_conn.sismember('rajchain_latest_transactions_set',latest_transaction):
                    print 'aaa'
                    logging.info('transactions ::: %s, already exists. Not adding' %latest_transaction)
                else:
                    redis_conn.sadd('rajchain_latest_transactions_set',latest_transaction)
                    print 'bbb'
                    insert_dict1 = {}
                    insert_dict1['block_count'] = custom_rpc('getinfo')['blocks']
                    insert_dict1['transaction'] = latest_transaction
                    # insert_dict1['types'] = get_types(latest_transaction)
                    logging.info('inserting transaction:: %s in mongo' %latest_transaction)
                    db_conn.transaction_details.insert(insert_dict1)
            print 'sleeping for 8 secs'
            time.sleep(8)
        mongo_conn.close()
        redis_conn.delete('raj_key')


# def get_types(transaction):
#     transaction_details = custom_rpc('getrawtransaction',[transaction,1])
#     type_list = []
#     if transaction_details:
#         vout_details = transaction_details['vout']
#         for vout in vout_details:
#             if len(vout['assets']) > 0:
#                 if not 'Asset' in type_list:
#                     type_list.append('Asset')
#             elif len(vout['permissions']) > 0:
#                 if not 'Permission' in type_list:
#                     type_list.append('Permission')
#             elif len(vout['items']) > 0:
#                 if not 'items' in type_list:
#                     type_list.append('Item')
#     return type_list

insert_transactions_in_redis()
