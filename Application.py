#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Mon Jul 18 09:25:07 UTC 2011
# Modified :
###

import os

from myutil import listSub
from myutil import listPrint
from myutil import listUnique
from Operators import ResourceOperator
from Operators import FeedFilter
from Operators import FeedReader


class Application:
  __version__ = (0, 1, 1)
  def __init__(self):
    self.resOper = ResourceOperator()
    self.feedFilter = FeedFilter()
    self._initCache()

  def _initCache(self):
    self.resOper.getFeedResUpdateTime()
    self.resOper.fillCache()

  def readCommand(self, results):
    def getArg(x):
      return int(x.split(' ')[-1])
    try:
      cmd = input()
      while (cmd != 'exit'):
        if cmd.startswith('c'):
          os.system('open {!r}'.format(results[0][getArg(cmd)].link))
        elif cmd.startswith('d'):
          print('Not implement')
        elif cmd == 'add filter':
          self.addNewFilter()
        elif cmd == 'filtered':
          self._showResult(results[1])
        elif cmd == 'show':
          self._showResult(results[0])
        cmd = input()
    except EOFError:
      print('Bye~')

  def addNewFilter(self):
    print('Input reason tag.{tag 1 and 4 is must filter}')
    cmd = input().split(' ')
    reason = cmd[0]
    tag = cmd[1]
    print('Reason: {}\tTag: {}\nconfirm?'.format(reason,int(tag)))
    if input() != 'no':
      self.resOper.addFilterPattern(reason, tag)
    else:
      print('cancled')

  def fetchingRes(self):
    nodes = []
    for feedRes in self.resOper.getFeedResource():
      reader = FeedReader(feedRes)
      newNodes = reader.getFeedItems(isFetchExist=False)
      if len(newNodes) == 0:
        print('[Info] skip feeds {}'.format(feedRes.id), end='\t')
        continue
      nodes += newNodes
    nodes = listUnique(nodes, lambda x:x.title)
    validFeeds = self.feedFilter.filterFeeds(nodes)
    filtered = listSub(nodes, validFeeds)
    self._writeToDB(validFeeds, filtered)
    return (validFeeds, filtered)

  def _showResult(self, xs):
    print('\n{} feed(s) updated'.format(len(xs)))
    print(listPrint(xs, 'seq', fetchF=lambda x:x.title))

  def _writeToDB(self, valid, filtered):
    self.resOper.writeValid(valid)
    self.resOper.writeFiltered(filtered)

  def run(self, mode='normal'):
    if mode == 'init':
      self.fetchingRes()
    elif mode != 'normal':
      print('Welcom to Charllote Rss Reader. ')
      self.readCommand([])
    else:
      print('Now fetching resources')
      results = self.fetchingRes()
      self._showResult(results[0])
      print('Instruction:\nc x:Open browser to check no x\nd x:Direct download specified feed with defualt dowloader\n')
      self.readCommand(results)
        

if __name__ == '__main__':
  import sys
  mode = 'normal'
  if len(sys.argv) > 1:
    if sys.argv[1] == "--init":
      mode = "init"
    else:
      mode = 'skip'
  Application().run(mode)
