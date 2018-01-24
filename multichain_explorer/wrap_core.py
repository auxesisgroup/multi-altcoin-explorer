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




prod = False
redis_conn = config.redis_conn()
conf = {
    'rpc_port': 10332,
    'user_name': 'masscoinrpc',
    'password': '9Gjz8kSHqpEafq6DUaisePcnf6jSXiXcDKiUsfvwbMvC',
    'root': '1MNbWhUdFN2K7cTsehupp38zE79W6RvxfWprTf'
}

if prod:
    conf['password'] = 'BbM33ywZTXttm3wgyjWM1121TikNUaYShyD7vK2rf1La'
    conf['rpc_port'] = 8372


class WrapCoreException(Exception):
    def __init__(self, reason):
        self.reason = reason

class ModuleWrapCoreException(Exception):
    def __init__(self, reason):
        self.reason = reason


def single_quotes(data):
    return "'" + str(data) + "'"


def double_quotes(data):
    return '"' + str(data) + '"'


def sign_trans():
    pass

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


def listunspent(btc_prefix,payload):
    try:
        print("in list unspent")
        payload['method'] = 'listunspent'
        payload['params'] = []
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def generate(btc_prefix, number=1):
    print("Generating %s blocks" % number)
    cmd = ""
    print btc_prefix.split()
    if '-regtest' in btc_prefix.split():
        print 'in regtest'
        cmd = ' '.join([btc_prefix, 'generate', str(number)])
    # os_lambda = lambda x : os.popen(cmd).read()
    # pool = Pool(processes=1)
    # response = pool.apply_async(os_lambda, [0])
    response = os.popen(cmd).read()
    typed_response = json.loads(response)
    # print (typed_response)
    return typed_response


def getnewaddress(btc_prefix):
    print("in getnewaddress")
    cmd = ' '.join([btc_prefix, 'getnewaddress'])
    response = os.popen(cmd).read()
    # print (typed_response)
    return response


def listaddressgroupings(btc_prefix):
    print("in list address groupings")
    cmd = ' '.join([btc_prefix, 'listaddressgroupings'])
    response = os.popen(cmd).read()
    typed_response = json.loads(response)
    # print (typed_response)
    return typed_response


def getrawtransaction(btc_prefix,payload, transaction_hex):
    # cmd = ' '.join([btc_prefix, 'getrawtransaction', transaction_hex, '1'])
    # response = os.popen(cmd).read()
    # return json.loads(response)
    try:
        # print("in getrawtransaction wrapcore")
        # print 'tt %s,%s' %(transaction_hex,type(transaction_hex))
        payload['method'] = 'getrawtransaction'
        payload['params'] = [transaction_hex,1]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        # print 'rrr232323232323 %s' %response.status_code
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        # else:
        #     print 'WrapcoreException '
        #     raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def createrawtransaction(btc_prefix,payload, vin, vout):
    # print("in createrawtransaction")
    # cmd = ' '.join([btc_prefix, 'createrawtransaction', single_quotes(vin), single_quotes(vout)])
    # print 'creating raw trans %s' % cmd
    # response = os.popen(cmd).read()
    # return response
    try:
        print("in create rawtransaction wrapcore")#,vin,type(vin),type(vout)
        payload['method'] = 'createrawtransaction'
        payload['params'] = [json.loads(vin),json.loads(vout)]
        # print "payload", payload
        response = requests.post(btc_prefix,data=json.dumps(payload))
        print response
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']

        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def decoderawtransaction(btc_prefix,payload, transaction_hex):
    # print 'in decode raw transaction decoding %s' % transaction_hex
    # cmd = ' '.join([btc_prefix, 'decoderawtransaction', transaction_hex])
    # response = os.popen(cmd).read()
    # return response
    try:
        print("in decoderawtransaction wrapcore")
        payload['method'] = 'decoderawtransaction'
        payload['params'] = [transaction_hex]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def signrawtransaction(btc_prefix,payload ,trans_hex, utxo, keys, hash_type=''):
    # print 'in signrawtransaction decoding %s' % [trans_hex, utxo, hash_type]
    # cmd = ' '.join([btc_prefix, 'signrawtransaction', trans_hex, single_quotes(utxo), single_quotes(keys)])
    # print cmd
    # response = os.popen(cmd).read()
    # return response
    try:
        print("in signrawtransaction wrapcore")
        payload['method'] = 'signrawtransaction'
        payload['params'] = [trans_hex,json.loads(utxo),json.loads(keys)]
        print 'payload',payload
        response = requests.post(btc_prefix,data=json.dumps(payload))
        print response
        if response.status_code == 200:
            result = json.loads(response.text)
            print result['result'],type(result['result'])
            return result['result']
        # else:
        #     print 'WrapcoreException '
        #     raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def sendrawtransaction(btc_prefix,payload, signed_hex):
    # cmd = ' '.join([btc_prefix, 'sendrawtransaction', signed_hex])
    # response = os.popen(cmd).read()
    # return response
    try:
        print("in sendrawtransaction wrapcore")
        payload['method'] = 'sendrawtransaction'
        payload['params'] = [signed_hex]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def dumpprivkey(btc_prefix,payload, address):
    try:
        print("in dummppriv wrapcore")
        payload['method'] = 'dumpprivkey'
        payload['params'] = [address]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def getblock(btc_prefix,payload, block_hash):
    try:
        # print("in getblock wrapcore")
        payload['method'] = 'getblock'
        payload['params'] = [block_hash]
        response = requests.post(btc_prefix,data=json.dumps(payload))

        # print "resp!!!", response.text
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        # else:
        #     print 'WrapcoreException '
        #     raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def getblockhash(btc_prefix, payload,block_number):
    try:
        # print("in getblockhash wrapcore, getting hash of::%s" %block_number)
        payload['method'] = 'getblockhash'
        payload['params'] = [int(block_number)]
        # print 'btbt %s' %btc_prefix
        response = requests.post(btc_prefix,data=json.dumps(payload))
        # print '111 %s' %response.text
        if response.status_code == 200:
            result = json.loads(response.text)
            # print "result", result
            return result['result']
        # else:
        #     print 'WrapcoreException '
        #     raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def getblockcount(btc_prefix,payload):
    try:
        # print("in getblockcount wrapcore")
        payload['method'] = 'getblockcount'
        payload['params'] = []
        response = requests.post(btc_prefix,data=json.dumps(payload))
        # print 'rrrrrr %s' %response.text
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        # else:
        #     print 'WrapcoreException '
        #     raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def getRawMemPool(btc_prefix,payload):
    try:
        # print("in getrawmempool wrapcore")
        payload['method'] = 'getrawmempool'
        payload['params'] = []
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def getinfo(btc_prefix, payload):
    # cmd = ' '.join([btc_prefix, 'getinfo'])
    # response = os.popen(cmd).read()
    # typed_response = json.loads(response)
    # return typed_response
    try:
        print("in getinfo wrapcore")
        payload['method'] = 'getinfo'
        payload['params'] = []
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def estimatefee(btc_prefix,payload, blocks):
    try:
        print("in estimatefee wrapcore")
        payload['method'] = 'estimatefee'
        payload['params'] = [blocks]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def gettxout(btc_prefix, payload,txid, vout):
    try:
        print("in gettxout wrapcore")
        payload['method'] = 'gettxout'
        payload['params'] = [str(txid),str(vout)]
        response = requests.post(btc_prefix,data=json.dumps(payload))
        if response.status_code == 200:
            result = json.loads(response.text)
            return result['result']
        else:
            print 'WrapcoreException '
            raise ModuleWrapCoreException('WCE')
    except WrapCoreException as wce:
        print 'WrapCoreException ', wce
        raise WrapCoreException('WCE')
    except requests.ConnectionError as ce:
        print 'Error: Bitcoin core is not running'# ,ce.message


def custom(btc_prefix, core_api, _json=True):
    cmd = ' '.join([btc_prefix, str(core_api)])


def getblockcount1(btc_prefix):
    print("in getblockcount")
    cmd = [btc_prefix, 'getblockcount']
    # p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
    # stderr=subprocess.PIPE, shell=True)
    # out, err = p.communicate()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    o = p.stdout().read()
    # response = os.popen(cmd).read()
    print "response: %s " % o
    # typed_response = json.loads(response)
    # try:
    #     return int(response)
    # except Exception as e:
    #     return e


# print getblockcount1(config.btc_prefix)
# a = getrawtransaction('http://udasi:aa@localhost:18332/',{"jsonrpc":1,"id":"curltext"},'086951e293b1696986fd776f338a38309218bb79bcfe48b02434bfae3f0ff16f')
# print a
