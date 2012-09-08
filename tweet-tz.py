#!/usr/bin/env python
# encoding: utf-8

#import sys
#import os
import icalendar
import pytz
#import twitter
#import tweetcal_keys as keys
#import tweepy

FILENAME = 'tweets.ics'


def main():
    contents = open(FILENAME, 'rb').read()
    cal = icalendar.Calendar.from_ical(contents)
    comps = cal.walk()

    for c in comps[1:10]:
      start = icalendar.prop.vDDDTypes.from_ical(c['DTSTART'])
      newstart = start.replace(tzinfo=pytz.UTC)
      print type(newstart)

      #c['dtend'] = c['dtend'].replace(tzinfo=pytz.UTC)

if __name__ == '__main__':
    main()
