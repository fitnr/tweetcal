import re
import time
import logging
from datetime import datetime
from email.utils import formatdate
from tweepy import API, Status
from twitter_bot_utils import archive
from . import tweetcal

iso8601 = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ?(\+\d{4})?")


def fix_timeformat(string):
    match = iso8601.match(string)

    if match:
        dt = datetime.strptime(match.groups()[0], "%Y-%m-%d %H:%M:%S")
        string = formatdate(time.mktime(dt.timetuple()))

    return string


def read_as_status(archivepath):
    api = API()

    for tweet in archive.read_json(archivepath):

        tweet['created_at'] = fix_timeformat(tweet['created_at'])

        if tweet.get('retweeted_status'):
            tweet['retweeted_status']['created_at'] = fix_timeformat(tweet['retweeted_status']['created_at'])

        print tweet['text'], tweet['created_at']
        yield Status.parse(api, tweet)


def to_cal(archivepath, output, dry_run=None):
    '''Read an archive into a calendar'''
    logger = logging.getLogger('tweetcal')

    generator = lambda: read_as_status(archivepath)

    cal = tweetcal.new_calendar()

    logger.info('Reading archive.')
    tweetcal.add_to_calendar(cal, generator)

    logger.info('Added {} tweets to calendar.'.format(len(cal)))

    if not dry_run:
        tweetcal.write_calendar(cal, output)
        logger.info('Wrote {}.'.format(output))

def to_cal_args(args):
    tweetcal.setup_logger(args.verbose)
    to_cal(args.path, args.output, args.dry_run)
