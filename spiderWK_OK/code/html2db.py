#!/usr/bin/env python
#import datetime
#from sqlalchemy import Column,create_engine,Table,MetaData
#from sqlalchemy.types import TIMESTAMP,Integer,String
#from sqlalchemy.dialects.mysql import MEDIUMTEXT
#from config import *
#
#class Html2db:
#    def __init__(self):
#        dbengine = create_engine("mysql://%s:%s@%s/%s?charset=utf8&use_unicode=0" % (MYSQL_USER,MYSQL_PASS,MYSQL_HOST,MYSQL_DB))
#        metadata = MetaData(dbengine)
#        table = Table('bjdch_spider_wk',metadata,autoload = True)
#        self.conn = dbengine.connect()
#    def datainsert(self,title,content,htmlpage,url,pubtime,inserttime):
#        self.conn.execute(self.table.insert().values(title = title,content = content,htmlpage = htmlpage,url = url,pubtime = pubtime,inserttime = inserttime))
#        #self.conn.execute(self.table.insert().values(title = title,content = content,htmlpage = htmlpage,class = chChannel,url = url,pubtime = pubtime,inserttime = inserttime))

import MySQLdb
import sys
from config import *

class Html2db:
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(host =MYSQL_HOST,db = MYSQL_DB,user = MYSQL_USER,passwd = MYSQL_PASS,charset = 'utf8')
            self.cursor = self.conn.cursor()
        except MySQLdb.Error, e:
            sys.stderr.write("Could not open the MySQLdb !")

    def datainsert(self,title,content,htmlpage,chChannel,url,pubtime,inserttime):
        try:
            sql = "insert into bjdch_spider_wk(title,content,htmlpage,class,url,pubtime,inserttime)values(%s,%s,%s,%s,%s,%s,%s)"
            para = (title,content,htmlpage,chChannel,url,pubtime,inserttime)
            self.cursor.execute(sql,para)
        except MySQLdb.Error, e:
            sys.stderr.write("Insert data to bjdch_spider failed !")








