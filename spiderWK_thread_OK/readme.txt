0.���ܽ���:
  a).�����url��ʼ�����ݲɼ�����������������������ȹ�زɼ���
  b).�޸�"�ɼ���������������"������������ɴ��������б�
  c).�ɼ�������浽MySQL
  d).�м����ݱ��浽MongoDB
  e).������вɼ�
  
1.���л���
  1).Python2.7
     ��Ҫ��װ����Pythonģ��
     SQLAlchemy-0.7.6(http://www.sqlalchemy.org/download.html)
     html5lib-0.95(http://code.google.com/p/html5lib/downloads/list)
     beautifulsoup4-4.0.5(http://www.crummy.com/software/BeautifulSoup/#Download)
     chardet-1.0.1(http://pypi.python.org/pypi/chardet)
     pymongo-2.2(http://pypi.python.org/pypi/pymongo/)
  2).MySQL
  3).MongoDB 2.0.4

3.���ݿ�����
  config.py
  MYSQL_HOST  =        '127.0.0.1'
  MYSQL_USER  =       'test'
  MYSQL_PASS  =       'test'
  MYSQL_DB    =       'test'
  
  MONGODB_HOST   =    '127.0.0.1'
  MONGODB_PORT   =     27017

4.�ɼ����
  1).��ʱ���¡�ǿ�Ƹ��µ�url�б�
  WATCH_URL_FILE    = 'url/watch.txt'
  UPDATE_URL_FILE   = 'url/update.txt'

  2).���Ϲ����url�Ųɼ�
  DOWN_URL_RE_BLACK = 're/down.black'
  DOWN_URL_RE_WHITE = 're/down.white'
  
  3).�������Ϲ����url,���ɼ������޸ĺ����¼���ɼ�����
  SAVE_URL_RE_BLACK = 're/save.black'
  SAVE_URL_RE_WHITE = 're/save.white'
  
  4).����ɼ�ʱ��ֻ������һ������MASTER=True
5.��ʼ�ɼ�
  python  spider.py

��������:
   1.װmysql,python,mongodb
   2.��config.py���޸�mysql���˻�����(MYSQL_USER,MYSQL_PASS,MYSQL_DB)
   3.��url/watch.txt�������url
   4.����python  spider.py
   