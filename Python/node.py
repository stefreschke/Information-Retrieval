# -*- coding: utf-8 -*-
"""
Created on Tue Feb 12 16:29:58 2019

@author: jonas
"""

from abc import ABC, abstractmethod

class Node(ABC):
    
    def __init__(self):
        self._keyList = []
        self._nodeList = []
        
    @abstractmethod
    def insert(self, str, docID):
        pass
    
    @abstractmethod
    def find(self, str):
        pass