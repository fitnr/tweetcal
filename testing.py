import icalendar
import pytz
from icalendar import Calendar, Event, prop.vText
from datetime import datetime

event = Event()
event.add('summary',icalendar.prop.vText("asdsḈ"))
cal = Calendar()
cal = Calendar()
cal.add('prodid', '-//My calendar product//mxm.dk//')
cal.add('version', '2.0')
cal.add_component(event)
cal.to_ical()


auth = tweepy.OAuthHandler(keys.consumer_key, keys.consumer_secret)
auth.set_access_token(keys.access_token, keys.access_token_secret)
api = tweepy.API(auth)
tweets = api.user_timeline(since_id=210468705950384129, max_id=218349282380623871, count=200)

contents = open(FILENAME, 'rb').read()
cal = icalendar.Calendar.from_ical(contents)
for tweet in tweets:
    event = tweetcal.create_event(tweet)
    cal.add_component(event)
    most_recent = tweet.text

f = open(FILENAME, 'wb')
f.write(cal.to_ical())
f.close()
print 'Inserted some tweets. Most recent was: ' + most_recent
