import sys
import logging
import os
import requests
import json
import datetime
import random
import sqlite3
import time
import config
import thread

logger = config.logger['explorer1']
logging.getLogger("requests").setLevel(logging.WARNING)
_file = logger['path'] + logger['filename']
logging.basicConfig(filename=_file,
                filemode='a',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%H:%M:%S',
                level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
_logging = logging.getLogger('explorer')
_logging.addHandler(logging.StreamHandler(sys.stdout))

prod = False
redis_conn = config.redis_conn()
conf = {
    'rpc_port': 6754,
    'user_name': 'multichainrpc',
    'password': '5JeZbt2cDEuWzceZyVUhY9BbCjbvsiRy5MRjZHav4oKd',
    'root': '1DwE9qG9qfDokiyx6AyhCp9dp4UgLrMmWcVF4C'
}

if prod:
    conf['password'] = 'BbM33ywZTXttm3wgyjWM1121TikNUaYShyD7vK2rf1La'
    conf['rpc_port'] = 8372



class UtilityException(Exception):
    def __init__(self, message):
        self.message = message

class exec_time():
    def __init__(self):
        self.start_epoch = time.time()

    def get_duration(self):
        self.end_epoch = time.time()
        duration = self.end_epoch - self.start_epoch
        return duration

def custom_rpc(method, params=[]):
    try:
        _prefix = 'http://' + conf['user_name'] + ':' + conf['password'] + '@localhost:' + str(conf['rpc_port']) + '/'
        payload = {"jsonrpc": 1, "id": "curltext"}
        print _prefix
        # print("Remote Procedural Call")
        payload['method'] = method
        payload['params'] = params
        rpc_start_time = exec_time()
        response = requests.post(_prefix, data=json.dumps(payload))
        # print 'response!!!', payload
        if response.status_code == 200:
            rpc_end_time = rpc_start_time.get_duration()
            print 'time taken for rpc of method::: %s, is::: |%s' %(method,rpc_end_time)
            _logging.debug('time taken for rpc of method::: %s, is::: |%s' %(method,rpc_end_time))
            result = json.loads(response.text)
            return result['result']
        else:
            rpc_end_time = rpc_start_time.get_duration()
            print 'time taken for rpc of method::: %s, is::: |%s' %(method,rpc_end_time)
            reason = json.loads(response.text)
            print 'error in rpc call for method:::: %s, reason is::: %s' %(method,reason)
            return None
            # raise UtilityException(reason)
    except UtilityException as wce:
        print 'UtilityException', wce.message
        raise wce
    except requests.ConnectionError as ce:
        reason = "Mulitchain Core not running"
        print 'Error: Multichain core is not running'  # ,ce.message
        # raise UtilityException({'reason': 'Bitcoin Server not running'})


def get_transactions():
    transactions_list = []
    for block_no in range(500,1000):
        if block_no % 2 == 0:
            print 'block_number::: %s' %block_no
            block_details = custom_rpc('getblock',['1'])
            txs = block_details['tx']
            for transaction in txs:
                transactions_list.append(transaction)
    print transactions_list
    return transactions_list

def consecutive_transactions():
    transactions_list = get_transactions()
    for i in range(0,len(transactions_list)):
        st = time.time()
        transaction_details = custom_rpc('getrawtransaction',[transactions_list[i],1])
        et = time.time()
        print 'time taken for transaction::: %s is::: %s' %(i,et - st)
        _logging.debug('time taken for transaction::: %s is::: %s' %(i,et - st))

def get_transaction_info(counter,txid):
    st = time.time()
    transaction_details = custom_rpc('getrawtransaction',[txid,1])
    et = time.time()
    print 'time taken for transaction::: %s is::: %s' %(counter,et - st)
    _logging.debug('time taken for transaction::: %s is::: %s' %(counter,et - st))

def parallel_transactions():
    counter = 0
    transactions_list = get_transactions()
    for transaction in transactions_list:
        thread.start_new_thread(get_transaction_info,(counter,transaction,))
        counter += 1



# consecutive_transactions()
parallel_transactions()
time.sleep(5000)

#
#
# def _timings():
#     # create key pairs timing
#     st = time.time()
#     keypair = custom_rpc('createkeypairs')
#     et = time.time()
#     print et, st
#     print 'createkeypair time ', et - st
#     # grant timing
#     st = time.time()
#     grant = custom_rpc('grant', [keypair['address'], 'send,receive'])
#     et = time.time()
#     print et, st
#     print 'grant time ', et - st
#     #issuemmore time
#     st = time.time()
#     grant = custom_rpc('issuemore', [keypair['address'], 'Auxtoken', 10])
#     et = time.time()
#     print et, st
#     print 'issue time ', et - st