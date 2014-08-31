#!/usr/bin/env python
# encoding: utf-8
"""
tweetcal.py

Created by neil on 2012-06-07.
Copyright (c) 2012 fake is the new real. All rights reserved.

Reads a CSV with the following columns into a calendar:
date, time, tweet, link (to tweet)
"""
import icalendar
from pytz import UTC
#import twitter
from datetime import datetime, timedelta
import csv

csv.register_dialect('tweets', delimiter=',', quoting=csv.QUOTE_ALL)

elapse = timedelta(seconds=60)

def unicode_csv_reader(utf8_data, dialect='tweets', **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    # decode UTF-8 back to Unicode, cell by cell:
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def main():
    cal = icalendar.Calendar()
    iCalDate = icalendar.prop.vDDDTypes
    cal.add('prodid', '-//twitter maker//fake is the new real//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', 'Tweets')

    stamp = datetime.now(tz=UTC)

    # read csv
    reader = unicode_csv_reader(open('fitnr_backup-2012-06-06.csv'))
    reader.next()
    for row in reader:
        event = icalendar.Event()
        # print row
        [date, time, tweet, link] = row
        [year, month, day] = [int(x) for x in date.split('-')]
        [hour, minute, sec] = [int(x) for x in time.split(':')]

        tweet_time = datetime(year, month, day, hour, minute, sec, tzinfo=UTC)

        event['dtstart'] = iCalDate(tweet_time)
        event['dtend'] = iCalDate(tweet_time + elapse)
        event.add('dtstamp', stamp)
        event.add('summary', tweet)
        event.add('description', link)
        event.add('priority', 1)
        tweet_id = link.split('/')
        event['uid'] = str(tweet_id[-1]) + '@fakeisthenewreal.org'
        cal.add_component(event)

    f = open('tweets.ics', 'wb')
    f.write(cal.to_ical())
    f.close()


if __name__ == '__main__':
    main()
