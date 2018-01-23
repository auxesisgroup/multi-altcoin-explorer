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

logger = config.logger['explorer']
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
    'rpc_port': 6268,
    'user_name': 'multichainrpc',
    'password': '6j3BcorWN6bAHAR2zG8mTMHCanygBJqBupV9ThcEV5NV',
    'root': '1U4CEBPxBEPordqBrXuYf5ypRXsoHnEeRF9ouw',
    'burn_address':'1XXXXXXWhKXXXXXXqXXXXXXXTxXXXXXXb1d3Yd'
}

if prod:
    conf['password'] = 'FeHhgHtviDvQi8KyRRb2P9bWqm8jy254K7LudAy5ZBMW'
    conf['rpc_port'] = 4258
    conf['root'] = '1SiHjBKisFnLRZrRRX2v54aq6qx5dKyKB1Ws97'
    conf['burn_address'] = '1XXXXXXX97XXXXXXAxXXXXXXgGXXXXXXYNhbVR'

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


def get_vout(input_transaction,from_address):
    transaction_details = custom_rpc('getrawtransaction',[input_transaction,1])
    vout = transaction_details['vout']
    count = 0
    for vout_details in vout:
        if 'scriptPubKey' in vout_details:
            if 'addresses' in vout_details['scriptPubKey']:
                # print 'qqqqq %s' %vout_details['scriptPubKey']['addresses']
                if vout_details['scriptPubKey']['addresses'][0] == from_address:
                    # print 'wwww'
                    return count
                else:
                    count += 1


def issue_assets():
    init_issue = custom_rpc('issue',[conf['root'],{"name":"aux_coin_v1","open":True},10000,0.01])
    txid_list = []
    priv_key_list = []
    address_list = []
    for i in range(0,1000):
        keypair = custom_rpc('createkeypairs')
        issue_txid = custom_rpc('sendtoaddress',[keypair[0]['address'],{"aux_coin_v1":10}])
        txid_list.append(issue_txid)
        address_list.append(keypair[0]['address'])
        priv_key_list.append(keypair[0]['privkey'])
    # print {'txid_list':txid_list,'priv_key_list':priv_key_list}
    return {'txid_list':txid_list,'priv_key_list':priv_key_list,'address_list':address_list}


def create_transactions():
    while True:
        issue_data = issue_assets()
        txid_list = issue_data['txid_list']
        priv_key_list = issue_data['priv_key_list']
        address_list = issue_data['address_list']
        for i in range(0,len(txid_list)):
            print 'thread %s started' %i
            thread.start_new_thread(create_transaction_threads,(i,txid_list[i],address_list[i],priv_key_list[i],))
            print 'thread %s stopped' %i

        # inputs_list = []
        # vout = get_vout(txid_list[i],address_list[i])
        # inputs_list.append({"txid":txid_list[i],"vout":vout})
        # new_keypair = custom_rpc('createkeypairs')
        # new_grant = custom_rpc('grant',[new_keypair[0]['address'],'send,receive'])
        # to_address = new_keypair[0]['address']
        # hex_blob = custom_rpc('createrawtransaction',[inputs_list,{to_address:{"aux_coin_v1":5000}}])
        # longer_hex_blob = custom_rpc('appendrawchange',[hex_blob,address_list[i]])
        # even_longer_hex_blob = custom_rpc('appendrawdata',[longer_hex_blob,'5554584f732046545721'])
        # final_hex_blob = custom_rpc('signrawtransaction',[even_longer_hex_blob,[],[priv_key_list[i]]])
        # txid = custom_rpc('sendrawtransaction',[final_hex_blob['hex']])
        # print 'txid for ::: %s is:: %s' %(i,txid)


def create_transaction_threads(counter,input_txid,from_address,priv_key):
    print '11111111111111111111111111111111111'
    start_time = (time.time())
    inputs_list = []
    vout = get_vout(input_txid,from_address)
    inputs_list.append({"txid":input_txid,"vout":vout})
    new_keypair = custom_rpc('createkeypairs')
    #new_grant = custom_rpc('grant',[new_keypair[0]['address'],'send,receive'])
    to_address = new_keypair[0]['address']
    hex_blob = custom_rpc('createrawtransaction',[inputs_list,{to_address:{"aux_coin_v1":5}}])
    longer_hex_blob = custom_rpc('appendrawchange',[hex_blob,from_address])
    even_longer_hex_blob = custom_rpc('appendrawdata',[longer_hex_blob,'5554584f732046545721'])
    final_hex_blob = custom_rpc('signrawtransaction',[even_longer_hex_blob,[],[priv_key]])
    txid = custom_rpc('sendrawtransaction',[final_hex_blob['hex']])
    end_time = (time.time())
    print 'txid is::::: %s for thread:: %s' %(txid,counter)


    burn_coins(counter,txid,to_address,new_keypair[0]['privkey'],input_txid,from_address,priv_key)
    # print 'txid for ::: %s is:: %s' %(counter,txid)
    _logging.debug('time taken for::: %s transaction with txid:: %s is::::: %s'  %(counter,txid,end_time-start_time))


def burn_coins(counter,txid_1,address_1,priv_key_1,txid_2,address_2,priv_key_2):
    print '22222222222222222222222'
    start_time = (time.time())
    inputs_list = []
    vout = get_vout(txid_1,address_1)
    inputs_list.append({"txid":txid_1,"vout":vout})
    hex_blob = custom_rpc('createrawtransaction',[inputs_list,{conf['burn_address']:{"aux_coin_v1":5}}])
    longer_hex_blob = custom_rpc('appendrawchange',[hex_blob,address_1])
    even_longer_hex_blob = custom_rpc('appendrawdata',[longer_hex_blob,'5554584f732046545722'])
    final_hex_blob = custom_rpc('signrawtransaction',[even_longer_hex_blob,[],[priv_key_1]])
    txid = custom_rpc('sendrawtransaction',[final_hex_blob['hex']])
    end_time = (time.time())
    print 'txid is::::: %s for thread:: %s' %(txid,counter)
    _logging.debug('time taken for burning::: %s transaction with txid:: %s is::::: %s'  %(counter,txid_1,end_time-start_time))



    # time.sleep(10)
    # start_time = (time.time())
    # inputs_list = []
    # vout = get_vout(txid_2,address_2)
    # inputs_list.append({"txid":txid_2,"vout":vout})
    # hex_blob = custom_rpc('createrawtransaction',[inputs_list,{conf['burn_address']:{"aux_coin_v1":5}}])
    # longer_hex_blob = custom_rpc('appendrawchange',[hex_blob,address_2])
    # even_longer_hex_blob = custom_rpc('appendrawdata',[longer_hex_blob,'5554584f732046545722'])
    # final_hex_blob = custom_rpc('signrawtransaction',[even_longer_hex_blob,[],[priv_key_2]])
    # txid = custom_rpc('sendrawtransaction',[final_hex_blob['hex']])
    # end_time = (time.time())
    # print 'txid is::::: %s for thread:: %s' %(txid,counter)
    # _logging.debug('time taken for burning::: %s transaction with txid:: %s is::::: %s'  %(counter,txid_1,end_time-start_time))

create_transactions()

time.sleep(5000)
