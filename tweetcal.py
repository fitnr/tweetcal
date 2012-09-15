#!/usr/bin/env python
# encoding: utf-8
"""
tweetcal.py

Created by neil on 2012-06-09.
Copyright (c) 2012 Neil Freeman. All rights reserved.
"""

import sys
import os
from icalendar import Calendar, Event
import pytz
import argparse
from datetime import timedelta
import tweetcal_keys as twkeys
import tweepy
import logging

# Constant
PATH = os.path.dirname(sys.argv[0])


class no_tweets_exception(Exception):

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=30)
    return start, end


def create_event(tweet):
    event = Event()

    try:
        start, end = parse_date(tweet.created_at)
        url = 'http://twitter.com/{0}/{1}'.format(tweet.user.screen_name, tweet.id_str)
        text = tweet.text.replace('&amp;', '&')

        event.add('summary', text)
        event.add('description', text)
        event.add('url', url)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('uid', '{0}@fakeisthenewreal'.format(tweet.id_str))
        event['X-TWEET-ID'] = tweet.id_str

    except Exception, e:
        logger.error(e)
        logger.error("{0} [{1} created at {2}]".format(tweet.text, tweet.id_str, tweet.created_at))
    else:
        return event


def main(argv=None):
    description = 'Grab tweets into an ics file.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--user', type=str, help='user to grab. Must be in config file.', required=True)
    parser.add_argument('--method', default='present', choices=['present', 'past'], required=False, help='Start in the past, or in the present.')
    args = parser.parse_args()

    method = args.method
    user = args.user
    settings = twkeys.keys[user]
    filename = (PATH or '.') + '/' + settings['file']
    twargs = {}
    twargs['count'] = 200

    # Open calendar file
    contents = open(filename, 'rb').read()

    if contents == '':
        cal = Calendar()
        cal.add('PRODID', '-//twitter maker//fake is the new real//EN')
        cal.add('X-WR-CALNAME', user + ' tweets')
        method = 'present'
        cal['X-SINCE-TWEET-ID'] = 0
        twargs['since_id'] = 0

    else:
        cal = Calendar.from_ical(contents)

    logger.debug("Opened calendar file and it's this kind of object: {0}".format(type(contents)))

    if contents != '':
        if method == 'present':
            # Get the last id.
            key = cal['X-SINCE-TWEET-ID']
            twargs['since_id'] = key

        elif method == 'past':
            # Get the last id.
            key = cal['X-MAX-TWEET-ID']
            twargs['max_id'] = key
    try:

        # Auth and check twitter
        auth = tweepy.OAuthHandler(twkeys.consumer_key, twkeys.consumer_secret)
        auth.set_access_token(settings['access_token'], settings['access_token_secret'])
        api = tweepy.API(auth)

        if api.test():
            # Fetch the tweets
            #tweets = api.user_timeline(since_id=218348003273084928, max_id=218349282380623871, count=200)
            tweets = api.user_timeline(**twargs)
        else:
            raise Exception('Twitter API problem')

        if len(tweets) == 0:
            raise no_tweets_exception("No tweets")

        else:
            # Reverse so that the last shall be first
            tweets.reverse()
            logger.info("[tweetcal] fetched {0} tweets.".format(len(tweets)))

        # Create the events
        for tweet in tweets:
            event = create_event(tweet)
            cal.add_component(event)

        if method == 'present':
            x_id = tweets[-1].id_str
            cal['X-SINCE-TWEET-ID'] = x_id

        elif method == 'past':
            x_id = tweets[0].id_str
            cal['X-MAX-TWEET-ID'] = x_id

        logger.info('[tweetcal] last/max was {0}'.format(x_id))

        cal['X-APPLE-CALENDAR-COLOR'] = '#' + tweets[-1].user.profile_link_color

        # Write to file.
        ical = cal.to_ical()
        f = open(filename, 'wb')
        f.write(ical)
        f.close()

        logger.info('[tweetcal] Inserted {1} tweets. Most recent was: {0}'.format(tweets[-1].text, len(tweets)))

    except tweepy.TweepError, e:
        logger.error(e)
    except no_tweets_exception, e:
        logger.error(e)
    except Exception, e:
        logger.error(e)
        g = open(filename, 'wb')
        g.write(contents)
        raise

if __name__ == '__main__':
    logger = logging.getLogger('tweetcal')

    # file logging
    # fh_formatter = logging.Formatter('%(asctime)s %(name)-16s %(levelname)-8s %(message)s')
    # fh = logging.FileHandler(PATH + '/tweetcal.log')
    # fh.setLevel(0)
    # fh.setFormatter(fh_formatter)
    # logger.addHandler(fh)

    # # console logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch_formatter = logging.Formatter('%(levelname)-8s %(message)s')
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    main()
