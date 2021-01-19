# made by nkmtn10@gmail.com
# Cantata points geodata (geojson)

import requests
import geojson
import json

URL_CITY = "https://app.cantata.ru/city_tree"
URL_EXTRACT = "https://app.cantata.ru/shops?city="
PARAM_EXTRACT = "&limit=1000"

#
# def get_stations():
#


def extract_cites(url):
    data = requests.get(url).json()

    cites = []
    for country in data['data']:
        for district in country['items']:
            for city in district['items']:
                cites.append(city['name'])
    return cites


def extract_points(url_cites, url_points, url_param):
    cites_list = extract_cites(url_cites)

    if not cites_list:
        return 'False'

    days = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    feature_list = []

    print(cites_list, "\n\n")
    for city in cites_list:
        url = url_points + city + url_param
        res = requests.get(url).json()

        if not res["data"]:
            continue

        for point in res["data"]:

            metro_list = []
            if point["station"]:
                for station in point["station"]:
                    metro_st = {
                        "name": station["name"],
                        "coordinates": [station["lon"], station["lat"]]
                    }
                    metro_list.append(metro_st)

            feature = {
                "type": "Feature",
                "properties": {
                    "address": "???",
                    "name": point["name"],
                    "schedule": {
                        "days": str(days[int(point["working_times"][0]["dayFrom"])])
                                + "-" + str(days[int(point["working_times"][0]["dayTo"])]),
                        "time": str(point["working_times"][0]["timeFrom"])
                                + "-" + str(point["working_times"][0]["timeTo"])
                    },
                    "metro": metro_list
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [point["lon"], point["lat"]]
                }
            }
            feature_list.append(feature)
    return geojson.FeatureCollection(feature_list)


if __name__ == '__main__':
    geodata = extract_points(URL_CITY, URL_EXTRACT, PARAM_EXTRACT)
    if geodata == 'False':
        exit(1)
    f = open('cantata.geojson', 'w').write(str(geodata))
