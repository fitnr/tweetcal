#!/usr/bin/env python
# encoding: utf-8
"""
tweetcal.py

Created by neil on 2012-06-09.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

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

# Constants
# Todo: change to argument
FILENAME = 'tweets.ics'


def get_latest_id(calendar):
    components = calendar.walk()
    latest = components[-1]
    return latest['id_str']


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=30)
    return start, end


def create_event(tweet):
    """Has a problem with \u221a\xa9"""
    event = icalendar.Event()

    #text = icalendar.prop.vText(tweet.text).to_ical()
    start, end = parse_date(tweet.created_at)

    try:
        event['summary'] = tweet.text
        event.add('description', 'http://twitter.com/' + tweet.user.screen_name + '/' + tweet.id_str)
        event.add('dtstart', start)
        event.add('dtend', end)
        event['uid'] = tweet.id_str + '@fakeisthenewreal'
        event['id_str'] = tweet.id_str

    except Exception, e:
        print e
        print tweet.text
        print tweet.id_str
        print tweet.created_at
    else:
        return event


def main():
    contents = open(FILENAME, 'rb').read()

    # Open calendar file
    cal = icalendar.Calendar.from_ical(contents)

    try:
        #last_id = get_latest_id(cal)

        # Auth and check twitter
        #auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
        #auth.set_access_token(keys.access_token, keys.access_token_secret)
        #api = tweepy.API(auth)

        #tweets = api.user_timeline(since_id=last_id, count=200)
        #tweets = api.user_timeline(since_id=210468705950384129, max_id=218349282380623871, count=200)

        p = open('pickletweets.pickle', 'rb')
        tweets = pickle.load(p)

        print "[tweetcal] fetched " + str(len(tweets))

        # Reverse so that the last shall be first
        tweets.reverse()

        for tweet in tweets:
            event = create_event(tweet)
            cal.add_component(event)
            most_recent = tweet.text

        ical = cal.to_ical()
        f = open(FILENAME, 'wb')
        f.write(ical)
        f.close()

        print '[tweetcal] Inserted some tweets. Most recent was: ' + most_recent

    except Exception, e:
        f = open(FILENAME, 'wb')
        f.write(contents)
        print e
        raise

if __name__ == '__main__':
    main()
