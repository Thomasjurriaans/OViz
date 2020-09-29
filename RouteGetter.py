import http.client, urllib.request, urllib.parse, urllib.error, json
from Dictionaries import *
from collections import OrderedDict
from datetime import date


def get_route(route_key, origin, to):

    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': route_key,
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'dateTime': str(date.today()) + 'T13:08:50+0100',     # Takes train journeys from the afternoon, which are the most "regular" (Middle of the night journeys look very different usually for example)
        'excludeHighSpeedTrains': 'False',
        'excludeReservationRequired': 'True',
        'previousAdvices': '0',
        'nextAdvices': '1',
        'passing': 'True',
        'fromStation': origin,
        'toStation': to,
    })

    try:
        conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
        conn.request("GET", "/reisinformatie-api/api/v3/trips?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    try:
        legs = json.loads(data)['trips'][0]['legs']
    except:
        print(data)

    passes = []
    for leg in legs:
        for dic in leg['stops']:
            try:
                passes.append(name_to_code[dic['name']])                    # Get the name from each station that is passed along the way and convert to station code
            except KeyError:
                print("Name '" + dic['name'] + "' not found in dictionary.")
    unique_passes = list(OrderedDict.fromkeys(passes))                      # Efficiently remove duplicates (Overstap stations)
    return unique_passes


