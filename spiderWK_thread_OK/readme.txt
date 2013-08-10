0.功能介绍:
  a).从入口url开始，根据采集白名单、黑名单按广度优先规矩采集。
  b).修改"采集白名单、黑名单"后快速重新生成待采任务列表
  c).采集结果保存到MySQL
  d).中间数据保存到MongoDB
  e).多机并行采集
  
1.运行环境
  1).Python2.7
     需要安装以下Python模块
     SQLAlchemy-0.7.6(http://www.sqlalchemy.org/download.html)
     html5lib-0.95(http://code.google.com/p/html5lib/downloads/list)
     beautifulsoup4-4.0.5(http://www.crummy.com/software/BeautifulSoup/#Download)
     chardet-1.0.1(http://pypi.python.org/pypi/chardet)
     pymongo-2.2(http://pypi.python.org/pypi/pymongo/)
  2).MySQL
  3).MongoDB 2.0.4

3.数据库设置
  config.py
  MYSQL_HOST  =        '127.0.0.1'
  MYSQL_USER  =       'test'
  MYSQL_PASS  =       'test'
  MYSQL_DB    =       'test'
  
  MONGODB_HOST   =    '127.0.0.1'
  MONGODB_PORT   =     27017

4.采集规矩
  1).定时更新、强制更新的url列表
  WATCH_URL_FILE    = 'url/watch.txt'
  UPDATE_URL_FILE   = 'url/update.txt'

  2).符合规则的url才采集
  DOWN_URL_RE_BLACK = 're/down.black'
  DOWN_URL_RE_WHITE = 're/down.white'
  
  3).保留符合规则的url,供采集规则修改后重新计算采集任务
  SAVE_URL_RE_BLACK = 're/save.black'
  SAVE_URL_RE_WHITE = 're/save.white'
  
  4).多机采集时，只能其中一个设置MASTER=True
5.开始采集
  python  spider.py

快速启动:
   1.装mysql,python,mongodb
   2.在config.py里修改mysql的账户密码(MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   3.在url/watch.txt里加种子url
   4.运行python  spider.py
   