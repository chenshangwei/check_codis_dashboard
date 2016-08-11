#!/usr/bin/env python
#coding:utf-8
# pip install kazoo==2.0   #kazoo2.21使用了six模块在python2.7下有问题，故使用kazoo2.0版本
'''
    pip安装模块警告InsecurePlatformWarning: A true SSLContext object is not available.
    解决方法见：http://blog.csdn.net/henulwj/article/details/48131393/
    
         首先安装Python-devel libffi-devel openssl-devel
            yum install python-devel libffi-devel openssl-devel
         之后在安装pyopenssl ndg-httpsclient pyasn1
            pip install pyopenssl ndg-httpsclient pyasn1
'''
# https://github.com/chenshangwei/check_codis_dashboard/

'''
   检测codis中的dashboard进程
       如果该进程挂掉，则重启它
           因为zookeeper的缘故，在重启之前需要将zk中的dashboard信息delete掉
   python check_dashboard.py
   使用前，
     配置zk连接信息与dashboard命令
'''
import sys
import logging
import urllib2
import subprocess
import time
from kazoo.client import KazooClient

zk_hosts = "192.168.1.200:2181"
zk_dashboard = "/zk/codis/db_120ask/dashboard"
dashboard_addr = "192.168.1.200:18087"

dashboard_command = "/home/go/src/github.com/CodisLabs/codis/bin/codis-config -c /home/go/src/github.com/CodisLabs/codis/config.ini -L /home/go/src/github.com/CodisLabs/codis/logs/dashboard.log dashboard --addr " + str(dashboard_addr) + " &"

codisha_command = "/home/go/src/github.com/ngaut/codis-ha/codis-ha -codis-config=" + str(dashboard_addr) + " -productName=120ask &"

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(message)s',
                datefmt='%Y-%b-%d %H:%M:%S',
                filename='/root/tools/check_dashboard.log', #日志文件
                filemode='ab')

def delDashboard():
   zk = KazooClient(hosts=zk_hosts)
   zk.start()
   if zk.exists(zk_dashboard):
      if zk.delete(zk_dashboard):
         logging.info("[success] delete %s" % zk_dashboard)     
   zk.stop()

def runDashboard():
   recode = subprocess.call(dashboard_command,shell=True)
   if recode == 0:
      logging.info("[success] start dashboard")
      return True
   else:
      logging.info("[fail] start dashboard")
      return False
def runCodisHA():
   time.sleep(5) #等待dashboard启动
   recode = subprocess.call(codisha_command,shell=True)
   if recode == 0:
      logging.info("[success] start codis-ha")
      return True
   else:
      logging.info("[fail] start codis-ha")
      return False
def check():
   url =  "http://"+str(dashboard_addr)+"/api/overview"
   try:
      request = urllib2.Request(url)
      response = urllib2.urlopen(request)
      return True
   except Exception,e:
      return False

if __name__ == '__main__':
   if check():
      print "dashboard is ok"
      sys.exit(0)
   delDashboard()  #删除zk中的dashboard信息
   runDashboard()  #启动dashboard
   #runCodisHA()   #可选 启动codis-ha
