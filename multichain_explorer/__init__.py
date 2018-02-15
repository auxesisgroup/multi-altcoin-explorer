__author__ = 'U.D.'

from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
# from flask_socketio import SocketIO,emit


import logging
import sys
import json
import uuid
import hashlib
import random
import requests
import time


import config
from wrap_core import *
from models import *
# from mailin import Mailin


app = Flask(__name__, template_folder='templates')
CORS(app)
# socketIo = SocketIO(app)
redis_conn = config.redis_conn()

# logger = config.logger
# _file = logger['path'] + logger['filename']
# logging.basicConfig(filename=_file,
#                 filemode='a',
#                 format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                 datefmt='%H:%M:%S',
#                 level=logging.DEBUG)
# _logging = logging.getLogger('explorer')
# _logging.addHandler(logging.StreamHandler(sys.stdout))
staging = config.staging

base_address_url = 'http://67.205.166.57/get_key/explorer?token=abcd1234&notify_count=1'
forward_btc_url = 'http://67.205.166.57/forward_btc'

@app.route('/')
def hello_world():
    # _logging.info('!!!!!!!!!!!!!!!!!!!!!')
    print '------ rendering rajchain index page ---'
    chain_details = db_conn.chain_details.find_one({})
    res = {}
    # block_count = custom_rpc('getinfo')['blocks']
    # assets_count = len(custom_rpc('listassets'))
    # stream_count = len(custom_rpc('liststreams'))
    res['block_count'] = redis_conn.get('rajchain_block_count')
    res['assets_count'] = redis_conn.get('rajchain_assets_count')
    res['stream_count'] = redis_conn.get('rajchain_streams_count')
    print 'lll %s' %res['block_count']
    return render_template('index.html',context=res)

# @app.route('/re/',methods=['GET'])
# def re():
#     print '............ redirecting .............. %s' %request.query_string

"""  -----------------------------------------  EXPLORER MAIN APIs ------------------------------------------- """
@app.route('/explorer/get_block_hash/<height>',methods=['GET'])
def get_block_hash(height):
    print '--------- getting block hash ---------'
    print '--------- getting block hash ---------'
        # block_details = get_block_hash_model(height)
    # block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,height)
    # res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
    if int(height) == 0:
        return render_template('block.html',context={'height':height,'no_data':True})
    res1 = custom_rpc('getblockhash',[int(height)])
    res = custom_rpc('getblock',[res1])
    if res:
        res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
        res['no_of_tx'] = len(res['tx'])
        res['output_total'] = get_output_total(res['tx'])
        print 'sss %s' %res
        return render_template('block.html',context=res)
    else:
        return render_template('block.html',context={'height':height,'no_data':True})




@app.route('/explorer/get_block_info/<block_hash>',methods=['GET'])
def get_block_info(block_hash):
    print '--------- getting block info ---------'
    print '--------- getting block hash ---------'
        # block_details = get_block_hash_model(height)
    # block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,height)
    # res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
    res = custom_rpc('getblock',[block_hash])
    if res:
        res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
        res['no_of_tx'] = len(res['tx'])
        res['output_total'] = get_output_total(res['tx'])
        print 'sss %s' %res
        return render_template('block.html',context=res)
    else:
        return render_template('block.html',context={'hash':block_hash,'no_data':True})


@app.route('/explorer/get_transaction_info/<txid>',methods=['GET'])
def get_transaction_info(txid):
    print '--------- getting transaction info ---------'
    print '--------- getting transaction info ---------'
    transaction_details = get_transaction_details(txid)
    if transaction_details == 'no_such_tx':
        return render_template('transaction.html',context={'txid':txid,'no_data':True})
    return render_template('transaction.html',context=transaction_details)

@app.route('/explorer/get_address_info/<address>',methods=['GET'])
def get_address_info(address):
    print '--------- getting address info ---------'
    address_details = get_address_info_model(address)
    if address_details:
        transaction_list_to_send = []
        data_to_send = {}
        print 'transactions are::: %s' %address_details['txs']
        transactions_list = address_details['txs']
        # transactions_count = 0
        balance = 0.0
        total_output = 0.0
        for transaction in transactions_list:
            if transaction['spent'] is False and transaction['txid'] not in transaction_list_to_send:
                balance += transaction['balance']
                # transactions_count += 1
            if transaction['txid'] not in transaction_list_to_send:
                total_output += transaction['balance']
                transaction_list_to_send.append(transaction['txid'])
                # transactions_count += 1
            if 'spent_txid' in transaction:
                if transaction['spent_txid'] not in transaction_list_to_send:
                    transaction_list_to_send.append(transaction['spent_txid'])
                    # transactions_count += 1

        data_to_send['balance'] = balance
        data_to_send['total_output'] = total_output
        # data_to_send['transactions_count'] = transactions_count
        data_to_send['address'] = address_details['address']
        data_to_send['transaction_list_to_send'] = transaction_list_to_send
        data_to_send['transactions_count'] = len(transaction_list_to_send)
        return render_template('address.html',context=data_to_send)
    else:
        return render_template('address.html',context={'address':address,'no_data':True})





@app.route('/explorer/get_latest_transactions/',methods=['GET'])
def get_latest_transactions():
    print '------- getting latest transactions -----------'
    print '------- getting latest transactions -----------'
    redis_conn.setex('transaction_mutex_key',60,'true')
    transactions_list = db_conn.transaction_details.find({}).sort('_id',-1).limit(20)
    list_to_return = []
    for transaction in transactions_list:
        print 'transaction is::: %s' %transaction
        transaction_dict = {}
        transaction_dict['transaction'] = transaction['transaction']
        current_block_count = redis_conn.get('rajchain_block_count')
        confirmations = int(current_block_count) - int(transaction['block_count'])
        if confirmations == 0:
            transaction_dict['confirmations'] = 'Mempool'
        else:
            transaction_dict['confirmations'] = confirmations
        if confirmations > 2:
            redis_conn.srem('latest_transactions_set',transaction)
        # transaction_dict['types'] = transaction['types']
        transaction_dict['current_block_count'] = current_block_count
        list_to_return.append(transaction_dict)
    return json.dumps(list_to_return)








"""  -----------------------------------------  EXPLORER Endpoints ------------------------------------------- """
@app.route('/api_get_block_hash/<height>',methods=['GET'])
def api_get_block_hash(height):
    print '--------- getting block hash API---------'
    print '--------- getting block hash ---------'
        # block_details = get_block_hash_model(height)
    block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,height)
    res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
    if res:
        res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
        res['no_of_tx'] = len(res['tx'])
        res['output_total'] = get_output_total(res['tx'])
        print 'sss %s' %res
        return jsonify(res)
    else:
        return 'no_block_available'

@app.route('/api_get_block_info/<block_hash>',methods=['GET'])
def api_get_block_info(block_hash):
    print '--------- getting block info API---------'
    print '--------- getting block hash ---------'
        # block_details = get_block_hash_model(height)
    # block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,height)
    res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
    if res:
        res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
        res['no_of_tx'] = len(res['tx'])
        res['output_total'] = get_output_total(res['tx'])
        print 'sss %s' %res
        return jsonify(res)
    else:
        return 'no_block_available'


@app.route('/api_get_transaction_info/<txid>',methods=['GET'])
def api_get_transaction_info(txid):
    print '--------- getting transaction info ---------'
    print '--------- getting transaction info ---------'
    transaction_details = get_transaction_details(txid)
    if transaction_details == 'no_such_tx':
        return render_template('transaction.html',context={'txid':txid,'no_data':True})
    return jsonify(transaction_details)


@app.route('/api_get_address_info/<address>',methods=['GET'])
def api_get_address_info(address):
    print '--------- getting address info API---------'
    address_details = get_address_info_model(address)
    if address_details:
            transaction_list_to_send = []
            data_to_send = {}
            print 'transactions are::: %s' %address_details['txs']
            transactions_list = address_details['txs']
            # transactions_count = len(transactions_list)
            balance = 0.0
            total_output = 0.0
            for transaction in transactions_list:
                if transaction['spent'] is False and transaction['txid'] not in transaction_list_to_send:
                    balance += transaction['balance']
                if transaction['txid'] not in transaction_list_to_send:
                    total_output += transaction['balance']
                    transaction_list_to_send.append(transaction['txid'])
                if 'spent_txid' in transaction:
                    if transaction['spent_txid'] not in transaction_list_to_send:
                        transaction_list_to_send.append(transaction['spent_txid'])
                        # transactions_count += 1

            data_to_send['balance'] = balance
            data_to_send['total_output'] = total_output
            # data_to_send['transactions_count'] = transactions_count
            data_to_send['address'] = address_details['address']
            data_to_send['transaction_list_to_send'] = transaction_list_to_send
            data_to_send['transactions_count'] = len(transaction_list_to_send)
            return jsonify(data_to_send)
    else:
        return 'no such address'
























if staging is False:       # For local
    @app.route('/explorer/',methods=['GET'])
    def explorer():
        # _logging.info('!!!!!!!!!!!!!!!!!!!!!')
        print '------ rendering rajchain index page ---'
        res = {}
        block_count = custom_rpc('getinfo')['blocks']
        assets_count = len(custom_rpc('listassets'))
        stream_count = len(custom_rpc('liststreams'))
        res['block_count'] = block_count
        res['assets_count'] = assets_count
        res['stream_count'] = stream_count
        print 'lll %s' %block_count
        return render_template('index.html',context=res)

    """  -----------------------------------------  EXPLORER MAIN APIs ------------------------------------------- """
    @app.route('/explorer/get_block_hash/<height>',methods=['GET'])
    def local_get_block_hash(height):
        print '--------- getting block hash ---------'
        # block_details = get_block_hash_model(height)
        # block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,height)
        # res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
        res = custom_rpc('getblock',[height])
        if res:
            res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
            res['no_of_tx'] = len(res['tx'])
            res['output_total'] = get_output_total(res['tx'])
            print 'sss %s' %res
            return render_template('block.html',context=res)
        else:
            return render_template('block.html',context={'height':height,'no_data':True})


    @app.route('/explorer/get_block_info/<block_hash>',methods=['GET'])
    def local_get_block_info(block_hash):
        print '--------- getting block info ---------'
        # res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
        res = custom_rpc('getblock',[block_hash])
        if res:
            res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
            res['no_of_tx'] = len(res['tx'])
            res['output_total'] = get_output_total(res['tx'])
            print 'sss %s' %res
            return render_template('block.html',context=res)
        else:
            return render_template('block.html',context={'hash':block_hash,'no_data':True})



    @app.route('/explorer/get_transaction_info/<txid>',methods=['GET'])
    def local_get_transaction_info(txid):
        print '--------- getting transaction info ---------'
        transaction_details = get_transaction_details(txid)
        if transaction_details == 'no_such_tx':
            return render_template('transaction.html',context={'txid':txid,'no_data':True})
        return render_template('transaction.html',context=transaction_details)


    @app.route('/explorer/get_address_info/<address>',methods=['GET'])
    def local_get_address_info(address):
        print '--------- getting address info in local rendering ---------'
        address_details = get_address_info_model(address)
        if address_details:
            transaction_list_to_send = []
            data_to_send = {}
            print 'transactions are::: %s' %address_details['txs']
            transactions_list = address_details['txs']
            # transactions_count = 0
            balance = 0.0
            total_output = 0.0
            for transaction in transactions_list:
                if transaction['spent'] is False and transaction['txid'] not in transaction_list_to_send:
                    balance += transaction['balance']
                    # transactions_count += 1
                if transaction['txid'] not in transaction_list_to_send:
                    total_output += transaction['balance']
                    transaction_list_to_send.append(transaction['txid'])
                    # transactions_count += 1
                if 'spent_txid' in transaction:
                    if transaction['spent_txid'] not in transaction_list_to_send:
                        transaction_list_to_send.append(transaction['spent_txid'])
                        # transactions_count += 1

            data_to_send['balance'] = balance
            data_to_send['total_output'] = total_output
            # data_to_send['transactions_count'] = transactions_count
            data_to_send['address'] = address_details['address']
            data_to_send['transaction_list_to_send'] = transaction_list_to_send
            data_to_send['transactions_count'] = len(transaction_list_to_send)
            return render_template('address.html',context=data_to_send)
        else:
            return render_template('address.html',context={'address':address,'no_data':True})






    @app.route('/explorer/get_latest_transactions/',methods=['GET'])
    def local_get_latest_transactions():
        print '------- getting latest transactions -----------'
        transactions_list = db_conn.transaction_details.find({}).sort('_id',-1).limit(20)
        list_to_return = []
        for transaction in transactions_list:
            print 'transaction is::: %s' %transaction
            transaction_dict = {}
            transaction_dict['transaction'] = transaction['transaction']
            current_block_count = redis_conn.get('rajchain_block_count')
            confirmations = int(current_block_count) - int(transaction['block_count'])
            if confirmations == 0:
                transaction_dict['confirmations'] = 'Mempool'
            else:
                transaction_dict['confirmations'] = confirmations
            # transaction_dict['types'] = transaction['types']
            transaction_dict['current_block_count'] = current_block_count
            list_to_return.append(transaction_dict)
        return json.dumps(list_to_return)






    """  -----------------------------------------  EXPLORER Endpoints ------------------------------------------- """
    @app.route('/explorer/api_get_block_hash/<height>',methods=['GET'])
    def local_api_get_block_hash(height):
        print '--------- getting block hash API---------'
        print '--------- getting block hash ---------'
        # block_details = get_block_hash_model(height)
        # block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,height)
        # res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
        res = custom_rpc('getblock',height)
        if res:
            res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
            res['no_of_tx'] = len(res['tx'])
            res['output_total'] = get_output_total(res['tx'])
            print 'sss %s' %res
            return jsonify(res)
        else:
            return 'no_block_available'

    @app.route('/explorer/api_get_block_info/<block_hash>',methods=['GET'])
    def local_api_get_block_info(block_hash):
        print '--------- getting block info API---------'
        # block_details = get_block_info_model(block_hash)
        print '--------- getting block hash ---------'
        # block_details = get_block_hash_model(height)
        # block_hash = getblockhash(config.testnet['btc_prefix'],config.payload,height)
        res = getblock(config.testnet['btc_prefix'],config.payload,block_hash)
        if res:
            res['block_time'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(res['time']))
            res['no_of_tx'] = len(res['tx'])
            res['output_total'] = get_output_total(res['tx'])
            print 'sss %s' %res
            return jsonify(res)
        else:
            return 'no_block_available'


    @app.route('/explorer/api_get_transaction_info/<txid>',methods=['GET'])
    def local_api_get_transaction_info(txid):
        print '--------- getting transaction info using new API ---------'
        print '--------- getting transaction info ---------'
        transaction_details = get_transaction_details(txid)
        if transaction_details == 'no_such_tx':
            return 'no_such_tx'
        return jsonify(transaction_details)


    @app.route('/explorer/api_get_address_info/<address>',methods=['GET'])
    def local_api_get_address_info(address):
        print '--------- getting address info API---------'
        address_details = get_address_info_model(address)
        if address_details:
            transaction_list_to_send = []
            data_to_send = {}
            print 'transactions are::: %s' %address_details['txs']
            transactions_list = address_details['txs']
            # transactions_count = len(transactions_list)
            balance = 0.0
            total_output = 0.0
            for transaction in transactions_list:
                if transaction['spent'] is False and transaction['txid'] not in transaction_list_to_send:
                    balance += transaction['balance']
                if transaction['txid'] not in transaction_list_to_send:
                    total_output += transaction['balance']
                    transaction_list_to_send.append(transaction['txid'])
                if 'spent_txid' in transaction:
                    if transaction['spent_txid'] not in transaction_list_to_send:
                        transaction_list_to_send.append(transaction['spent_txid'])
                        # transactions_count += 1

            data_to_send['balance'] = balance
            data_to_send['total_output'] = total_output
            # data_to_send['transactions_count'] = transactions_count
            data_to_send['address'] = address_details['address']
            data_to_send['transaction_list_to_send'] = transaction_list_to_send
            data_to_send['transactions_count'] = len(transaction_list_to_send)
            return jsonify(data_to_send)
        else:
            return 'no such address'



def get_transaction_details(txid):
    # transaction_detail = getrawtransaction(config.testnet['btc_prefix'],config.payload,txid)
    transaction_detail = custom_rpc('getrawtransaction',[txid,1])
    print 'ttttt %s' %transaction_detail
    if transaction_detail is None:
        return 'no_such_tx'
    print 'tetetetetet %s' %transaction_detail
    insert_dict = {}
    vin_address = []
    vin_inputs = []
    input_scripts = []
    vout_address = []
    vout_outputs = []
    output_scripts = []

    # transaction_detail = getrawtransaction(config.testnet['btc_prefix'],
    #                       config.payload, tx)
    print 'ttttt %s' %transaction_detail
    insert_dict['txid'] = transaction_detail['txid']
    if 'blockhash' in transaction_detail:
        insert_dict['blockhash'] = transaction_detail['blockhash']
        insert_dict['block_number'] = custom_rpc('getblock',[insert_dict['blockhash']])['height']
    insert_dict['vin_address'] = vin_address
    insert_dict['vin_inputs'] = vin_inputs
    insert_dict['input_scripts'] = input_scripts
    insert_dict['vout_address'] = vout_address
    insert_dict['vout_outputs'] = vout_outputs
    insert_dict['output_scripts'] = output_scripts
    vin = transaction_detail['vin']
    vout = transaction_detail['vout']
    insert_dict['total_inputs_count'] = len(vin)
    insert_dict['total_outputs_count'] = len(vout)
    insert_dict['input_length'] = len(vin)
    insert_dict['output_length'] = len(vout)
    if 'blocktime' in transaction_detail:
        insert_dict['block_epoch'] = transaction_detail['blocktime']
    if 'confirmations' in transaction_detail:
        insert_dict['confirmations'] = transaction_detail['confirmations']
    else:
        insert_dict['confirmations'] = 0
    # insert_dict['size'] = transaction_detail['size']
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
            # vin_transaction_info = getrawtransaction(config.testnet['btc_prefix'],config.payload,input_tx['txid'])
            vin_transaction_info = custom_rpc('getrawtransaction',[input_tx['txid'],1])
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
            # input_transaction_info = getrawtransaction(config.testnet['btc_prefix'],
            #         config.payload, input_tx['txid'])
            input_transaction_info = custom_rpc('getrawtransaction',[input_tx['txid'],1])
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

    print 'transaction details v2::: %s' %insert_dict
    transaction_details = insert_dict
    if transaction_details:
        if 'block_epoch' in transaction_details:
            block_epoch = transaction_details['block_epoch']
            block_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(block_epoch))
            transaction_details['block_time'] = block_time
        total_input = 0.0
        total_output = 0.0
        for inputs in transaction_details['vin_inputs']:
            total_input += float(inputs)
        for outputs in transaction_details['vout_outputs']:
            if outputs != 'NA':
                total_output += float(outputs)
        transaction_fee = total_input - total_output
        # fee_per_byte = transaction_fee/float(transaction_details['size'])
        transaction_details['total_inputs'] = total_input
        transaction_details['total_outputs'] = total_output
        transaction_details['fee'] = transaction_fee
        if transaction_fee < 0:
            transaction_details['fee'] = 0.0
        # transaction_details['fee_per_byte'] = fee_per_byte
        print 'tt %s' %transaction_details
        vin_list_details = []
        vout_list_details = []
        for i in range(0,len(vin_inputs)):
            vin_list_details.append({'vin_address':vin_address[i],'vin_input':vin_inputs[i]})
        for i in range(0,len(vout_outputs)):
            vout_list_details.append({'vout_address':vout_address[i],'vout_output':vout_outputs[i]})
        transaction_details['vin_list_details'] = vin_list_details
        transaction_details['vout_list_details'] = vout_list_details

    return transaction_details


def get_output_total(tx_list):
    print '--------- getting output total:::::::::: %s' %tx_list
    output_total = 0.0
    for transaction in tx_list:
        # tx_info = getrawtransaction(config.testnet['btc_prefix'],config.payload,str(transaction))
        tx_info = custom_rpc('getrawtransaction',[str(transaction),1])
        vout = tx_info['vout']
        for output_tx in vout:
            output_total += float(output_tx['value'])
    print output_total
    return output_total



if __name__ == '__main__':
    print "Running blockchain_explorer API"
    # app.secret_key = 'secret_wallet'
    # app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', debug=True)
