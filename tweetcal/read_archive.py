import re
import time
from datetime import datetime
from email.utils import formatdate
import argparse
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


def to_cal(archivepath, ics):
    '''Read an archive into a calendar'''

    generator = lambda: read_as_status(archivepath)

    cal = tweetcal.new_calendar()
    tweetcal.add_to_calendar(cal, generator)
    tweetcal.write_calendar(cal, ics)


def main():
    parser = argparse.ArgumentParser(description="Load a twitter archive into an ICS file")

    parser.add_argument('archive', type=str, help="Input path")
    parser.add_argument('output', type=str, help="destination calendar file")

    args = parser.parse_args()

    to_cal(args.archive, args.output)

if __name__ == '__main__':
    main()
