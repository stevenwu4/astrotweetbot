import praw
import random
from twython import Twython, TwythonRateLimitError
from urllib2 import Request, urlopen, URLError, HTTPError
import urllib
import base64
from PIL import Image

SUB_REDDITS = ["skyporn", "spaceporn", "earthporn"]
USED_LINK_LOG = "url_logs.log"
SUPPORTED_FORMAT = ["png", "jpg"]

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

MESSAGES = ["Check out this cool photo I found on the Internet",
            "I was just reading Reddit and I found this",
            "Just got a Reddit delivery",
            "This photo I found looks great!",
            "I found this and stared at it for a long time (with my robot eye)",
            "Amazing sight",
            "Who needs to go outside when photos like is on the Internet",
            "Thanks to reddit, I discovered this",
            "I am a bot and I was stunned by this amazing scenery",
            "Approved by the Reddit public"]


class DownloadFailedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

def _download_img(url):
    retry_limit = 3
    retry_delay = 5  # seconds
    file_name = 'image'
    for c in range(retry_limit):
        try:
            download = urllib.urlretrieve(url, file_name)
            return download[0]
        except URLError as e:
            print("Image download failed URL:", url, "Reason:", e.reason)
            sleep(retry_delay)
    raise DownloadFailedError("Download failed after %d attempts" % retry_limit)


# throws TwythonRateLimitError
def _b64_encode(file_name):  
    #file_name is in the same directory
    with open(file_name, 'r') as f:
        image = f.read()
    return base64.b64encode(image)

def _size_test(b64string, size_limit):
    return len(b64string) < size_limit

def _get_size(twython_instance):
    return twython_instance.get_twitter_configuration()['photo_size_limit']


def main():
    reddit_post_limit = 10
    twitter_retries = 3
    twitter_retry_delay = 60  # second

    used_links = set()
    try:
        with open(USED_LINK_LOG, 'r') as log_file:
            for line in log_file:
                used_links.add(line.strip())
    except IOError as e:
        if e.errno == 2:  # file doesn't exist
            # make the file if it doesn't exist
            open(USED_LINK_LOG, 'w').close()

    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET,
                      ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    for c in range(twitter_retries):
        try:
            twitter_photo_size_limit = _get_size(twitter)
            break
        except TwythonRateLimitError as e:
            sleep(twitter_retry_delay)
            continue
        raise TwythonRateLimitError(
        """%d tries failed while trying to use "get_twitter_configuration":""" \
        % twitter_retries, 429)
        
    user_agent = "Astro Tweet Bot link gatherer by @astro_tweet_bot"
    reddit = praw.Reddit(user_agent=user_agent)
    submissions = reddit.get_subreddit(random.choice(SUB_REDDITS)) \
                                  .get_hot(limit=reddit_post_limit)
    links = [x.url for x in submissions]
    for l in links:
        if l in used_links:
            continue
        if l[(len(l) - 3):].lower() not in SUPPORTED_FORMAT:
            continue
        file_name = _download_img(l) 
        # save to today.jpg, extension doesn't matter since it gets encoded
        encoded = _b64_encode(file_name)
        if _size_test(encoded, twitter_photo_size_limit):
            # print "start it"
            for c in range(twitter_retries):
                try:
                    #twitter.update_status(status=random.choice(MESSAGES)+" "+l)
                    twitter.update_status_with_media(media=open(file_name,'r'), status=random.choice(MESSAGES))
                    print ("photo successfully tweeted")
                    return 0
                except TwythonRateLimitError as e:
                    sleep(twitter_retry_delay)
                    continue
            raise TwythonRateLimitError("%d tries failed" % twitter_retries, 429)
    print "nothing was sent"
    return 1

if __name__ == "__main__":
    main()