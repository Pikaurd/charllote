#file: Charllote/sendlink.py

import re
import urllib.request, urllib.parse

from pikaurdlib.util import getContentByURL
from pikaurdlib.util import toUTF8

class SendLink4Transmission:
  __url__ = 'http://nas:4090/transmission/rpc'
  __addTorrent__ = '{{"method":"torrent-add", "arguments":{{"paused":false,"filename":"{torrent}"}}}}'

  def __init__(self):
    self.sessionID = None
    self.fillSessionID()

  def fillSessionID(self):
   # if self.sessionID is None:
    pattern = r'(?<=X-Transmission-Session-Id: )[\d\w]+'
    req = urllib.request.Request(SendLink4Transmission.__url__)
    try:
      urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
      assert(e.code == 409)
      content = toUTF8(e.read())
    self.sessionID = re.search(pattern, content).group()

  def sendlink(self, link):
    post = SendLink4Transmission.__addTorrent__.format(torrent=link)
    data = post.encode('utf8')
    req = urllib.request.Request(SendLink4Transmission.__url__, data)
    req.add_header('X-Transmission-Session-Id', self.sessionID)
    with urllib.request.urlopen(req) as s:
      print(s.read())
    
    
import unittest

class TestSendLink4Transmission(unittest.TestCase):
  def setUp(self):
    self.sendlink = SendLink4Transmission()

  def test_fillSessionID(self):
    self.sendlink.fillSessionID()
    self.assertIsNotNone(self.sendlink.sessionID)

  def test_sendlink(self):
    link = 'magnet:?xt=urn:btih:PKA5DXV7X4BZYH4BFQIWXCT6O3FAOPHL&tr=http://t2.popgo.org:7456/annonce'
    self.sendlink.sendlink(link)

if __name__ == '__main__':
  unittest.main()
