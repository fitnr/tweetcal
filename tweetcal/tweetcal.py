#!/usr/bin/env python
# encoding: utf-8
# Copyright (c) 2014 Neil Freeman

from os import path
from icalendar import Calendar, Event
import twitter_bot_utils as tbu
from HTMLParser import HTMLParser
import pytz
from datetime import timedelta
import tweepy
import logging


def setup_logger(verbose=None):
    logger = logging.getLogger('tweetcal')

    if verbose:
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('tweetcal: %(message)s'))
        logger.addHandler(ch)

    return logger


def get_settings_and_keys(args):
    setup_logger(args.verbose or args.dry_run)

    argsdict = {k: v for k, v in vars(args).items() if v is not None}

    settings, keys = tbu.confighelper.configure(args.user, args.config, **argsdict)

    settings['file'] = path.join(path.dirname(__file__), settings['file'])

    return settings, keys


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=1)
    return start, end


def create_event(tweet):
    event = Event()

    try:
        url = u'http://twitter.com/{0}/status/{1}'.format(tweet.user.screen_name, tweet.id_str)
        event.add('url', url)

        text = tbu.helpers.replace_urls(tweet)
        text = HTMLParser().unescape(text)
        event.add('summary', text)

        dtstart, dtend = parse_date(tweet.created_at)
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)

        event.add('uid', u'{0}@{1}.twitter'.format(tweet.id_str, tweet.user.screen_name))
        event['X-TWEET-ID'] = tweet.id_str

    except Exception as e:
        logger = logging.getLogger('tweetcal')
        logger.error(e)
        logger.error(u"{0} [{1} created at {2}]".format(tweet.text, tweet.id_str, tweet.created_at))

    else:
        return event


def get_calendar(filename, user):
    '''Open calendar file and return as Calendar object, along with list of IDs retrieved (to avoid dupes)'''
    with open(filename, 'rb') as h:
        contents = h.read()
        logging.getLogger('tweetcal').info("Opened calendar file " + filename)

    if contents == '':
        cal = Calendar()
        cal.add('PRODID', '-//twitter maker//fake is the new real//EN')
        cal.add('X-WR-CALNAME', user + ' tweets')

    else:
        cal = Calendar.from_ical(contents)

    return cal


def get_since_id(cal, since_id=None):
    '''Set the max and since ids to request from twitter. If the calendar has a max ID, use it as the since'''
    output = dict()
    since_id = since_id or cal.get('X-MAX-TWEET-ID', None)

    if since_id:
        output['since_id'] = since_id

    logging.getLogger('tweetcal').debug('Setting since_id: {}'.format(str(since_id)))

    return output


def set_max_id(cal, max_id):
    '''Combine set of read IDs and just-added IDs to get the new max id'''
    m = max(cal['X-MAX-TWEET-ID'], max_id)
    cal['X-MAX-TWEET-ID'] = m

    logging.getLogger('tweetcal').debug('Set {1} to {0}'.format(max_id, 'X-MAX-TWEET-ID'))

def get_tweets(consumer_key, consumer_secret, key, secret, **kwargs):

    # Auth and check twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(key, secret)
    api = tweepy.API(auth)

    logging.getLogger('tweetcal').debug(
        "Setting up connection to Twitter API (since_id: {})".format(kwargs.get('since_id')))

    return tweepy.Cursor(api.user_timeline, **kwargs)


def add_to_calendar(cal, cursor):
    """Add tweets to the calendar object"""
    ids, status = (), None

    # Loop the cursors and create the events if the tweet doesn't yet exist
    for status in cursor.items():
        event = create_event(status)
        cal.add_component(event)
        ids = ids + (status.id, )

    logging.getLogger('tweetcal').info('Inserted {} tweets.'.format(len(ids)))

    if status:
        cal['X-APPLE-CALENDAR-COLOR'] = '#' + status.user.profile_link_color

    try:
        max_id = max(ids)

    # If that's empty, there will be a ValueError, which is fine.
    except ValueError:
        max_id = 0

    set_max_id(cal, max_id)


def write_calendar(cal, calendar_file):
    ical = cal.to_ical()
    open(calendar_file, 'wb').write(ical)


def tweetcal(settings, keys):
    logger = logging.getLogger('tweetcal')

    if len(keys) != 4:
        raise ValueError("Incomplete settings: Don't have complete keys for @" + settings['user'])

    cal = get_calendar(settings['file'], settings['user'])

    since = get_since_id(cal, settings.get('since_id'))

    cursor = get_tweets(
        consumer_key=keys['consumer_key'],
        consumer_secret=keys['consumer_secret'],
        key=keys['key'],
        secret=keys['secret'],
        **since
    )

    logger.info("Grabbing tweets for @" + settings['user'])
    add_to_calendar(cal, cursor)

    if settings['dry_run']:
        logger.info('Ending without rewriting file.')

    else:
        logger.info('Writing tweets to file.')
        write_calendar(cal, settings['file'])


def main():
    parser = tbu.creation.setup_args('Grab tweets into an ics file.')

    parser.add_argument('--user', type=str, help='user to grab. Must be in config file.', required=True)

    parser.add_argument('--since_id', type=int, default=None,
                        required=False, help='Since ID: search tweets after this one.')

    args = parser.parse_args()

    settings, keys = get_settings_and_keys(args)

    tweetcal(settings, keys)


if __name__ == '__main__':
    main()
