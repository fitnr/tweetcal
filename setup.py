from setuptools import setup

try:
    readme = open('./readme.rst', 'r').read()

except IOError:
    readme = open('./readme.md', 'r').read()

setup(
    name='tweetcal',

    version='0.4.3',

    description='Python utilities for twitter bots',

    long_description=readme,

    url='http://github.com/fitnr/tweetcal',

    author='Neil Freeman',

    author_email='contact@fakeisthenewreal.org',

    license='GPLv3',

    packages=['tweetcal'],

    entry_points={
        'console_scripts': [
            'tweetcal=tweetcal.command:main',
        ],
    },

    test_suite='tests',

    install_requires=[
        'icalendar==3.8.4',
        'tweepy==3.1.0',
        'twitter_bot_utils >=0.6.2, <1'
    ]
)

