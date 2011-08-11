#!/usr/bin/python3
# -*- coding: utf8 -*-

###
# Created : 2011-05-26 22:16
# Modified: 2011-07-12 17:30
###

import unittest
import sqlite3

class DBOperationOfSqlite3:
  __conn = None
  def __init__(self, dbpath):
    self.dbPath = dbpath

  def connect(self):
    DBOperationOfSqlite3.__conn = sqlite3.connect(self.dbPath)

  def close(self):
    self.__close(DBOperationOfSqlite3.__conn)

  def select(self, query):
    c = self.__execute(query)
    resultSet = [ r for r in c ]
    self.__close(c)
    return resultSet

  def executeDML(self, sqlScript):
    self.__close(self.__execute(sqlScript))
    DBOperationOfSqlite3.__conn.commit()

  def __execute(self, sqlScript):
    c = DBOperationOfSqlite3.__conn.cursor()
    c.execute(sqlScript)
    return c

  def __close(self, closeable):
    closeable.close()
    
  


class TestDBOperation(unittest.TestCase):
  def setUp(self):
    self.conn = DBOperationOfSqlite3('orient.sqlite3.db')
    self.conn.connect()

  def tearDown(self):
    self.conn.close()

  def test_select(self):
    self.assertIsNotNone(self.conn)

  def test_select(self):
    self.assertEqual(5,len(self.conn.select('select * from feed_info')))

if __name__ == '__main__':
  unittest.main()
