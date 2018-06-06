__author__ = 'udasi'
_author_ = 'cryptoKTM
import config
from wrap_core import *

db_conn = config.mongo_conn().explorer
redis_conn = config.redis_conn()

transaction_results = db_conn.transaction_details.find({},no_cursor_timeout=True)


# def insert_address_in_redis():
#     for transaction in transaction_results:
#         if 'address' in transaction:
#             redis_conn.rpush('address_list',transaction['address'])
#         else:
#             for input_address in transaction['vin_address']:
#                 if len(input_address) > 0:
#                     redis_conn.rpush('address_list',input_address)
#             for output_address in transaction['vout_address']:
#                 if len(output_address) > 0:
#                     redis_conn.rpush('address_list',output_address)




# for address in redis_conn.lrange('address_list',0,-1):
#     print 'aaaa %s' %address
#     insert_dict = {}
#     out_tx_list = []
#     in_tx_list = []
#     insert_dict['address'] = address
#     for transaction in transaction_results:
#         print 'tttt %s' %transaction
#         if 'address' in transaction:
#             if address == transaction['address']:
#                 out_tx_list.append(transaction['txid'])
#         else:
#             if address in transaction['vin_address']:
#                 in_tx_list.append(transaction['txid'])
#             elif address in transaction['vout_address']:
#                 out_tx_list.append(transaction['txid'])
#     insert_dict['out_transaction'] = out_tx_list
#     insert_dict['in_transaction'] = in_tx_list
#     print 'iiii %s' %insert_dict
#     db_conn.address_details.insert(insert_dict)





# for transaction in transaction_results:
#     print 'ttt %s' %transaction
#     for address in redis_conn.lrange('address_list',0,-1):
#         insert_dict = {}
#         insert_dict['address'] = address
#         print 'aa %s' %address
#         if 'address' in transaction:
#             if address == transaction['address']:
#                 insert_dict['output_transaction'] = transaction['txid']
#                 insert_dict['newly_generated_coins'] = True
#                 db_conn.address_details.insert(insert_dict)
#         else:
#             if address in transaction['vin_address']:
#                 insert_dict['input_transaction'] = transaction['txid']
#                 db_conn.address_details.insert(insert_dict)
#             elif address in transaction['vout_address']:
#                 insert_dict['output_address'] = transaction['txid']
#                 db_conn.address_details.insert(insert_dict)


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


for transaction in transaction_results:
    txid = transaction['txid']
    address_list = get_address(transaction)
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



