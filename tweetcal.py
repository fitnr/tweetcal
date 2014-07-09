#!/usr/bin/env python
# encoding: utf-8
"""
tweetcal.py

Created by neil on 2012-06-09.
Copyright (c) 2012 Neil Freeman. All rights reserved.
"""
from os import path
from icalendar import Calendar, Event
import pytz
import argparse
from datetime import timedelta
import tweepy
import logging
try:
    from . import tweetcal_config as twkeys
except Exception:
    import tweetcal_config as twkeys


class no_tweets_exception(Exception):

    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=10)
    return start, end


def create_event(tweet):
    event = Event()

    try:
        start, end = parse_date(tweet.created_at)
        url = 'http://twitter.com/{0}/status/{1}'.format(tweet.user.screen_name, tweet.id_str)
        text = tweet.text.replace('&amp;', '&')

        event.add('summary', text)
        event.add('url', url)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('uid', '{0}@{1}'.format(tweet.id_str, tweet.user.screen_name))
        event['X-TWEET-ID'] = tweet.id_str

    except Exception as e:
        logger.error(e)
        logger.error("{0} [{1} created at {2}]".format(tweet.text, tweet.id_str, tweet.created_at))
    else:
        return event


def get_calendar(filename, user):
    '''Open calendar file and return as Calendar object, along with list of IDs retrieved (to avoid dupes)'''
    idset = set()

    with open(filename, 'rb') as h:
        contents = h.read()
        logger.debug("Opened calendar file and it's this kind of object: {0}".format(type(contents)))

    if contents == '':
        cal = Calendar()
        cal.add('PRODID', '-//twitter maker//fake is the new real//EN')
        cal.add('X-WR-CALNAME', user + ' tweets')

    else:
        cal = Calendar.from_ical(contents)
        idset = set(int(e['X-TWEET-ID']) for e in cal.subcomponents if e.get('X-TWEET-ID'))

    return cal, idset


def set_max_sin(cal, since_id=None, max_id=None):
    '''Set the max and since ids to request from twitter. If the calendar has a max ID, use it as the since'''
    since_id = since_id or cal.get('X-MAX-TWEET-ID', None)

    # Assume this means you're looking for earlier tweets
    if max_id < since_id:
        since_id = None

    return max_id, since_id


def set_max_id(cal, list1, list2):
    '''Combine set of read IDs and just-added IDs to get the new max id'''
    list_of_ids = list(list1) + list(list2)
    maxid = max(list_of_ids)

    cal['X-MAX-TWEET-ID'] = maxid
    logger.info('set {1} to {0}'.format(maxid, 'X-MAX-TWEET-ID'))


def get_tweets(**kwargs):
    logger.debug("Getting tweets with these args {0}".format(kwargs))
    try:
        # Auth and check twitter
        auth = tweepy.OAuthHandler(twkeys.consumer_key, twkeys.consumer_secret)
        auth.set_access_token(kwargs['access_token'], kwargs['access_token_secret'])
        api = tweepy.API(auth)

        cursor = tweepy.Cursor(api.user_timeline, **kwargs['twargs'])

        if not cursor.items:
            raise no_tweets_exception("No tweets")

    except Exception as e:
        print('API error!')
        raise e

    return cursor


def main():
    description = 'Grab tweets into an ics file.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--user', type=str, help='user to grab. Must be in config file.', required=True)
    parser.add_argument('--since_id', type=int, default=None,
                        required=False, help='Since ID: search tweets after this one.')
    parser.add_argument('--max_id', type=int, default=None,
                        required=False, help='Max ID: search tweets until this one.')

    args = parser.parse_args()

    logger.info("Starting to grab tweets for " + args.user)

    settings = twkeys.keys.get(args.user, {})
    if not settings.get('access_token') and not settings.get('access_token_secret'):
        logger.info("Don't have a key for this user.")
        return

    calfile = path.join((path.dirname(__file__) or '.'), settings['file'])

    cal, idset = get_calendar(calfile, args.user)
    max_id, since_id = set_max_sin(cal, args.since_id, args.max_id)

    twargs = {}
    if max_id:
        twargs['max_id'] = max_id

    if since_id:
        twargs['since_id'] = since_id

    settings['twargs'] = twargs

    try:
        cursor = get_tweets(**settings)
        status, added_ids = False, []

        # Loop the cursors and create the events if the tweet doesn't yet exist
        for status in list(cursor.items()):
            added_ids.append(status.id)
            if status.id in idset:
                logger.debug('not inserting ' + status.id_str)
                continue
            event = create_event(status)
            cal.add_component(event)

    except (tweepy.TweepError, no_tweets_exception) as e:
        logger.error(e)

    except Exception as e:
        logger.error(e)
        return

    try:
        if status:
            logger.info('Inserted {1} tweets. Most recent was: {0}'.format(status.text, len(added_ids)))
            cal['X-APPLE-CALENDAR-COLOR'] = '#' + status.user.profile_link_color
        else:
            logger.info('Did not find any new tweets')

        set_max_id(cal, idset, added_ids)
    except Exception as e:
        logger.error(e)

    try:
        ical = cal.to_ical()

    except Exception as e:
        logger.error(e)
        return

    # Write to file
    with open(calfile, 'wb') as f:
        logger.info('writing to file')
        f.write(ical)


if __name__ == '__main__':
    logger = logging.getLogger('tweetcal')
    filepath = path.dirname(__file__)
    logger.setLevel(logging.DEBUG)

    # file logging
    fh = logging.FileHandler(path.join(filepath + 'tweetcal.log'))
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter('%(asctime)s %(name)-16s line %(lineno)d %(levelname)-5s %(message)s'))
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)-5s [tweetcal] %(message)s'))
    logger.addHandler(ch)

    main()
