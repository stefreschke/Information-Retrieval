# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 17:22:19 2019

@author: jonas
"""

from trie_start_node import TrieStartNode

class Trie:
    def __init__(self):
        self._startNode = TrieStartNode()
        
    def insert(self, str, docID):
        self._startNode.insert(str, docID)
        
    def find(self, str):
        return self._startNode.find(str)
    
    

trie = Trie()
trie.insert("Test", 1)
trie.insert("Penis", 3)
print(trie.find("Test"))