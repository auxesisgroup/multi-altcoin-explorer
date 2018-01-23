__author__ = 'udasi'
import config
from wrap_core import *

db_conn = config.mongo_conn().explorer
redis_conn = config.redis_conn()

res = db_conn.address_check.update({'array.tx':"tx3",'array.n':1},{"$set":{'array.$.spent':True}})
print res