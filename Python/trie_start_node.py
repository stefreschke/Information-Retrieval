# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:38:58 2019

@author: jonas
"""

from node import Node
from trie_node import TrieNode

class TrieStartNode(Node):
    
    def __init__(self):
        super().__init__()
        
    def insert(self, str, docID):
        char = str[0]
        rest = str[1:]
        if str == "":
            raise Exception("Empty string not allowed as key")
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
            raise Exception("Can't search for empty string")
        char = str[0]
        rest = str[1:]
        if char in self._keyList:
            ind = self._keyList.index(char)
            return self._nodeList[ind].find(rest)
        else:
            raise Exception("No such key")