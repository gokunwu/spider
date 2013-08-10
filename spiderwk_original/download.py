#!/usr/bin/env python
import gzip
import io
import urllib2
import chardet
from urlparse import urljoin
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):     
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)              
        result.status = code 
        return result                                       
    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)              
        result.status = code                                
        return result
    
class Downloader:
    def __init__(self):
        self.header = {'User-Agent': "Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-CN; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3",
                         'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                              'Accept-Language':'en,zh-cn;q=0.7,zh;q=0.3',
                              'Accept-Encoding':'gzip',
                              'Accept-Charset':'GB2312,utf-8;q=0.7,*;q=0.7'}
        
    def content_decode(self, html, encoding):        
        if not encoding or not html:return html
        encoding = encoding.lower()
        if encoding == 'gzip':
            zfile = gzip.GzipFile(mode='rb', fileobj=io.BytesIO(html))
            return zfile.read()       
        else:
            return html
    
    def fetch(self, url):
        opener = urllib2.build_opener(SmartRedirectHandler(), urllib2.HTTPCookieProcessor())
        opener.addheaders = [(k, v) for k, v in self.header.items()]
        html, f, code = None, None, 0
        try:
            f = opener.open(url, timeout=15)
            redirect = f.url
            encoding = f.info().get('Content-Encoding')
            content_type = f.info().typeheader
            code = f.code
            s = f.info().type.lower() if f.info().type else ''
            if code == 200 and (s.startswith('text/html') or s.startswith('text/xhtml')):
                html = self.content_decode(f.read(), encoding)
        except IOError, e:
            if e.code == 404:
                return None, url, e.code
            raise e
        finally:
            if f:
               f.close()
        return html, redirect, code

