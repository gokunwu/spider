#!/usr/bin/env python

import re
import os
import md5
import time
import datetime
import logging
import threading


import sys, signal, time
from urlparse import urljoin
from urlparse import urlparse
from bs4 import BeautifulSoup
from download import Downloader
from pymongo.connection import Connection
from pagestore import PageStore
from config import *
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

class Spider(threading.Thread):
    def __init__(self, master=True):
        threading.Thread.__init__(self)
        self.pagestore = PageStore()
        
        self.downloader = Downloader();
        self.connection = Connection(MONGODB_HOST, MONGODB_PORT)
        db = self.connection.download
        if master:
            db.drop_collection('downurl')
            for f, tb in ((SAVE_URL_RE_BLACK, 'save_url_black'),
                (SAVE_URL_RE_WHITE, 'save_url_white'),
                (DOWN_URL_RE_BLACK, 'down_url_black'),
                (DOWN_URL_RE_WHITE, 'down_url_white')):
                if os.path.exists(f):
                    db.drop_collection(tb)
                    logger.info('load rule:%s...' % f)
                    for s in set(open(f).readlines()):
                        s = s.strip()
                        if s:
                            db[tb].insert({'pattern': s})
                    logger.info('load rule:%s...OK' % f)
        self.downurl, self.allurl, self.watchurl, self.updateurl, self.secceedurl = db.downurl, db.allurl, db.watchurl, db.updateurl, db.secceedurl
        self.save_url_black = self.load_re(db.save_url_black)
        self.save_url_white = self.load_re(db.save_url_white)
        self.down_url_black = self.load_re(db.down_url_black)
        self.down_url_white = self.load_re(db.down_url_white)
        if master:
            self.load_watch_url()
            self.load_update_url()
            self.reload_allurl()
            logger.info('allurl:%d' % self.allurl.find().count())
            logger.info('secceedurl:%d' % self.secceedurl.find().count())
            logger.info('updateurl:%d' % self.updateurl.find().count())
            logger.info('watchurl:%d' % self.watchurl.find().count())
            logger.info('downurl:%d' % self.downurl.find().count())
        
    def load_re(self, tb):
        s = set([r['pattern'] for r in tb.find()])
        return [re.compile(s) for r in s]
    def get_safe_utf8(self, s):
        if isinstance(s, str):
            return s
        else:
            return s.encode('utf-8', 'ignore')
    def getmd5(self, s):
        m = md5.new()
        m.update(self.get_safe_utf8(s))
        return m.hexdigest()

    def get_one_task(self, tb):
        row = tb.find_and_modify(remove=True)
        if not row:return None
        row = self.allurl.find_one(row)
        return row['url'] if row else None

    def add_one_task(self, url, tb):
        s = url.lower()
        if s.startswith('http://') or s.startswith('https://'):
            k = self.getmd5(s)
            self.allurl.insert({'url': url, '_id':k})
            tb.insert({'_id': k})

    def load_watch_url(self):
        if not os.path.exists(WATCH_URL_FILE):
            return
        logger.info('load watch urls...')
        with open(WATCH_URL_FILE) as f:
            while True:
                url = f.readline()
                if not url:break
                self.add_one_task(url.strip(), self.watchurl)
        logger.info('load watch urls...%d' % self.watchurl.count())
    
    def normal_url(self, url):
        u = urlparse(url)
        if u.fragment:
            return url[:-(len(u.fragment) + 1)]
        return url
    
    def load_update_url(self):
        if not os.path.exists(UPDATE_URL_FILE):
            return
        logger.info('load update urls...')
        with open(UPDATE_URL_FILE) as f:
            while True:
                url = f.readline()
                if not url:break
                self.add_one_task(url.strip(), self.updateurl)
        logger.info('load update urls...%d' % self.updateurl.count())
    
    def check_url(self, url, black, white):
        for p in black:
            if p.search(url):
                return False
        if not white:
            return True
        for p in white:
            if p.search(url):
                return True
        return False
    
    def check_add_new_task(self, url):
        s = url.lower()
        #error url
        if not s.startswith('http://') and not s.startswith('https://'):
            return False
        #don't save url
        if not self.check_url(url, self.save_url_black, self.save_url_white):
            return False
        k = self.getmd5(s)
        #already save
        if self.allurl.find({'_id':k}).count():
            return False
        self.allurl.insert({'url': url, '_id':k})
        
        #dont't down
        if not self.check_url(url, self.down_url_black, self.down_url_white):
            return False
        
        #already down succeed
        if self.secceedurl.find({'_id':k}).count():
            return False
        self.downurl.insert({'_id': k})
        return True
    
    def reload_allurl(self):
        logger.info('reload all url...')
        for row in self.allurl.find():
            k, url = row['_id'], row['url']
            if not self.check_url(url, self.down_url_black, self.down_url_white):
                continue
            if self.secceedurl.find({'_id':k}).count():
                continue
            self.downurl.insert({'_id':k})
        logger.info('reload all url...%d ' % self.downurl.find().count())
    
    def detect_html(self, html):
        if not html:return None
        try:
            return html.decode('utf-8')
        except:
            return html.decode('gbk', 'ignore')
    
    def process_url(self, url):
        html, redirect, code = self.downloader.fetch(self.get_safe_utf8(url))
        if code == 200:
            html = self.detect_html(html)
            for href in self.link_parse(html, redirect):
                try:
                    self.check_add_new_task(href)
                except Exception as e:
                    logger.exception('%s,%s:%s' % (type(href), href, e.message))
            for k in set([self.getmd5(url.lower()), self.getmd5(redirect.lower())]):
                self.secceedurl.insert({'_id': k})
            if html:
                self.pagestore.succeed(url, html)
                return True
        return False
    
    def link_parse(self, html, base):
        urls = set()
        if not html or not base:return urls
        soup = BeautifulSoup(html)
        for a in soup.findAll('a'):
            href = a.get('href')
            if not href:continue
            if href in urls:continue
            href = self.normal_url(self.get_safe_utf8(urljoin(base, self.get_safe_utf8(href))))
            urls.add(href)
        return urls
    
    def get_url_block(self):
        while True:
            for tb in (self.watchurl, self.downurl, self.updateurl):
                url = self.get_one_task(tb)
                if url:return url
            logger.info('no any task')
            time.sleep(1)
        
    def proce_one_url(self):
        url = self.get_url_block()
        logger.info('down:%s' % url)
        ret = False
        try:
            ret = self.process_url(url)
        except Exception as e:
            logger.exception('url:%s %s' % (url, e.message))
        if not ret:
            self.pagestore.failed(url)

    def run(self):
        while True:
            try:
                while True:
                    self.proce_one_url()
            except Exception,e:
                logger.exception(e.message)
                time.sleep(1)
   

if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda x,y:sys.exit())
    master = None
    if MASTER:
        master = Spider(True);
    threads = [Spider(False) for i in range(MAX_DOWN_THREAD)]
    for th in threads:
        th.setDaemon(True)
        th.start()
    while True:
        time.sleep(WATCH_SLEEP_MINUTE * 60)
        if master:
            master.load_watch_url()
