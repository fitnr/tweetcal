import os
import tweepy
import unittest
import logging
from tweetcal import tweetcal
from icalendar import Calendar, Event

TWEET = {
    "source": "\u003Ca href=\"http:\/\/twitter.com\/download\/iphone\" rel=\"nofollow\"\u003ETwitter for iPhone\u003C\/a\u003E",
    "entities": {
        "user_mentions": [{
            "name": "John Doe",
            "screen_name": "twitter",
            "indices": [0, 8],
            "id_str": "1",
            "id": 1
        }],
        "media": [],
        "hashtags": [],
        "urls": []
    },
    "created_at": "Wed May 23 06:01:13 +0000 2007",
    "in_reply_to_status_id_str": "318563540590010368",
    "id_str": "318565861172600832",
    "in_reply_to_user_id": 14155645,
    "text": "@twitter example tweet example tweet example tweet",
    "id": 318565861172600832,
    "in_reply_to_status_id": 318563540590010368,
    "in_reply_to_screen_name": "twitter",
    "in_reply_to_user_id_str": "14155645",
    "retweeted": None,
    "user": {
        "name": "Neil Freeman",
        "screen_name": "fitnr",
        "protected": False,
        "id_str": "6853512",
        "profile_image_url_https": "https:\/\/pbs.twimg.com\/profile_images\/431817496350314496\/VGgzYAE7_normal.jpeg",
        "id": 6853512,
        "verified": False
    }
}


class test_twitter_bot_utils(unittest.TestCase):

    def setUp(self):
        self.api = tweepy.API()
        self.status = tweepy.Status.parse(self.api, TWEET)

        self.screen_name = 'example_screen_name'

    def test_create_event(self):
        event = tweetcal.create_event(self.status)

        assert event['summary'] == self.status.text
        assert event['dtstart'].dt.month == 5

    def test_new_calendar(self):
        cal = tweetcal.new_calendar(self.screen_name)
        assert type(cal) == Calendar
        assert cal['X-WR-CALNAME'] == self.screen_name + ' tweets'

    def test_get_cal(self):
        ics = os.path.join(os.path.dirname(__file__), 'calendar.ics')
        cal = tweetcal.get_calendar(ics)

        assert cal['VERSION'] == "2.0"
        assert len(cal.subcomponents) > 0
        self.assertEqual(str(cal.subcomponents[0]['SUMMARY']), 'Lorem ipsum dolor')

        empty = os.path.join(os.path.dirname(__file__), 'empty.ics')

        self.assertRaises(IOError, tweetcal.get_calendar, empty)
        self.assertRaises(IOError, tweetcal.get_calendar, 'fake-2342.ics')


if __name__ == '__main__':
    unittest.main()
