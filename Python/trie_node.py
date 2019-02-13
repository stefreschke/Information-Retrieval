# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:21:13 2019

@author: jonas
"""

from node import Node

class TrieNode(Node):
    
    def __init__(self, key):
        super().__init__()
        self._key = key
        self._docIDs = set()
    
    def insert(self, str, docID):
        if str == "":
            self._docIDs.add(docID)
            return
        char = str[0]
        rest = str[1:]
        if char in self._keyList:
            ind = self._keyList.index(char)
            self._nodeList[ind].insert(rest, docID)
            return
        else:
            node = TrieNode(char)
            self._nodeList.append(node)
            self._keyList.append(char)
            node.insert(rest, docID)
            return
            
    def find(self, str):
        if str == "":
            return self._docIDs
        char = str[0]
        rest = str[1:]
        if char in self._keyList:
            ind = self._keyList.index(char)
            return self._nodeList[ind].find(rest)
        else:
            raise Exception("No such key")
        