#! /usr/bin/env python
# -*- coding: utf-8 -*-

from example import Example
from profiler import Profiler

profiler = Profiler()
ex = Example(profiler=profiler)
ex.run_loop()

events = profiler.finished_events

stats = profiler.finished_events_stats
print(stats)
