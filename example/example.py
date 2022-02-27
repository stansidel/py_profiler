#! /usr/bin/env python
# -*- coding: utf-8 -*-

from random import random
from profiler import Profiler
import time

class Example:
    def __init__(self, profiler):
        self.__profiler = profiler or Profiler()
    
    def run_loop(self):
        run_uid = self.__profiler.start('run_loop')
        for i in range(10):
            loop_uid = self.__profiler.start('loop')
            time.sleep(int(random() * 3))
            self.__profiler.stop(loop_uid)
            print('Iteration ' + str(i + 1))
        self.__profiler.stop(run_uid)

