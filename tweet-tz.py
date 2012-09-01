#!/usr/bin/env python
# encoding: utf-8

#import sys
#import os
import icalendar
import pytz
#import twitter
from datetime import timedelta
#import tweetcal_keys as keys
#import tweepy
import pickle
import codecs

def main():
    p = open('pickletweets.pickle', 'rb')
    tweets = pickle.load(p)

    t = tweets[0]
    print t.created_at
    print t.id_str
    aware = 
    print aware

if __name__ == '__main__':
    main()
