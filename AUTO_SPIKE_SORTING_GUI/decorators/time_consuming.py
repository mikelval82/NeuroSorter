#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 15 11:17:21 2021

@author: mikel
"""
import functools
import time

def timeit(func): 
    """
    A function wrapper for counting the time taken in a process
    """
    @functools.wraps(func)
    def inner(*args, **kwargs):
        begin = time.time() 
        result = func(*args, **kwargs) 
        end = time.time()
 
        time_consumed = "Total time taken in function " + func.__name__ + ': ' + '{0:.2f}'.format(end - begin)  + ' seconds'
        
        return [result, time_consumed]
  
    return inner
    


