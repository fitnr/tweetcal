import argparse
from . import tweetcal, read_archive

def main():
    parser = argparse.ArgumentParser(description='Grab tweets into an ics file.')

    subparsers = parser.add_subparsers()

    archiver = subparsers.add_parser('archive')
    archiver.set_defaults(func=read_archive.to_cal_args)
    archiver.add_argument('path', type=str, metavar='PATH', help='Path to archive file')
    archiver.add_argument('output', type=str, metavar='OUTPUT', help='Path to output file')
    archiver.add_argument('-n', '--dry-run', action='store_true', help="Don't actually run.")
    archiver.add_argument('-v', '--verbose', action='store_true', help="Log to stdout.")
    archiver.add_argument('-x', '--max-id', type=float, default=float('inf'), help='Only save tweets older than this id')
    archiver.add_argument('-s', '--since-id', type=int, default=1, help='Only save tweets newer than this id')

    load = subparsers.add_parser('stream')
    load.set_defaults(func=tweetcal.tweetcal)
    load.add_argument('--config', type=str, help='Config file.')
    load.add_argument('--user', type=str, help='User to grab. Must be in config file.')
    load.add_argument('-x', '--max', type=int, help='Maximum number of tweets to download default: 100.')
    load.add_argument('-n', '--dry-run', action='store_true', help="Don't actually run.")
    load.add_argument('-v', '--verbose', action='store_true', help="Log to stdout.")

    args = parser.parse_args()

    args.func(args)

if __name__ == '__main__':
    main()
