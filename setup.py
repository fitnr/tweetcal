# Tweetcal: Convert a tweet stream to ics calendar
# Copyright (c) 2014-2015 Neil Freeman
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
from setuptools import setup

try:
    readme = open('./readme.rst', 'r').read()

except IOError:
    readme = open('./readme.md', 'r').read()

setup(
    name='tweetcal',

    version='0.4.5',

    description='Convert a tweet stream to ics calendar',

    long_description=readme,

    url='http://github.com/fitnr/tweetcal',

    author='Neil Freeman',

    author_email='contact@fakeisthenewreal.org',

    license='GPL-3.0',

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Operating System :: OS Independent',
    ],

    packages=['tweetcal'],

    entry_points={
        'console_scripts': [
            'tweetcal=tweetcal.command:main',
        ],
    },

    test_suite='tests',

    use_2to3=True,

    install_requires=[
        'icalendar>=3.8.4,<4.0',
        'tweepy>=3.1.0,<4.0',
        'twitter_bot_utils >=0.6.2, <1'
    ]
)
