#!/usr/bin/env python
# encoding: utf-8
"""
tweetcal.py

Created by neil on 2012-06-09.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.
"""

#import sys
#import os
from icalendar import Calendar, Event
import pytz
#import twitter
from datetime import timedelta
import tweetcal_keys as keys
import tweepy
import logging

# Constants
# Todo: change to argument
FILENAME = 'fitnr-new-tweets.ics'


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=30)
    return start, end


def create_event(tweet):
    event = Event()

    try:
        start, end = parse_date(tweet.created_at)
        desc = '<a href="http://twitter.com/{0}/{1}">tweet</a>'.format(tweet.user.screen_name, tweet.id_str)

        event.add('summary', tweet.text)
        event.add('description', desc)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('uid', '{0}@fakeisthenewreal'.format(tweet.id_str))
        event['id_str'] = tweet.id_str

    except Exception, e:
        logger.error(e)
        logger.error("{0} [{1} created at {2}]".format(tweet.text, tweet.id_str, tweet.created_at))
    else:
        return event


def main():
    # Open calendar file
    contents = open(FILENAME, 'rb').read()
    cal = Calendar.from_ical(contents)

    logger.debug("Opened calendar file and it's this kind of object: {0}".format(type(contents)))

    try:
        # Get the last id.
        last_id = cal['X-LAST-TWEET-ID']

        # Auth and check twitter
        auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
        auth.set_access_token(keys.access_token, keys.access_token_secret)
        api = tweepy.API(auth)

        # Fetch the tweets
        #tweets = api.user_timeline(since_id=218348003273084928, max_id=218349282380623871, count=200)
        tweets = api.user_timeline(since_id=last_id, count=200)

        logger.info("[tweetcal] fetched {0}, last was {1}".format(len(tweets), last_id))

        # Reverse so that the last shall be first
        tweets.reverse()

        for tweet in tweets:
            event = create_event(tweet)
            cal.add_component(event)

        # Set some global settings for the file.
        last_id = tweets[-1].id_str
        cal['X-LAST-TWEET-ID'] = last_id
        cal['X-APPLE-CALENDAR-COLOR'] = tweets[-1].profile_link_color

        # Write to file.
        ical = cal.to_ical()
        f = open(FILENAME, 'wb').read
        f.write(ical)
        f.close()

        logger.info('[tweetcal] Inserted {1} tweets. Most recent was: {0}'.format(tweets[-1].text, len(tweets)))

    except Exception, e:
        f.write(cal.to_ical())
        logger.error(e)
        raise

if __name__ == '__main__':
    logger = logging.getLogger('tweetcal')

    # file logging
    fh_formatter = logging.Formatter('%(asctime)s %(name)-16s %(levelname)-8s %(message)s')
    fh = logging.FileHandler('../log/tweetcal.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fh_formatter)
    logger.addHandler(fh)

    # console logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch_formatter = logging.Formatter('%(levelname)-8s %(message)s')
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    main()
