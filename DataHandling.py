import pandas as pd
import os
from Dictionaries import name_to_code
import http.client
import json
import RouteGetter
from Functions import *


def get_csv_data(route_key, railmap, refresh=True):
    if not refresh:
        try:
            history = pd.read_pickle("data/travelhistory/fullhistory.pkl")
            stations = pd.read_csv("data/stations/filteredstations.csv")
        except FileNotFoundError:
            print("Something went wrong while reading .csv's, refreshing...")
            history, stations = get_csv_data(railmap, refresh=True)

    else:
        stations = pd.read_csv("data/stations/stations.csv", sep=',')                           # Read station data
        stations = stations[stations.Country == "Netherlands"]                                  # Filter all non-Dutch
        stations['Code'] = stations['Code'].str.lower()                                         # Make all codes lower case

        history = prepare_history(stations)
        history = enrich_history(route_key, history, stations, railmap)

        history.to_pickle("data/travelhistory/fullhistory.pkl")
        stations.to_csv("data/stations/filteredstations.csv", index=False)

    return history, stations


def prepare_history(stations):
    framelist = []
    for filename in sorted(os.listdir("data/travelhistory/raw/")):  # Make a list of all csv's as dataframes
        framelist.append(pd.read_csv("data/travelhistory/raw/" + filename, sep=';', decimal=","))

    history = pd.concat(framelist, axis=0, ignore_index=True)  # Concat all csv data

    history['Vertrek_code'] = history['Vertrek'].replace(name_to_code)  # Replace normal values according to dictionary
    history['Bestemming_code'] = history['Bestemming'].replace(name_to_code)  # To make sure names match Station names

    history = history.drop(['Check-in', 'Klasse', 'Product', 'Opmerkingen', 'Transactie', 'Naam', 'Kaartnummer'], axis=1)

    history = history[history.Bestemming_code == history.Bestemming_code]  # Remove all bestemming == NaN rows
    history = history[(history.Vertrek_code.isin(stations.Code)) & (history.Bestemming_code.isin(stations.Code))]  # Remove non-train station destinations
    history = history[history.Bestemming_code != history.Vertrek_code]  # Remove non-journeys

    history['Bedrag'] = history['Bedrag'].fillna(value=0)
    history = history.reset_index(drop=True)

    return history


def enrich_history(route_key, history, stations, railmap):
    from_lat, from_lon, to_lat, to_lon = [], [], [], []
    for location in history.Vertrek_code:
        from_lat.append(stations.where(stations.Code == location).dropna()['Lat'].values[0])            # Enrich with lat & lon data
        from_lon.append(stations.where(stations.Code == location).dropna()['Lon'].values[0])

    for location in history.Bestemming_code:
        to_lat.append(stations.where(stations.Code == location).dropna()['Lat'].values[0])
        to_lon.append(stations.where(stations.Code == location).dropna()['Lon'].values[0])

    history['from_lat'] = from_lat
    history['from_lon'] = from_lon
    history['to_lat'] = to_lat
    history['to_lon'] = to_lon

    history = enrich_history_routes(route_key, history, railmap)                                                                # Add routes and route's coordinates

    return history


def enrich_history_routes(route_key, history, railmap):
    routes, all_routes_coords = [], []
    for row in history.iterrows():                                                                                              # Loop over every history entry
        row = row[1]
        route = RouteGetter.get_route(route_key, row['Vertrek_code'], row['Bestemming_code'])
        routes.append(route)

        entire_route = []
        gap = False                                                                                                             # True whenever missing track data is gapped with a straight line
        for stop, nextstop in current_and_next(route):
            if nextstop is None: break                                                                                          # If destination is reached
            between_stops = railmap.loc[(railmap['origin'] == stop) & (railmap['to'] == nextstop)]['coordinates'].tolist()      # Get the list, of the coordinates, of the row in railmap that we want
            if between_stops:                                                                                                   # Check if list is empty
                between_stops = between_stops[0]                                                                                # Extract from nested list

            else:
                between_stops = railmap.loc[(railmap['origin'] == nextstop) & (railmap['to'] == stop)]['coordinates'].tolist()
                if between_stops:
                    between_stops = between_stops[0]                                                                            # Extract
                    between_stops = between_stops[::-1]                                                                         # and reverse to correct the order of coordinates.
                else:
                    print("No track coordinates found between: " + stop + " and " + nextstop)
                    gap = True                                                                                                  # No track found, so stop loop and add straight line from
                    continue                                                                                                    # previous end to next start
            if gap:
                gap = False
                entire_route.append([previous_tail, between_stops[0]])                                                          # This adds the missing track
            previous_tail = between_stops[-1]

            entire_route.append(between_stops)                                                                                  # Add parts of a journey to entire journey/route
        all_routes_coords.append(entire_route)                                                                                  # Add entire journey to all journeys/route

    history['route'] = routes
    history['route_coords'] = all_routes_coords
    return history


def get_railmap_data(map_key, refresh=True):

    if not refresh:
        try:
            data = pd.read_pickle("data/railmap/railmap.pkl")
        except FileNotFoundError:
            print("Something went wrong while reading railmap pickle")
            data = get_railmap_data(refresh=True)

    else:

        headers = {
            # Request headers
            'Ocp-Apim-Subscription-Key': map_key
        }

        try:
            conn = http.client.HTTPSConnection('gateway.apiportal.ns.nl')
            conn.request("GET", "/Spoorkaart-API/api/v1/spoorkaart?%s", "{body}", headers)
            response = conn.getresponse()
            data = response.read()
            conn.close()
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))

        data = parse_railmap_data(data)
        data.to_pickle("data/railmap/railmap.pkl")

    return data


def parse_railmap_data(data):
    json_data = json.loads(data)

    # if there is a message there was an error in the request, print the message instead of just throwing an error
    if 'message' in json_data:
        print(json_data['message'])

    json_extracted = json_data['payload']['features']                         # Take features, from payload, from json data.
    df = pd.DataFrame(json_extracted)

    df.insert(1, 'origin', df['properties'].apply(lambda x: x['from']))         # Extract origin from properties column
    df.insert(2, 'to', df['properties'].apply(lambda x: x['to']))               # Extract to
    df['coordinates'] = df['geometry'].apply(lambda x: x['coordinates'])        # Extract coordinates from geometry column
    df = df.drop(['type', 'properties', 'geometry'], axis=1)                    # Drop unnecessary columns

    return df



