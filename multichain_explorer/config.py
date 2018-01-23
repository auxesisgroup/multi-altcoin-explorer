__author__ = 'udasi'


import datetime
from pymongo import MongoClient
import redis

str_date = datetime.datetime.now().strftime('%Y%m%d')

debug = True
development = True
staging = False


payload = {"jsonrpc":1,"id":"curltext"}
mainnet = {
    # 'btc_prefix': '/usr/bin/bitcoin-cli -rpcuser=explorer -rpcpassword=aouzqcLx__5jddVNbImqfKqK8P7RsBq5X-5q4IONGFo=  -datadir=/mnt/volume-nyc1-01-part1/',
    'btc:prefix': 'http://Yourusername:Yourpassword@localhost:7001/',
    # 'upd_url': 'http://127.0.0.1:5000/update_explorer',
}
testnet = {
    # 'btc_prefix': '/usr/bin/bitcoin-cli -rpcuser=sma -rpcpassword=haeibH_lGx3Gc1k__w7AmRMLTi0IWOAFwnJB9IT9xHk -testnet -datadir=/home/ayubi/.bitcoin',
    'btc_prefix': 'http://Yourusername:Yourpassword@localhost:7001/',
    # 'base_url': 'http://udasi:aa@localhost:8332/',
}

logger = {
    'mempool':{
    'filename': 'mempool_%s' % str_date,
    'path':'/var/log/python_apps/visachain_tests/'
    },
    'block':{
    'filename': 'block_%s' % str_date,
    'path':'/var/log/python_apps/visachain_tests/'
    },
    'explorer':{
    'filename': 'test_logs_%s' % str_date,
    'path':'/var/log/python_apps/visachain_tests/'
    }

}

_set = {}
if debug is True:
    _set = testnet
    if not development:
        # _set['btc_prefix'] = '/usr/bin/bitcoin-cli -rpcuser=explorer -rpcpassword=aouzqcLx__5jddVNbImqfKqK8P7RsBq5X-5q4IONGFo=  -datadir=/mnt/volume-nyc1-01-part1/ -testnet'
        _set['btc_prefix'] = 'http://Yourusername:Yourpassword@localhost:7001/'
        _set['upd_url'] = 'http://67.205.166.57/update_explorer'
        # _set['base_url'] = 'http://_explorer:aouzqcLx__5jddVNbImqfKqK8P7RsBq5X-5q4IONGFo=@localhost:18332/'
        _set['payload'] = {"jsonrpc":1,"id":"curltext"}


else:
    _set = mainnet
    if not development:
        # _set['btc_prefix'] = '/usr/bin/bitcoin-cli -rpcuser=explorer -rpcpassword=aouzqcLx__5jddVNbImqfKqK8P7RsBq5X-5q4IONGFo=  -datadir=/mnt/volume-nyc1-01-part1/'
        _set['btc_prefix'] = 'http://Yourusername:Yourpassword@localhost:7001/'
        # _set['base_url'] = 'http://_explorer:aouzqcLx__5jddVNbImqfKqK8P7RsBq5X-5q4IONGFo=@localhost:8332/'
        _set['payload'] = {"jsonrpc":1,"id":"curltext"}



def mongo_conn():
    try:
        conn = MongoClient(host='127.0.0.1', port=27017)
        print("MongoDB Connected", conn)
        return conn
    except Exception as e:
        print "Error in mongo connection: ", e


def redis_conn(ip='127.0.0.1', port=6379):
    try:
        r = redis.StrictRedis(host=ip, port=port)
        print "redis connected:", r
        return r
    except Exception as e:
        print "Error in redis connection: ", e
