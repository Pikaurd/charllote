#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Tue Jul 12 11:27:29 UTC 2011
# Modified :Sun Aug 13 14:22:31 UTC 2011
###

import datetime
import os
import re

from db import DBOperationOfSqlite3 as DBOper

from Entities import Cache
from Entities import FeedItem
from Entities import FeedRes
from Entities import FeedResUpdateTime
from Entities import FilterReason

from pikaurdlib.util import FeedParser
from pikaurdlib.util import queryStmt
from pikaurdlib.util import time2Str
from pikaurdlib.util import str2Time
from pikaurdlib.util import listPrint
from pikaurdlib.util import listUnique
from pikaurdlib.util import listSub
from pikaurdlib.util import CacheIsEmptyError
from pikaurdlib.util import EmptyObject

class FeedReader:
  def __init__(self, feedRes):
    self.isSkip = True
    self.feedParser = FeedParser()
    self.feedRes = feedRes
    self.initFeedParser(feedRes.url)

  def initFeedParser(self, url):
    if url.startswith('http'):
      self.feedParser.parse(url=url)
    else:
      self.feedParser.parse(file=url)
    if self.feedParser.isAvailable():
      self._fillFeedResPubDate()
    
  def getFeedItems(self, isFetchExist=True):
    items = []
    if self.isSkip and not isFetchExist:
      return items
    itemsRaw = self.feedParser.findall('.//item')
    for i in itemsRaw:
      feedItem = self._generateFeedItemFromNode(i)
      #print('data: {!s}\tdate:{}'.format(feedItem, FeedResUpdateTime.get(self.feedRes.id)))

      if isFetchExist or self._isFeedNew(feedItem):#feedIsNew:
        items.append(feedItem)
    return items

  def _generateFeedItemFromNode(self, node):
    title = self._getTextIfNotNone(node.find('title'))
    link = self._getTextIfNotNone(node.find('link'))
    pubDate = self._getTextIfNotNone(node.find('pubDate'))
    return FeedItem(title, pubDate, link, self.feedRes.id)
    
  def _isFeedNew(self, feedItem):
    try:
      feedIsNew = feedItem.isUpdated(FeedResUpdateTime.get(self.feedRes.id)) and not Cache.isExist(feedItem)
    except CacheIsEmptyError:
      ResourceOperator().fillCache()
    finally:
      if Cache.isEmpty():
        feedIsNew = feedItem.isUpdated(FeedResUpdateTime.get(self.feedRes.id))
      else:
        feedIsNew = feedItem.isUpdated(FeedResUpdateTime.get(self.feedRes.id)) and not Cache.isExist(feedItem)
    return feedIsNew

  def _fillFeedResPubDate(self):
    newPubDate = str2Time(self._getPubDate())
    #print('old: {}\tnew: {}'.format(self.feedRes.pubDate, newPubDate))
    if self.feedRes.isUpdated(newPubDate):
      self.feedRes.pubDate = newPubDate
      ResourceOperator().addFeedResUpdateTime(self.feedRes)
      self.isSkip = False
    #  print('skip feed: {}'.format(self.feedRes.url))

  def _getPubDate(self):
    pubDateNode = self.feedParser.find('.//lastBuildDate')
    if pubDateNode == None:
      pubDateNode = self.feedParser.find('.//pubDate')
    return pubDateNode.text 
    
  def _isUpdated(self, feedResId):
    return false

  def _getTextIfNotNone(self, element):
    if element is not None:
      return element.text
    else:
      return object()

class FeedFilter:
  def __init__(self):
    self.patterns = ResourceOperator().getFilterPattern()
    self._regexPattern()
  
  def _regexPattern(self):
    aListContainsAllPatterns = [e.content for e in self.patterns]
    mustFilter = [e.content for e in self.patterns if e.isMustFilter() ]
    self.patterns = '(?i)' + '|'.join(aListContainsAllPatterns)
    self.mustFilterPatterns = '(?i)' + '|'.join(mustFilter)
#   print("must filter patterns\t" + self.mustFilterPatterns)

  def filterFeeds(self, feeds):
    _isContainFilterReason = lambda x: len(re.findall(self.patterns, x)) > 0
    firstFilter = [ e for e in feeds if _isContainFilterReason(e.title) ]
    result = [e for e in firstFilter if self._isValid(e)]
    filteredFeeds = listSub(feeds, firstFilter) + result
    return filteredFeeds

  def _isValid(self, feed):
    _notIsMustFilter = lambda x: len(re.findall(self.mustFilterPatterns, x)) == 0
    _isValid = lambda x: len(re.findall('(?i)720p|1080|mkv|dvd', x)) > 0
    x = feed.title
    return _notIsMustFilter(x) and _isValid(x)

class ResourceOperator:
  def __init__(self, dbPath='/work.sqlite3.db'):
    pathPrefix = os.path.dirname(os.path.realpath( __file__ ))
    self.db = DBOper(pathPrefix + dbPath)
    self.db.connect()

  def addFilterPattern(self, reason, tag):
    sql = 'insert into reason_of_filtered(content, type_id, create_time) values({!r},{!r},{!r})'
    curTime = time2Str(datetime.datetime.now())
    self.db.executeDML(sql.format(reason, tag, curTime))

  def addFeeds(self, feeds):
    for feed in feeds:
      self.addFeed(feed)

  def addFeed(self, feed):
    self.db.executeDML(feed.insertStmt())

  def writeValid(self, feeds):
    self._writeFeeds(feeds, 'feeds')

  def writeFiltered(self, feeds):
    self._writeFeeds(feeds, 'feeds_filtered')

  def _writeFeeds(self, feeds, table):
    sql = 'insert into {} (from_feed_id, title, link, time) values ({!r},{!r},{!r},{!r})'
    for feed in feeds:
      self.db.executeDML(sql.format(table, feed.fromFeedId, feed.title, feed.link, feed.pubDate))

  def getFilterPattern(self):
    rs = self.db.select(queryStmt('from reason_of_filtered'))
    return [ FilterReason(e[1], e[2], e[3], e[0]) for e in rs ] 

  def getFeedResource(self):
#    feedResUpdateTime = self.getFeedResUpdateTime()
    rs = self.db.select(queryStmt('from feed_info'))
    return [ FeedRes(e[1], e[2], e[3], e[0], FeedResUpdateTime.get(e[0]) ) for e in rs ] 

  def addFeedResUpdateTime(self, feedRes):
    sql = 'insert into feed_update_time (feed_id, update_time) values ({!r}, {!r})'
    self.db.executeDML(sql.format(feedRes.id, time2Str(feedRes.pubDate)))

  def getFeedResUpdateTime(self):
    rs = self.db.select('select feed_id, update_time from feed_update_time group by feed_id')
    for r in rs:
      FeedResUpdateTime(r[0], r[1])
#    return { r[0]: r[1] for r in rs }

  def getFeeds(self, size=1000):
    rs = self.db.select(queryStmt('from feeds order by id desc limit '+str(size)))
    return [ FeedItem(r[2], r[4], r[3], r[1]) for r in rs ]

  def fillCache(self):
    for e in self.getFeeds(100):
      Cache.update(e)
    

