#!/usr/bin/env python
# encoding: utf-8
# Copyright (c) 2014 Neil Freeman

from os import path
from icalendar import Calendar, Event
from twitter_bot_utils import creation, helpers
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


def get_settings(args):
    settings = helpers.config_parse(args.config)

    setup_logger(args.verbose or args.dry_run)

    # Remove secret bits.
    settings.update(settings['users'][args.user])
    del settings['users']

    settings.update({k: v for k, v in vars(args).items() if v is not None})

    if not settings.get('key') or not settings.get('secret'):
        raise KeyError("Incomplete settings: Don't have a key for this user.")

    settings['file'] = path.join(path.dirname(__file__), settings['file'])

    if args.max_id:
        settings['max_id'] = args.max_id

    if args.since_id:
        settings['since_id'] = args.since_id

    return settings


def parse_date(datetime):
    start = datetime.replace(tzinfo=pytz.UTC)
    end = start + timedelta(seconds=1)
    return start, end


def create_event(tweet):
    event = Event()

    try:
        url = u'http://twitter.com/{0}/status/{1}'.format(tweet.user.screen_name, tweet.id_str)
        event.add('url', url)

        text = helpers.replace_urls(tweet)
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


def set_max_sin(cal, since_id=None, max_id=None):
    '''Set the max and since ids to request from twitter. If the calendar has a max ID, use it as the since'''
    output = dict()
    since_id = since_id or cal.get('X-MAX-TWEET-ID', None)

    # Assume this means you're looking for earlier tweets
    if max_id and max_id < since_id:
        since_id = None

    if max_id:
        output['max_id'] = max_id

    if since_id:
        output['since_id'] = since_id

    logging.getLogger('tweetcal').debug('Setting since_id: {}'.format(str(since_id)))

    return output


def set_max_id(cal, max_id):
    '''Combine set of read IDs and just-added IDs to get the new max id'''
    cal['X-MAX-TWEET-ID'] = max_id

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

    set_max_id(cal, max(ids))


def write_calendar(cal, calendar_file):
    ical = cal.to_ical()
    open(calendar_file, 'wb').write(ical)


def tweetcal(settings):
    logger = logging.getLogger('tweetcal')

    cal = get_calendar(settings['file'], settings['user'])

    max_since = set_max_sin(cal, settings.get('since_id'), settings.get('max_id'))

    cursor = get_tweets(
        consumer_key=settings['consumer_key'],
        consumer_secret=settings['consumer_secret'],
        key=settings['key'],
        secret=settings['secret'],
        **max_since
    )

    logger.info("Grabbing tweets for @" + settings['user'])
    add_to_calendar(cal, cursor)

    if settings['dry_run']:
        logger.info('Ending without rewriting file.')

    else:
        logger.info('Writing tweets to file.')
        write_calendar(cal, settings['file'])


def main():
    parser = creation.setup_args('Grab tweets into an ics file.')

    parser.add_argument('--user', type=str, help='user to grab. Must be in config file.', required=True)

    parser.add_argument('--since_id', type=int, default=None,
                        required=False, help='Since ID: search tweets after this one.')
    parser.add_argument('--max_id', type=int, default=None,
                        required=False, help='Max ID: search tweets until this one.')

    args = parser.parse_args()
    settings = get_settings(args)

    tweetcal(settings)


if __name__ == '__main__':
    main()
