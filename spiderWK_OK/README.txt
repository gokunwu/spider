0.爬虫功能
  定时从网站的四个频道抓取数据，并分析页面，提取网页标题正文，采集当天发布的信息
  网站：http://www.npc.gov.cn
  频道：
  全国人大  http://www.npc.gov.cn/npc/xinwen/syxw/node_238.htm
  上海市        http://www.npc.gov.cn/npc/xinwen/dfrd/sh/sh_xwbd.htm
  天津市        http://www.npc.gov.cn/npc/xinwen/dfrd/tj/tj_xwbd.htm
  重庆市        http://www.npc.gov.cn/npc/xinwen/dfrd/chongqing/chq_xwbd.htm
  省区      http://www.npc.gov.cn/npc/xinwen/dfrd/node_11394.htm

1.运行环境
  1).Python2.7
    需要安装以下Python模块
    PyMySQL(https://github.com/petehunt/PyMySQL/)
    SQLAlchemy-0.7.6(http://www.sqlalchemy.org/download.html)
    html5lib-0.95(http://code.google.com/p/html5lib/downloads/list)
    beautifulsoup4-4.0.5(http://www.crummy.com/software/BeautifulSoup/#Download)
    chardet-2.1.1
    MySQL-python-1.2.3
  2).MySQL
2.数据库设置
  config.py
  MYSQL_HOST  =        '127.0.0.1'
  MYSQL_USER  =       'test'
  MYSQL_PASS  =       'test'
  MYSQL_DB    =       'test'
