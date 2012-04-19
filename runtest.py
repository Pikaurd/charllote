#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Tue Jul 12 09:15:47 UTC 2011
# Modified :
###

import re
import unittest

from Operators import FeedReader
from Operators import FeedFilter
from Operators import ResourceOperator
from pikaurdlib.util import *

from Entities import Cache
from Entities import FeedRes
from Entities import FeedResUpdateTime
from Entities import MockFeedItem

class TestFeedParser(unittest.TestCase):
  def setUp(self):
    self.feedFetcher = FeedParser()
#    self.feedFetcher.parse(url='http://manhua.178.com/u/usagidrop/rss.xml')
    self.feedFetcher.parse(file='rss.xml')

  def test_findall(self):
    a = self.feedFetcher.findall('.//item')
    self.assertEqual(5, len(a), 'length not equals')

class TestFeedReader(unittest.TestCase):
  def setUp(self):
    feedRes = FeedRes('rss.xml', 'tag', 'description', 0, 'Sat, 1 Jan 2011 22:23:26 +0800')
    self.feedReader = FeedReader(feedRes)

  def tearDown(self):
    pass
  
  def test_FeedItems(self):
    items = self.feedReader.getFeedItems()
    expect = ['http://www.178.com/mh/usagidrop/14596.shtml?from=rssReader',
              'http://www.178.com/mh/usagidrop/14445.shtml?from=rssReader']
    self.assertEqual(expect[0], items[0].link)
    self.assertEqual(expect[1], items[1].link)

  def test_FeedItems2(self):
    items = self.feedReader.getFeedItems(FeedReader.noDuplicate)
    #items = self.feedReader.getFeedItems()
    expect = ['http://www.178.com/mh/usagidrop/14596.shtml?from=rssReader',
              'http://www.178.com/mh/usagidrop/14445.shtml?from=rssReader']
    print('print ' + listPrint(items))
    self.assertEqual(expect[0], items[0].link)
    self.assertEqual(expect[1], items[1].link)

#  def test_FillFeedResDate(self):
#    self.assertTrue(self.feedReader.fillFeedResPubDate())

  @unittest.skip('skip tmp test')
  def test_tmpTest(self):
    resOper = ResourceOperator('/dev.sqlite3.db')
    for feedRes in resOper.getFeedResource():
      feedReader = FeedReader(feedRes)
      self.assertTrue(feedReader.fillFeedResPubDate())

class TestFeedFilter(unittest.TestCase):
  def setUp(self):
    self.filter = FeedFilter() 
#   self.reader = FeedReader('http://manhua.178.com/u/usagidrop/rss.xml')

  def tearDown(self):
    self.filter = None

  def test_filterFeedsExp(self):
    li = [
           MockFeedItem('[枫雪动漫][Hoshizora e Kakaru Hashi 架向星空之桥][12][RMVB+MKV]'),
           MockFeedItem('【旋风字幕组】死神Bleach 第330话「想要活下去！望实的斩魂刀」【RMVB】简体 848x480'), 
           MockFeedItem('动漫之家[DmzJ字幕组][7月新番][Natsume_Yuujinchou_San_夏目友人帐_第三季][02][HDTV][rmvb+mkv]'),
           MockFeedItem('【SOSG字幕团】★4月新番【银魂 Gintama】【第216话】[简体MP4][720p][HDTV]【替代RMVB，享受高清】(RMVB全面停压淘汰)'),
           MockFeedItem('【SOSG字幕團】★4月新番【銀魂 Gintama】【第216話】[繁體MP4][480p][HDTV]【替代RMVB，享受便捷】(RMVB全面停壓淘汰)'),
           MockFeedItem('【异域字幕组】★【7月新番】[夏目友人帐 参][Natsume Yuujinchou San][02][720P][简体][MKV]'),
           MockFeedItem('【AcgmTHK字幕組&K2字幕組】★七月新番【神様のメモ帳 神的記事本】[02][繁體][576P&720P][RV10&Mp4][Http下載、內詳]')
         ]
    result = self.filter.filterFeeds(li)
    errorMsg = listPrint(result)
    self.assertEqual(4, len(result), errorMsg)

  @unittest.skip('reality test skip')
  def test_filterFeeds(self):
    feedRes = FeedRes('popgo.xml', 'tag', 'description', 0, 'Tue, 12 Jul 2011 22:23:26 +0800')
    self.reader = FeedReader(feedRes)
    feeds = self.reader.getFeedItems()
    filtered = self.filter.filterFeeds(feeds)
    filteredLength = len(filtered)
    notFilterLength = len(feeds)
    print('Before: {}\tAfter: {}'.format(notFilterLength, filteredLength))
    f = lambda x:x.title
    print('Filtered -----------\n{}Not filtered ----------\n{}'.format(listPrint(listSub(feeds, filtered), fetchF=f), listPrint(filtered, fetchF=f)))
    self.assertTupleEqual((35, 18), (notFilterLength, filteredLength))

#@unittest.skip("Test another skipping")
class TestResourceOperator(unittest.TestCase):
  def setUp(self):
    self.resOper = ResourceOperator('/dev.sqlite3.db')
    feedRes = FeedRes('popgo.xml', 'tag', 'description', 0, 'Tue, 12 Jul 2011 22:23:26 +0800')
    self.reader = FeedReader(feedRes)

  def tearDown(self):
    self.resOper = None

  @unittest.skip("insert skipping")
  def test_addFilterPattern(self):
    reason = '异域字幕组'
    tag = 1
    self.resOper.addFilterPattern(reason, tag)

  def test_getFilterPattern(self):
    patterns = [
                '480',
                '1024'
               ]
    tmpList = self.resOper.getFilterPattern()
    realList = []
    realList.append(tmpList[0].content)
    realList.append(tmpList[1].content)
    self.assertListEqual(patterns, realList)

  def test_getFeedResource(self):
    real = self.resOper.getFeedResource()
#    print(listPrint(real))
    self.assertEqual(2, real[1].id)
    self.assertEqual(7, len(real))

  @unittest.skip("insert skipping")
  def test_addAndGetFeedResUpdateTime(self):
    feedRes = self.reader.feedRes
    self.resOper.addFeedResUpdateTime(feedRes)
    self.resOper.getFeedResUpdateTime()# add data in FeedReaUpdateTime.Cache
    self.assertLessEqual(feedRes.pubDate, FeedResUpdateTime.get(feedRes.id))

  def test_getFeeds(self):
    feeds = self.resOper.getFeeds()
    self.assertLessEqual(0, len(feeds))

  def test_fillCache(self):
    self.resOper.fillCache()
    self.assertLessEqual(0, Cache.size())


if __name__ == '__main__':
  unittest.main()

