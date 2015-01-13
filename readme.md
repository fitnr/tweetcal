# Tweetcal

Tweetcal converts a Twitter feed into .ics (calendar) format.

## Install

Install with `pip install tweetcal`

## How to

Tweetcal has two commands. The first converts a Twitter archive to `ics`, the second saves recent tweets to `ics`.

### Reading an archive

Download your [Twitter archive](https://support.twitter.com/articles/20170160-downloading-your-twitter-archive) and unzip it. Let's say it's in `~/Downloads/archive/`. Run this command:

````sh
$ tweetcal read-archive ~/Downloads/archive calendar-file.ics
````

This will create `calendar-file.ics`. Test it by opening in your favorite calendaring program.

### Saving recent tweets

For this section, you'll need [Twitter OAuth credentials](https://dev.twitter.com/oauth/overview/application-owner-access-tokens).

Save those tokens to a yaml or json file. Use the [sample format in the repo](https://github.com/fitnr/tweetcal/blob/master/sample-config.yaml) as a guide. Let's say you've saved the file to `~/tweetcal.yaml` and your username is 'screen_name1'. Once that's set up, run:

```` sh
$ tweetcal stream --config ~/tweetcal.yaml --user screen_name1
````

Tweetcal leaves a note in ics files it creates to tell it where in an account's stream to start downloading. Because of this, you should only use a file created by Tweetcal with tweetcal-stream.
