#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Tue Jul 12 09:22:42 UTC 2011
# Modified :
###

import datetime
import re
import os

from pikaurdlib.util import decodeXMLContent
from pikaurdlib.util import str2Time
from pikaurdlib.util import time2Str
from pikaurdlib.util import CacheIsEmptyError

dateFormat = '%Y-%m-%d %H:%M:%S'

class FeedItem:
  def __init__(self, title, pubDate, link='', fromId=0):
    self.fromFeedId = fromId
    self.title = decodeXMLContent(title)
    self.pubDate = time2Str(str2Time(pubDate))
    self.link = link

  def insertStmt(self):
    sql = 'insert into feeds (from_feed_id, title, link, time) values({!r},{!r},{!r},{!r})'
    return sql.format(self.fromFeedId, self.title, self.pubDate, self.link)
#  def _formalDate(self, pubDate):

  def __eq__(self, x):
    return self.title == x.title

  def __str__(self):
    return 'Title: {}\tPubDate: {}\tLink: {}'.format(self.title, self.pubDate, self.link)
    
  def isUpdated(self, oldTime):
    return oldTime < str2Time(self.pubDate, dateFormat)

  def isNew(self):
    return Cache.isNotExist(self)

class Tags:
  def __init__(self, title, id=0):
    self.title = title
    self.id = id
    
class FeedResUpdateTime:
  cache = {}
  def __init__(self, feedId, updateTime):
    FeedResUpdateTime.cache[feedId] = str2Time(updateTime, dateFormat)

  @staticmethod
  def get(feedId):
    updateTime = FeedResUpdateTime.cache.get(feedId)
    if updateTime == None:
      updateTime = datetime.datetime(2011, 1, 1, 12, 0, 0)
#      updateTime = '2011-01-01 12:00:00'
    return updateTime

class FeedRes:
  def __init__(self, url, tag, description, id, pubDate=''):
    self.url = url
    self.tag = tag
    self.desc = description
    self.id = id
    if type(pubDate) is str:
      pubDate = str2Time(pubDate)
    self.pubDate = pubDate

  def __str__(self):
    return 'ID: {}\turl: {}\t PubDate: {}'.format(self.id, self.url, self.pubDate)

  def isUpdated(self, curTime):
    return curTime > self.pubDate

class Cache:
  _cache = {}
  
  @staticmethod
  def update(feed):
    Cache._cache[feed.title] = True

  @staticmethod
  def isExist(feed):
    if Cache.size() == 0:
      raise CacheIsEmptyError('Cache is empty')
    return Cache._cache.get(feed.title) != None

  @staticmethod
  def size():
    return len(Cache._cache)
    
  @staticmethod
  def clear():
    Cache._cache = {}

  @staticmethod
  def isEmpty():
    return Cache.size() == 0

class FilterReason:
  def __init__(self, content, type, createTime, id=0):
    self.content = content
    self.type = type
    self.createTime = createTime
    self.id = id

  def isMustFilter(self):
    return self.type == 1 or self.type == 4


# Mock
class MockFeedItem(FeedItem):
  def __init__(self,title='', pubDate='Tue, 12 Jul 2011 22:23:26 +0800', link='',fromId=''):
    FeedItem.__init__(self, title, pubDate, link, fromId)

# UnitTest
import unittest
class TestFeedResUpdateTime(unittest.TestCase):
  def setUp(self):
    FeedResUpdateTime(0, '2011-01-01 12:01:01')

  def test_get(self):
    self.assertEqual(datetime.datetime(2011,1,1,12,1,1), FeedResUpdateTime.get(0))

class TestCache(unittest.TestCase):
  def test_updateCache(self):
    Cache.clear()
    self.assertEqual(0, Cache.size())
    Cache.update(MockFeedItem('koi'))
    self.assertEqual(1, Cache.size())

  def test_isExist(self):
    Cache.clear()
    Cache.update(MockFeedItem('koi'))
    self.assertTrue(Cache.isExist(MockFeedItem('koi')))
    self.assertFalse(Cache.isExist(MockFeedItem('daisuki')))

  def test_clear(self):
    Cache.update(MockFeedItem('koi'))
    self.assertLess(0, Cache.size())
    Cache.clear()
    self.assertEqual(0, Cache.size())
    
  @unittest.expectedFailure
  def test_isExistFailure(self):
    Cache.isExist('')
    

if __name__ == '__main__':
  unittest.main() 
