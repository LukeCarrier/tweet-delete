# Delete your Tweets

People change. Make sure Twitter keeps pace.

---

## Hacking

Set up an isolated virtual environemnt where we can keep our dependencies. If you're using Python >= 3.7 the bundled `venv` module has you covered:

```
$ python -m venv venv
```

On other versions, install `virtualenv` and use that:

```
$ pip install virtualenv
$ virtualenv venv
```

Either way, we're now ready to install dependencies:

```
$ . venv/bin/activate
$ pip install -r requirements.txt
```

## Configuring

1. [Apply for access](https://developer.twitter.com/en/apply-for-access) to the Twitter API.
2. [Create an app](https://developer.twitter.com/en/apps) to obtain credentials.
3. Browse to the _Keys and tokens_ tab and copy your _Consumer API keys_.
4. While here, _Create_ and make a note of your _Access token & access token secret_.

## Deleting your archive

As the Twitter timeline API [only allows access to the last 3,200 Tweets](https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline) we need to get an index some other way.

Export your Tweets by browsing to Profile and settings > Settings and privacy > Content > Your Tweet archive and clicking Request your archive. You'll get an email in a few minutes with a link to download them. Once you've downloaded it, extract the zip file. Now, have TweetDelete do its thing:

```
$ python -m tweetdelete.archive \
          --consumer-key CONSUMER_KEY \
          --consumer-secret CONSUMER_SECRET \
          --access-token-key ACCESS_TOKEN_KEY \
          --access-token-secret ACCESS_TOKEN_SECRET \
          ARCHIVE_PATH SCRATCH_FILE OLDER_THAN
```
