__author__ = 'cryptoKTM'
import requests,json,sys,os,pymongo
import config
from wrap_core import *
import time
import logging
import datetime
import sys


import requests,json,sys,os,pymongo

from pymongo import MongoClient


db_conn = config.mongo_conn().rajchain_explorer
redis_conn = config.redis_conn()



url="http://asd:asdf@localhost:2332"
payload={}
payload = {"jsonrpc":1,"id":"curltext"}

 
# url="http://masscoinrpc:00AD1197627954913F825A16CFF4D4503E45616639C97543EA1C439ED9C735DC@localhost:2332"
   
# url="http://masscoinrpc:00AD1197627954913F825A16CFF4D4503E45616639C97543EA1C439ED9C735DC@165.227.116.61:2332"
 


class wrapcoreException(Exception): 
	def __init__(self, value): 
		self.parameter = value 
	def __str__(self): 
		return repr(self.parameter)





def get_block_count():
	payload["method"] = "getblockcount"
	payload["params"] =[]
	# print payload
	response = requests.post(url,json.dumps(payload))
	if response.status_code != 200:
		raise wrapcoreException ('')
	return(response.json()["result"])

def gettxid(block_no):
	# print"into gettxid"
	print "crawling block no block_no_ %s" %block_no	
	payload["method"]="getblockhash"
	payload["params"]=[block_no]
	resp = requests.post(url,json.dumps(payload))
	if resp.status_code != 200:
		raise wrapcoreException (block_no)
	else:
		block_hash = resp.json()["result"]
		payload["method"]="getblock"
		payload["params"]=[block_hash]
		resp = requests.post(url,json.dumps(payload))
		if resp.status_code == 200:
			return resp.json()["result"]["tx"]
		else:
			raise wrapcoreException("getblock error")

def add_from_txid(txid,block_no_):
	try:
		vin_addresses = []     
		vout_addresses=[]
		payload["method"]="getrawtransaction"
		payload["params"]=[txid,1]
		response = requests.post(url,json.dumps(payload))
		if response.status_code != 200:
			# raise Exception ('rpc error')
			raise wrapcoreException ("(line 95)vin_add ERROR for txid:: "+txid)
		response =response.json()
		# print "res is %s " %response
		timestamp = response["result"]["time"]
		block_no = block_no_
		response_vout = response["result"]["vout"]
		response_vin= response["result"]["vin"] 

		for data in response_vout:
			vout_json = {}
			vout_json["address"]=data["scriptPubKey"]["addresses"][0]
			vout_json["value"]=data["value"]
			vout_json["index"]=data["n"]
			vout_json["block_no"] =block_no
			vout_json["timestamp"] = timestamp
			vout_json["txid"]= txid
			vout_addresses.append(vout_json)

			exists_flag = db_conn.address_details_v5.find_one(vout_json)
			if not exists_flag:
				vout_insert_result = db_conn.address_details_v5.insert(vout_json)

		for data in response_vin:
			if data.__contains__('coinbase'):
				pass
				

			else:
				raw_tx1=data["txid"]
				vout_int=data["vout"]  #vout index
				payload["params"]=[raw_tx1,1]
				response_ = requests.post(url,json.dumps(payload))
				response_= response_.json()
				timestamp_ = response_["result"]["time"]
				data_ =response_["result"]["vout"]
				for item in data_:
					if item["n"] == vout_int:
						vin_json ={}
						vin_json["address"]=item["scriptPubKey"]["addresses"][0] 
						# vin_json["spent_timestamp"]=item["timestamp"]
						find_params={"address":vin_json["address"],"txid":raw_tx1}

						# exists_flag = db_conn.address_details_v5.find_one(find_params)
						# if exists_flag:
						update_flag = db_conn.address_details_v5.update(find_params,{"$set":{"spent_timestamp":timestamp,"spent_txid":txid}})
						# vin_json["spent_timestamp"]=item["timestamp"]
						# balance=item["value"]
					
						vin_addresses.append(vin_json)



		# print vout_addresses
		if vout_addresses and vin_addresses:
			return {"vout_add":vout_addresses,"vin_add":vin_addresses}


	except Exception as e:

		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
		print(exc_type, fname, exc_tb.tb_lineno, e.message)


try:
	crawled_block = int(redis_conn.get('crawled_block'))
	# crawled_block += 1  #is the no of block that is going to get crawled now
	block_count = int(get_block_count())
	final={}

	while((crawled_block+1) < block_count):
		# print 
		tx_array=gettxid((crawled_block+1))
		for data in tx_array:
			txid = str(data)
			a = add_from_txid(txid,(crawled_block+1))
			# if not a:
			# 	raise wrapcoreException('error on ')
		# final["block_no"]=crawled_block
		
		redis_conn.set('crawled_block',(crawled_block+1))
		crawled_block = int(redis_conn.get('crawled_block'))
		block_count = int(get_block_count())
		# print final
		# block_count+=1
		# crawled_block +=1
except wrapcoreException as we:
	print we.parameter
except Exception as e:
	exc_type, exc_obj, exc_tb = sys.exc_info()  
	fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1] 
	print "exception" 
	print(exc_type, fname, exc_tb.tb_lineno, e.message)