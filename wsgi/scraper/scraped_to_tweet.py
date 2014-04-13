import random
TEMPLATES = [ "You could see %s in %s, ",
              "If you look up, you might see %s in the %s constellation, ",
              "Look for %s in the %s constellation, ",
              "%s is above you in the %s constellation, you could also find ",
              "You might find %s in %s constellation, "
            ]

def info_to_tweet(sightings, user_name_len):
    # expects a list of dicts
    template = TEMPLATES[random.randrange(len(TEMPLATES))]
    result = "" 

    while True:
        result = template % (sightings[0]['primary_catalog'], sightings[0]['constellation'])
        for c in range(1, len(sightings)):
            if c == len(sightings) - 1:
                continue
            else:
                result += ", %s in %s" % (sightings[c]['primary_catalog'], sightings[c]['constellation'])
        else:
            if c >= 1 and template != TEMPLATES[3]:
                result += "and %s in %s" % (sightings[c]['primary_catalog'], sightings[c]['constellation'])
            else:
                result += "%s in %s" % (sightings[c]['primary_catalog'], sightings[c]['constellation'])

        if len(result) <= 140 - user_name_len+1:
            break
        elif len(sightings) == 0:
            return -1
        else:
            sightings.pop(len(sightings) - 1)
    return result
