__author__ = 'ud'
import config
from wrap_core import *

db_conn = config.mongo_conn().explorer
redis_conn = config.redis_conn()

mempool_list = getRawMemPool(config.testnet['btc_prefix'],config.payload)
for transaction in mempool_list:
    transaction_detail = getrawtransaction(config.testnet['btc_prefix'],config.payload,transaction)
    insert_dict = {}
    vin_address = []
    vin_inputs = []
    input_scripts = []
    vout_address = []
    vout_outputs = []
    output_scripts = []
    print 'ttttt %s' %transaction_detail
    insert_dict['txid'] = transaction_detail['txid']
    insert_dict['blockhash'] = transaction_detail['blockhash']
    insert_dict['vin_address'] = vin_address
    insert_dict['vin_inputs'] = vin_inputs
    insert_dict['input_scripts'] = input_scripts
    insert_dict['vout_address'] = vout_address
    insert_dict['vout_outputs'] = vout_outputs
    insert_dict['output_scripts'] = output_scripts
    vin = transaction_detail['vin']
    vout = transaction_detail['vout']
    insert_dict['input_length'] = len(vin)
    insert_dict['output_length'] = len(vout)
    insert_dict['block_epoch'] = transaction_detail['blocktime']
    insert_dict['confirmations'] = transaction_detail['confirmations']
    insert_dict['size'] = transaction_detail['size']
    insert_dict['version'] = transaction_detail['version']

    for input_tx in vin:
        print 'iii %s' %input_tx
        if 'coinbase' in input_tx:
            insert_dict['coinbase'] = input_tx['coinbase']
            insert_dict['mining_flag'] = True
            if 'addresses' in transaction_detail['vout'][0]['scriptPubKey']:
                insert_dict['address'] = transaction_detail['vout'][0]['scriptPubKey']['addresses'][0]
                # insert_dict['output'] = vout[0]['value']
            else:
                insert_dict['address'] = 'Unparsed Address'
                # insert_dict['output'] = 'NA'
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
                        insert_dict['vin_address'] = vin_address
                        insert_dict['vin_inputs'] = vin_inputs
                    else:
                        vin_address.append('Unparsed Address')
                        vin_inputs.append('NA')
                        insert_dict['vin_address'] = vin_address
                        insert_dict['vin_inputs'] = vin_inputs
            input_transaction_info = getrawtransaction(config.testnet['btc_prefix'],
                    config.payload, input_tx['txid'])
            input_transaction_vout = input_transaction_info['vout']
            print 'qqqqqqqqqqqqqq %s' %insert_dict

    for outputs in vout:
        if 'addresses' in outputs['scriptPubKey']:
            vout_address.append(outputs['scriptPubKey']['addresses'][0])
            vout_outputs.append(float(outputs['value']))
        else:
            vout_address.append('Unparsed Address')
            vout_outputs.append('NA')
        output_scripts.append(outputs['scriptPubKey']['asm'])



    db_conn.mempool_transaction_details.insert(insert_dict)

    transaction_flag = db_conn.transaction_details.find_one({'txid':transaction_detail['txid']})
    if transaction_flag:
        db_conn.mempool_transaction_details.remove({'txid':transaction_detail['txid']})

