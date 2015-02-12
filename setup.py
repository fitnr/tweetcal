from setuptools import setup

try:
    from pypandoc import convert
    def read_md(f):
        try:
            return convert(f, 'rst', 'md')
        except (RuntimeError, IOError):
            return ''

except ImportError:
    print("pypandoc module not found, could not convert Markdown to RST")
    def read_md(f):
        try:
            return open(f, 'r').read()
        except IOError:
            return ''


setup(
    name='tweetcal',

    version='0.4.2',

    description='Python utilities for twitter bots',

    long_description=read_md('readme.md'),

    url='http://github.com/fitnr/tweetcal',

    author='Neil Freeman',

    author_email='contact@fakeisthenewreal.org',

    license='GPL',

    packages=['tweetcal'],

    entry_points={
        'console_scripts': [
            'tweetcal=tweetcal.command:main',
        ],
    },

    install_requires=[
        'icalendar==3.8.4',
        'tweepy==3.1.0',
        'twitter_bot_utils==0.6.2.1'
    ]
)

