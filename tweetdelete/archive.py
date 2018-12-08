#!/usr/bin/python3

import argparse
import csv
from datetime import datetime, timedelta
import json
import logging
from os.path import isdir, isfile
import sys

import twitter


ERROR_SOURCE_DELETED = 34
ERROR_NO_STATUS = 144
ERROR_INACCESSIBLE = 179

ARCHIVE_TWEETS = '{}/tweets.csv'
TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S +0000'

root_logger = logging.getLogger()
stream = logging.StreamHandler(sys.stdout)
root_logger.addHandler(stream)
log = logging.getLogger(__name__)


def archive_datetime(timestamp):
    return datetime.strptime(str(timestamp), TIMESTAMP_FORMAT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            'archive', type=str,
            help='Path to your extracted Twitter archive')
    parser.add_argument(
            'scratch', type=str,
            help='Path to the scratch scratch file, used to track scratch Tweets')
    parser.add_argument(
            'older_than', type=int,
            help='Maximum age of a Tweet (seconds)')
    parser.add_argument(
            '--consumer-key', metavar='consumer_key', type=str,
            help='')
    parser.add_argument(
            '--consumer-secret', metavar='consumer_secret', type=str,
            help='')
    parser.add_argument(
            '--access-token-key', metavar='access_token_key', type=str,
            help='')
    parser.add_argument(
            '--access-token-secret', metavar='access_token_secret', type=str,
            help='')
    parser.add_argument(
            '--log-level', metavar='log_level', type=str,
            help='Output log level', default='debug')
    args = parser.parse_args()

    log.setLevel(args.log_level.upper())

    tweets_csv = ARCHIVE_TWEETS.format(args.archive)
    if not isdir(args.archive) or not isfile(tweets_csv):
        log.error('{} doesn\'t look like a valid archive')
        exit(1)

    try:
        with open(args.scratch, 'r') as scratch_file:
            scratch = json.load(scratch_file)
    except FileNotFoundError:
        scratch = {
            'deleted': [],
            'inaccessible': [],
            'source_deleted': [],
        }

    api = twitter.Api(
            consumer_key=args.consumer_key, consumer_secret=args.consumer_secret,
            access_token_key=args.access_token_key, access_token_secret=args.access_token_secret,
            sleep_on_rate_limit=False)
    user = api.VerifyCredentials()
    log.info('Authenticated as @{} ({}) with {} Tweets and {} likes'.format(
            user.screen_name, user.name, user.statuses_count, user.favourites_count))

    older_than = datetime.now() - timedelta(seconds=args.older_than)
    log.info('Deleting content older than {}'.format(older_than))

    try:
        with open(tweets_csv, 'r') as f:
            tweets = csv.DictReader(f)
            for tweet in tweets:
                if tweet['tweet_id'] in scratch['deleted']:
                    log.debug('Skipping previously deleted {}'.format(
                            tweet['tweet_id']))
                    continue

                timestamp = archive_datetime(tweet['timestamp'])
                if timestamp < older_than:
                    log.debug('Deleting {} ({})'.format(
                            tweet['tweet_id'], tweet['text']))
                    try:
                        api.DestroyStatus(tweet['tweet_id'])
                    except twitter.error.TwitterError as e:
                        handled = False
                        if e.message[0]['code'] == ERROR_INACCESSIBLE:
                            log.debug('Marking {} as inaccessible'.format(
                                    tweet['tweet_id']))
                            scratch['inaccessible'].append(tweet['tweet_id'])
                            handled = True
                        if e.message[0]['code'] == ERROR_SOURCE_DELETED:
                            log.debug('Marking {} as source deleted'.format(
                                    tweet['tweet_id']))
                            scratch['source_deleted'].append(tweet['tweet_id'])
                            handled = True
                        if e.message[0]['code'] == ERROR_NO_STATUS:
                            log.debug('Skipping missing {}'.format(
                                    tweet['tweet_id']))
                            handled = True

                        if not handled:
                            raise e

                    scratch['deleted'].append(tweet['tweet_id'])
                else:
                    log.debug('Skipping recent enough {}'.format(tweet['tweet_id']))
    finally:
        with open(args.scratch, 'w') as scratch_file:
            json.dump(scratch, scratch_file)
