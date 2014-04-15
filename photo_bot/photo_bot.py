import json
import urllib
import traceback
import base64
import os
from urllib2 import Request, urlopen, URLError, HTTPError
from time import sleep, time
from twython import Twython, TwythonRateLimitError
from PIL import Image

CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')


class RequestFailedError(Exception):
    """
    This is raised when flickr rejects, not twitter
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class DownloadFailedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


def _construct_rest_url_flickr(api_name, args):
    url_prefix = "https://api.flickr.com/services/rest/?method="
    api_key = "d01f1048dbb3b9159e6815962b2abd9b"
    result = url_prefix + api_name + "&"
    result += "format=json&"
    for k, v in args.iteritems():
        result = result + str(k) + "=" + str(v) + "&"
    result = result + "api_key=" + api_key
    return result


def _get_json_for_response(response_string):
    return response_string[14:len(response_string) - 1]


def _get_good_licenses():
    licenses = call_flickr("flickr.photos.licenses.getInfo", {})
    good_license_ids = []
    if "licenses" in licenses:
        # no try and except here, since a fail her is desirable when api changes
        for l in licenses['licenses']['license']:
            if 'Attribution' in l['name'] \
               or "No known copyright restrictions" in l['name']:
                good_license_ids.append(str(l['id']))
    return ",".join(good_license_ids)


def _download_img(url):
    retry_limit = 3
    retry_delay = 5  # seconds
    file_name = 'today.jpg'
    path_to_save = os.path.join(os.path.dirname(os.path.realpath(__file__)), file_name)
    for c in range(retry_limit):
        try:
            download = urllib.urlretrieve(url, path_to_save)
            if "image/jpeg" in str(download[1]):
                return file_name
            else:
                raise DownloadFailedError("Invalid image type/not an image")
        except URLError as e:
            print("Image download failed URL:", url, "Reason:", e.reason)
            sleep(retry_delay)


def _send_to_twitter(file_name):
    #file_name is in the same directory
    with open(file_name, 'r') as f:
        image = f.read()
        im = Image.open(file_name)
        width, height = im.size

    encoded = base64.b64encode(image)
    twitter = Twython(CONSUMER_KEY, CONSUMER_SECRET
        , ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)

    twitter.update_profile_banner_image(banner = encoded
        , width = width, height = height
        , offset_left = 0, offset_top = 0)


def call_flickr(api_name, args):
    """
    Calls a flickr api
    param api_name - the api to call
          args - the arguments of the api to send, in dict
    return response - the response in dict format
    """
    retry_limit = 3
    retry_delay = 30  # seconds

    request = Request(_construct_rest_url_flickr(api_name, args))
    for c in range(retry_limit):
        try:
            response = urlopen(request)
            kittens = response.read()
            dict_response = json.loads(_get_json_for_response(kittens))
            if "stat" in dict_response:
                if dict_response["stat"] == "fail":
                    print ("Api request returned fail. URL", request.get_full_url())
                    continue
            return dict_response
        except URLError, e:
            print "Request failed. URL: ", request.get_full_url(), "Reason:", e.reason
            sleep(retry_delay)  # dumb dumb just retry
    raise RequestFailedError("Too many retries, URL:s" % request.get_full_url())


def photo_to_url_flickr(photo_dict):
    """
    Expects a photo dictionary returned by flickr.photos.search
    return - url on success -1 on fail
    """
    try:
        farm = str(photo_dict['farm'])
        server_id = str(photo_dict['server'])
        p_id = str(photo_dict['id'])
        secret = str(photo_dict['secret'])
    except KeyError:
        return -1
    return "http://farm{0}.staticflickr.com/{1}/{2}_{3}.jpg" \
        .format(farm, server_id, p_id, secret)


def check_validity_flickr(photo_dict):
    """
    Checks whether a photo is suitable for banner use
    params photo_dict - a photo dictionary returned by the flickr api
           valid_licenses - a set of valid licenses
    return is_suitable - boolean whether the photo passed the tests
    """
    try:
        info_response = {}  # flickr.photos.getInfo
        size_response = {}  # call flickr.photos.getSizes
    except Exception:
        pass

    if "sizes" in size_response:
        sizes = [(s['width'], s['height']) for s in size_response['sizes']]
        for w, h in sizes:
            if 2000 > w > 1000 and 1080 > h > 600:
                return True
    return False


def start_bot():
    #search flickr :D
    #save photo :D
    #upload to twitter :D
    #periodicly do that and delete last one :D
    retry_delay = 10  # seconds
    keyword = "sky"
    image_index = 0
    while True:
        try:
            search_args = {
                "min_upload_date": time() - 86400,  # yesterday this time
                "safe_search": 1,  # don't want no prono
                "sort": "relevance",
                "license": _get_good_licenses(),
                "text": keyword,
                "per_page": 5
            }
            to_download = call_flickr("flickr.photos.search", search_args)['photos']['photo'][image_index]
            file_name = _download_img(photo_to_url_flickr(to_download))
            _send_to_twitter(file_name)
            print "Successfully updated banner photo"
            break
        except TwythonRateLimitError:
            sleep(retry_delay) #  just try again
        except RequestFailedError:
            traceback.print_exc()
        except DownloadFailedError as e:
            print "Error occurred after downloading image.", e.message
            image_index += 1  # try next image
            if image_index > 4:
                print("All 5 downloads failed! No update happen")
                break  # all 5 failed. no update this period
            sleep(retry_delay)

if __name__ == '__main__':
    # raise RequestFailedError('aliens invaded')
    start_bot()
    # print photo_to_url_flickr({"farm": "500", "server": "1000", "id": "123", "secret": "100"})
    # print _construct_rest_url_flickr("flickr.test.echo", {"foo": "bar"})