import json
from urllib2 import Request, urlopen, URLError, HTTPError
from time import sleep


class RequestFailedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

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


def check_validity_flickr(photo_dict, valid_licenses):
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

    if "photo" in info_response:
        if "license" in info_response['photo']:
            if int(info_response['photo']["license"]) in valid_licenses:
                pass
            else:
                return False
        else:
            return False
    else:
        return False

    if "sizes" in size_response:
        sizes = [(s['width'], s['height']) for s in size_response['sizes']]
        for w, h in sizes:
            if 2000 > w > 1000 and 1080 > h > 600:
                return True
    return False

def _construct_rest_url_flickr(api_name, args):
    url_prefix = "https://api.flickr.com/services/rest/?method="
    api_key = "d01f1048dbb3b9159e6815962b2abd9b"
    result = url_prefix + api_name + "&"
    result += "format=json&"
    for k, v in args.iteritems():
        result = result + k + "=" + v + "&"
    result = result + "api_key=" + api_key
    return result

def _get_json_for_response(response_string):
    return response_string[14:len(response_string) - 1]

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
            return json.loads(_get_json_for_response(kittens))
        except URLError, e:
            print "Request failed. URL: ", request.get_full_url(), "Reason:", e.reason
            sleep(retry_delay)  # dumb dumb just retry
    raise RequestFailedError("Too many retries, URL:", request.get_full_url())

if __name__ == '__main__':
    raise RequestFailedError('aliens invaded')
    print photo_to_url_flickr({"farm": "500", "server": "1000", "id": "123", "secret": "100"})
    call_flickr("flickr.test.echo", {"foo": "bar"})
    print _construct_rest_url_flickr("flickr.test.echo", {"foo": "bar"})





















