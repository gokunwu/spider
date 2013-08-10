#!/usr/bin/env python
# -*- coding: utf-8 -*-
import signal
import sys
import logging
import time
import re
import os

from HTMLParser import HTMLParser
from urlparse import urljoin
from urlparse import urlparse
from urlparse import urlsplit
from bs4 import BeautifulSoup
from download import Downloader
from html2db import Html2db 
from config import *

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.NOTSET)

class Spider():
    def __init__(self):
        self.today = time.strftime("%Y-%m-%d",time.localtime(time.time()))
        self.urllogpath = "../data/url"
        os.system("mkdir -p %s" % self.urllogpath)
        self.urllog = "../data/url/" + "downloadedurl_" + self.today + ".txt"
        self.subpagepath = "../data/subpagepath"
        os.system("mkdir -p %s" % self.subpagepath)
        
        self.baseurl = BASEURLS 
        self.suburl = {}
        self.downloader = Downloader()
        self.html2db = Html2db()

    def get_safe_utf8(self,s):
        if isinstance(s,str):
            return s
        else:
            return s.encode('utf-8','ignore')
    
    def detect_html(self,html):
        if not html:return None
        try:
            return html.decode('utf-8')
        except:
            return html.decode('gbk','ignore')
    
    def normal_url(self,url):
        u = urlparse(url)
        if u.fragment:
            return url[:-(len(u.fragment) + 1)]
        return url
    
    def link_parse(self,html,base):
        if not html or not base: return urls
        soup = BeautifulSoup(html)
        for li in soup.findAll('li'):
            try:
                li.contents[0].contents[0]
            except:
                continue
            title = li.contents[0].contents[0]
            #title = self.get_safe_utf8(title)
            href = li.contents[0]["href"]
            time = li.contents[1].strip()
            time = time.replace(u'）',"")
            time = time.replace(u'（',"")
            #title = self.cleanHtmlTag(self.get_safe_utf8(title))
            if not href:continue
            if href in self.suburl.keys():continue
            href = self.normal_url(self.get_safe_utf8(urljoin(base, self.get_safe_utf8(href))))
            #self.suburl[href] = (title,time)
            if time == self.today:
                self.suburl[href] = (title,time)
            #print title 
            #print href
            #print time 
        return True

    def cleanHtmlAgain(self,value):
        regex1 = "&lt;[\s\S]*?&gt;"
        value = re.subn(regex1,"",value,re.M)
        return value[0]

    def cleanHtmlTag(self,html):
        html = html.strip()
        html = html.strip("\n")
        result = []
        parser = HTMLParser()
        parser.handle_data = result.append
        parser.feed(html)
        parser.close()
        res = ''.join(result)
        res = self.cleanHtmlAgain(res)
        return res

    def getSubUrl(self,baseurl):
        tmp = ""
        maxturnpage = 5
        regex = "\/[a-zA-Z0-9]+_[a-zA-Z0-9]+\.htm$"
        for i in range(1,maxturnpage):
            if(re.search(regex,baseurl)):
                regextmp = "\.htm$"
                tmp = re.sub(regextmp,"_" + str(i) + ".htm",baseurl)
            else:
                regexdel = "_\d?\.htm$"
                urltmp = re.sub(regexdel,"_" + str(i) + ".htm",baseurl)
                baseurl = urltmp
            html, redirect, code = self.downloader.fetch(self.get_safe_utf8(baseurl))
            if code == 200:
                html = self.detect_html(html)
                self.link_parse(html,redirect)
                print 'baseurl down succeed : %s' % baseurl
            baseurl = tmp
        return True

    def deleteDownloadedUrl(self):
        print "There are %s urls need to download!" % len(self.suburl.keys())
        if os.path.isfile(self.urllog):
            logfile = open(self.urllog)
            if logfile:
                for line in logfile.readlines():
                    line = line.strip()
                    if line in self.suburl.keys():
                        del self.suburl[line]
            else:
                print("Could not open the logfile : %s",self.urllog)
        else:
            print ("the logfile : " + self.urllog + " is not exists this time !")
        print "There are %s urls  REALLY need to download!" % len(self.suburl.keys())
        
    def downloadPages(self,enChannel,chChannel):
        enChannelpath = self.subpagepath + "/" + enChannel
        os.system("mkdir -p %s" % enChannelpath)
        num = 0
        for suburl in self.suburl.keys():
            title = self.suburl[suburl][0]
            pubtime = self.suburl[suburl][1]
            html, redirect, code = self.downloader.fetch(self.get_safe_utf8(suburl))
            if code == 200:
                print "suburl download succeed : %s" % suburl
                html = self.detect_html(html)
                subpagefile = enChannelpath + "/content_" + self.today +"_" + str(num) + ".html"
                num = num + 1
                try:
                    fileout = open(subpagefile,"w")
                    fileout.write(self.get_safe_utf8(html) + "\n")
                    fileout.close()
                except IOError, e:
                    sys.stderr.write("could not open the subpagefile : %s" + subpagefile)
                soup = BeautifulSoup(html)
                for div in soup.findAll("div",id="Zoom"):
                    content = self.cleanHtmlTag(str(div))

                inserttime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                try:
                    title = self.get_safe_utf8(title)
                except:
                    title =title
                content = self.get_safe_utf8(content)
                html = self.get_safe_utf8(html)
                chChannel = self.get_safe_utf8(chChannel)
                suburl = self.get_safe_utf8(suburl)
                self.html2db.datainsert(title,content,html,chChannel,suburl,pubtime,inserttime)
            print title
            print suburl
            print pubtime
            #print content
            #print html
            print chChannel
            print inserttime 
            print "################################################################################"

    def recordDownloadedUrl(self):
        try:
            logout = open(self.urllog,"a")
            for url in self.suburl.keys():
                logout.write(url + "\n")
            logout.close()
        except IOError, e:
            sys.stderr.write("could not open the logfile : %s to write!" % self.urllog)


if __name__ == "__main__":
    signal.signal(signal.SIGINT,lambda x,y:sys.exit())
    spider = Spider()
    print "*********************************************************************"
    print "the spider start at %s" % time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    for baseurl in spider.baseurl.keys():
        enChannel = spider.baseurl[baseurl][0]
        chChannel = spider.baseurl[baseurl][1]
        print enChannel
        print chChannel
        spider.getSubUrl(baseurl)
        spider.deleteDownloadedUrl()
        spider.downloadPages(enChannel,chChannel)
        spider.recordDownloadedUrl()

    print "the spider finished at %s" % time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
    print "*********************************************************************\n"
