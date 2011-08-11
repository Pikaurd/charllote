#!/usr/bin/pyton3
# -*- coding: utf8 -*-

####
# Created : 2011/05/25 17:25
# Modified: Sat Jul 16 03:27:36 UTC 2011
####

import datetime
import re
try:
  from lxml import etree
except ImportError:
  import xml.etree.ElementTree as etree
  
from inspect import currentframe, getframeinfo
from urllib.request import urlopen

__version__ = (0, 1, 3)

def stringToFile(content, filepath, fileEncoding='utf-8'):
  '''
  A method to save string to a file
  @Param content -> to save string
  @Param filepath -> where to save the file and filename
  @Param encoding -> specified file encoding
  '''
  with open(filepath, mode='w', encoding=fileEncoding) as a_file:
    a_file.write(content)

def getWebFileHandle(url):
  return urlopen(url)

def getContentByURL(url):
  content = None
  with urlopen(url) as conn:
    content = conn.read()
  return content

def toUTF8(bytes):
  return bytes.decode('utf-8')

def queryStmt(query, debug=False):
  pattern = 'select {} {} {} _available = \'true\' {}'
  columns = ''
  conditions = ''
  oper = 'where'
  if query.startswith('from'):
    columns = '*'
  if ' where ' in query:
    oper = 'and'
  if 'order by' in query:
    conditionPos = query.find('order by')
    conditions = query[conditionPos:]
    query = query[:conditionPos]
  sql = pattern.format(columns, query, oper, conditions)
  if debug:
    print('>>from queryStmt debug info<<<')
    print(sql)
    print('columns: {}\tquery: {}\toper: {}\tcondition: {}'.format(columns, query, oper, conditions))
  return sql
  

def str2Time(s, tFormat='%a, %d %b %Y %H:%M:%S'):
  '''
  Date format: Fri, 27 May 2011 14:58:59 +0800
  to datetime
  '''
  if type(s) is datetime.datetime:
    return s
  if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', s) != None:
    tFormat = '%Y-%m-%d %H:%M:%S'
  utcOffset = datetime.timedelta(hours=0)
  try:
    if s[-5] == '+' or s[-5] == '-':
      utcOffset = datetime.timedelta(hours=int(s[-4:-2]))
      s = s[:-6]
    dTime = datetime.datetime.strptime(s, tFormat) - utcOffset
  except ValueError:
    print('[>>>ERROR<<<<]\tdata:{}\tFormat: {}'.format(s, tFormat))
  return dTime
  
def time2Str(d):
  return d.strftime('%Y-%m-%d %H:%M:%S')

#def timeToSqltite3UTCTime(t):
#  return datetime.datetime.strftime(s, '%Y-%m-%d %H:%m:%S')

def listPrint(alist, tag='D', sep='\n', fetchF=None):
  buffer = ''
  if fetchF == None:
    for e in alist:
      buffer += '[{tag}]{content!s}{sep}'.format(tag=tag, content=e, sep=sep)
  else:
    if tag ==  'seq':
      for i, e in enumerate(alist, 0):
        buffer += '[{}]{}{}'.format(i, fetchF(e), sep)
    else:
      for e in alist:
        buffer += '[{}]{}{}'.format(tag, fetchF(e), sep)
  return buffer

def listUnique(alist, key=lambda x:x):
  result = []
  keysOfResult = []
  for e in alist:
    ekey = key(e)
    if ekey not in keysOfResult:
      result.append(e)
      keysOfResult.append(key(e))
  return result

def listSub(alist, blist):
  '''
  return a list contains element of alist but blist
  '''
  return [ e for e in alist if e not in blist ]

def dprint(msg):
  curFrame = currentframe()
  lineno = curFrame.f_back.f_lineno
  filename = getframeinfo(curFrame).filename
  print(('[D]F:{} no:{}'+msg).format(filename, lineno))

def escapeHTMLtag(x):
  escapeTable = {
                  '&amp;' : '&',
                  '&lt;'  : '<',
                  '&gt;'  : '>'
                }
  for e in escapeTable.keys():
    x = x.replace(e, escapeTable.get(e))
  return x

class FeedParser:
  def __init__(self):
    self.tree = None
  
  def parse(self, fileHandle):
    with fileHandle as rsc:
      self.tree = etree.parse(rsc)
    return self.tree

  def parse(self, file=None, url=None):
    if file:
      with open(file) as res:
        self.tree = etree.parse(res)
    else:
      with getWebFileHandle(url) as res:
        self.tree = etree.parse(res)
    return self.tree
      
  def findall(self, query):
    return self.tree.findall(query)
    
  def find(self, query):
    return self.tree.find(query)

class CacheIsEmptyError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)

import unittest
class Test(unittest.TestCase):
  def test_listPrint(self):
    self.assertEqual('[D]1\n', listPrint([1]))
    self.assertEqual('[I]1\n', listPrint([1], 'I'))
    self.assertEqual('[I]1\t', listPrint([1], 'I', sep='\t'))
    self.assertEqual('[D]1\t', listPrint([1], sep='\t'))
    self.assertEqual('[D]1\n', listPrint([('a',1)], fetchF=lambda x:x[1]))

  def test_ListSub(self):
    alist = [1,2,3,4,5]
    blist = [2,4,6,8]
    self.assertListEqual([1,3,5], listSub(alist, blist))

  def test_EscapeHTMLtag(self):
    self.assertEqual('★御宅千夏&DHR動研★ [神樣DOLLS]', escapeHTMLtag('★御宅千夏&amp;DHR動研★ [神樣DOLLS]'))

  def test_uniquqList(self):
    self.assertListEqual([1,2,3], listUnique([1,1,2,1,3]))
    self.assertListEqual([(1,1)], listUnique([(1,1),(2,1),(3,1),(4,1)], lambda x:x[1]))

  def test_str2Time(self):
    self.assertEqual(datetime.datetime(2011,5,27,6,58,59) , str2Time('Fri, 27 May 2011 14:58:59 +0800'))
    self.assertEqual(datetime.datetime(2011,5,27,14,58,59) , str2Time('2011-05-27 14:58:59', '%Y-%m-%d %H:%M:%S'))
#    self.assertEqual(datetime.datetime(2011,7,12,22,23,26) , str2Time('Tue, 12 Jul 2011 22:23:26 +0800'))

  def test_queryStmt(self):
    expect = 'select * from a  where _available = \'true\' order by id desc limit 1'
    real = queryStmt('from a order by id desc limit 1')
    self.assertEqual(expect, real)
    self.assertEqual('select * from a where _available = \'true\' ', queryStmt('from a'))
    self.assertEqual('select  a from b where 1=1 and _available = \'true\' ', queryStmt('a from b where 1=1'))

if __name__ == '__main__':
  unittest.main()
