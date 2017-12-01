#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys, os, re, bisect
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, FuncFormatter
import numpy as np
from datetime import datetime
import json
import argparse

####################################################################################################
class UserChatStat:
  def __init__(self, name):
    assert len(name) != 0
    self.name = name
    self.dt = datetime.now()
    self.total = 0
    # dict of list of hour bins 24
    self.data = dict()

  def addMessage(self, time, text):
    self.total += 1
    #
    if self.data.get(time.date()) is None:
      self.data[time.date()] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
      assert len(self.data[time.date()]) == 24

    l = self.data[time.date()]
    l[time.time().hour] += 1

  def appendMessage(self, time, text):
    pass

  def plotDayHists(self):
    for k, v in self.data.items():
      print(k, ':', v)

      fig = plt.figure(figsize=(8, 8))
      ax = fig.add_subplot(111);
      ax.grid(linestyle='--', linewidth=0.5, color='.25', zorder=-10)
      ax.set_title(str(k) +' of ' + self.name, fontsize=20, verticalalignment='bottom')
      ax.set_xlabel('Hours of the day. (UTC+1) Stockholm time')
      ax.set_ylabel('Amount of messages')
      ax.xaxis.set_minor_locator(AutoMinorLocator(5))
      ax.bar(range(len(v)), v, width=0.9, align='edge')
      fig.savefig(self.name + str(k) + '.png')
      plt.close(fig)

  def plotHist(self, interval='day'):
    if interval == 'day':
      pass

  def healthCheck(self):
    msgsum = 0
    for k in self.data:
      msgsum += np.sum(self.data[k])
    assert self.total == msgsum

  def describe(self):
    print(self.name, self.data)

####################################################################################################
def main(config, chatfile):

  with open(config) as cf:
    confDict = json.load(cf)

  nameMapping = confDict['nameMapping']
  assert nameMapping != None

  name_map = dict()
  for k in nameMapping:
    name_map[k['ident']] = k['alias']

  name2msg = dict()

  prog = re.compile('(\d\d/\d\d/\d\d),\s([0-9:]+)\s(AM|PM):\s([‪‬\(\)\+\s\w\d‑\-]+):(.*)')

  def process_result(name, ts, text, append=False):
    if name2msg.get(name) is None:
      name2msg[name] = UserChatStat(name)
    if append:
      name2msg[name].appendMessage(ts, text)
    else:
      name2msg[name].addMessage(ts, text)
      name2msg['Chat'].addMessage(ts, text)


  with open(chatfile) as f:
    author_name = ''
    prev_author = ''
    msg_ts = None
    msg_ts_prev = None
    name2msg['Chat'] = UserChatStat('Chat')
    while True:
      line = f.readline()
      if not line:
        break
      result = prog.match(line)
      if result:
        msg_ts = datetime.strptime(result[1]+' '+result[2], '%m/%d/%y %I:%M:%S')
        if result[3] == 'PM':
          msg_ts = datetime(msg_ts.year, msg_ts.month, msg_ts.day, msg_ts.hour+12, msg_ts.minute, msg_ts.second)

        author_name = result[4]
        # map phone to name
        if result[4] in name_map:
          author_name = name_map[result[4]];

        if author_name != prev_author:
          process_result(author_name, msg_ts, result[5])
        else:
          stride = msg_ts_prev.timestamp() - msg_ts.timestamp()
          if stride > confDict['groupInterval']:
            process_result(author_name, msg_ts, result[5])
          else:
            process_result(author_name, msg_ts, line, True)

        msg_ts_prev = msg_ts
        prev_author = author_name
      else:
        if author_name != '':
          process_result(author_name, msg_ts, line, True)

  for key in name2msg:
    print(key, ':', name2msg[key].total)
    name2msg[key].healthCheck()

  name2msg['Chat'].plotDayHists()
  del name2msg['Chat']

  vals, keys = zip(*sorted(zip((z.total for z in name2msg.values()), name2msg.keys())))
  print('Total messages:', np.sum(vals))

  messageLimit = confDict['lowMessageLimit']
  print('Removing all less than ', messageLimit)
  idx = bisect.bisect(vals, messageLimit)
  keys = keys[idx:]
  vals = vals[idx:]

  y = np.arange(len(vals))

  fig = plt.figure(figsize=(8, 8))
  ax = fig.add_subplot(111);
  fig.subplots_adjust(left=0.25)
  ax.grid(linestyle='--', linewidth=0.5, color='.25', zorder=-10)
  ax.set_title('Member activity', fontsize=20, verticalalignment='bottom')
  ax.set_xlabel('Activity')
  ax.set_ylabel('Name')
  ax.xaxis.set_minor_locator(AutoMinorLocator(5))
  ax.barh(y, vals, height=0.9, tick_label=keys)
  fig.savefig('activity.png')
  plt.close(fig)



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('configfile', help='config file name')
  parser.add_argument('chatfile', help='chat file name')
  args = parser.parse_args()
  main(args.configfile, args.chatfile)
