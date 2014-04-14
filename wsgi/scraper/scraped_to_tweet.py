import random

TEMPLATES = ["You could see %s in %s, ",
             "If you look up, you might see %s in the %s constellation, ",
             "Look for %s in the %s constellation, ",
             "%s is above you in the %s constellation, you could also find ",
             "You might find %s in %s constellation, "]

def tonightssky_info_to_tweet(sightings, user_name_len):
    # expects a list of dicts
    template = TEMPLATES[random.randrange(len(TEMPLATES))]
    result = ""

    while True:
        result = template % (sightings[0]['primary_catalog'], sightings[0]['constellation'])
        for c in range(1, len(sightings)):
            if c == len(sightings) - 1:
                continue
            else:
                result += "%s in %s; " % (sightings[c]['primary_catalog'], sightings[c]['constellation'])

        result = result[::-1]
        result = result.replace(";", "")
        result = result[::-1]
        result += "and %s in %s" % (sightings[c]['primary_catalog'], sightings[c]['constellation'])

        if len(result) <= 140 - user_name_len+1:
            break
        elif len(sightings) == 0:
            return -1
        else:
            sightings.pop(len(sightings) - 1)
    return result


def satellite_info_to_tweet(satellites, user_name_len):
    """
    eg: "-1.9 (very bright): The <ISS> starts rising
    <'09:13:19 pm'>, but best seen <'09:15:43pm'>.
    Look <WNW>, <26> deg above ground!
    """
    satellites_by_magnitude = sorted(satellites, key=lambda k: k['magnitude'])
    best_satellite = satellites_by_magnitude[0]

    #intro = "You're lucky! " if 'bright' in best_satellite['magnitude'] else None

    string_template = (
        "{magnitude}: The {satellite} starts rising "
        "{rise_time}, but it's best seen at {best_time}. "
        "Look {direction} {degrees}deg above ground!"
    ).format(
        magnitude=best_satellite['magnitude'],
        satellite=best_satellite['name'],
        rise_time=best_satellite['rise_time'],
        best_time=best_satellite['best_time'],
        direction=best_satellite['direction'],
        degrees=best_satellite['max_elevation']
    )

    string_template_short = (
        "{magnitude}: {satellite} is best seen at {best_time}.  "
        "Look {direction}!"
    ).format(
        magnitude=best_satellite['magnitude'],
        satellite=best_satellite['name'],
        best_time=best_satellite['best_time'],
        direction=best_satellite['direction'],
    )

    if len(string_template) + user_name_len <= 140:
        return string_template
    elif len(string_template_short) + user_name_len <= 140:
        return string_template_short
    else: 
        return -1
    
