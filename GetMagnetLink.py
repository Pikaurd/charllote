#!/usr/bin/pyhton3
# -*- coding: utf8 -*-

import re

from pikaurdlib.util import getContentByURL
from pikaurdlib.util import toUTF8
from pikaurdlib.util import decodeXML

def getMagnetLink(content):
  pattern = r'magnet:\?[0-9a-zA-Z=:&;./]+'
  magnetLink = re.findall(pattern, content)
  assert(len(magnetLink) == 1)
  return decodeXML(magnetLink[0])

def getMagnetLinkFromURL(url):
  content = toUTF8(getContentByURL(url))
  pattern = r'magnet:\?[0-9a-zA-Z=:&;./]+'
  magnetLink = re.findall(pattern, content)
  assert(len(magnetLink) == 1)
  return decodeXML(magnetLink[0])


##############################
#  Test Case                 #
##############################
import unittest

class TestMagnet(unittest.TestCase):
  def test_getMagnetLink(self):
    sample = '''<a href="http://wt.dl.bt.ktxp.com/down/1335588384/1b782caa65ee8edb706c20f2f1af6e25c802b635.torrent"><u>网通下载点</u></a>&nbsp;&nbsp;
                <a href="magnet:?xt=urn:btih:1b782caa65ee8edb706c20f2f1af6e25c802b635&amp;tr.0=http://tracker.ktxp.com:6868/announce&amp;tr.1=udp://tracker.ktxp.com:6868/announce" title="使用磁力链接下载这个资源"><u>磁力(Magnet Link)</u></a>
                                <p> '''
    expected = 'magnet:?xt=urn:btih:1b782caa65ee8edb706c20f2f1af6e25c802b635&tr.0=http://tracker.ktxp.com:6868/announce&tr.1=udp://tracker.ktxp.com:6868/announce'
    actual = getMagnetLink(sample)
    self.assertEqual(actual, expected)

if __name__ == '__main__':
  unittest.main()
