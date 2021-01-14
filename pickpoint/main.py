# made by nkmtn10@gmail.com
# PickPoint all postamate geodata (geojson)
# Problems:
#   0. How often the PickPoint refreshes datafile
#   1. Schedule recording and working time format
#   2. Text encoding(?)

import requests
import xmltodict
import geojson

# URL to the data file provided by the company PickPoint
URL ="https://pickpoint.ru/postamats.xml"


def get_data(url=None):

    if url is None:
        return False

    res = requests.get(URL)
    if res.status_code is 200:
        print("Data successfully extracted")
        return get_geojson(res.content)
    else:
        print("Error while extracting data")
        return False


def get_geojson(res=None):

    if res is None:
        return False

    res = xmltodict.parse(res)

    geo_list = []
    for pt in res['ptinfo']['pt']:
        my_point = geojson.Point((float(pt['longitude'].replace(',', '.')), float(pt['latitude'].replace(',', '.'))))
        my_properties = {"id": pt['PT_ID'],
                         "name": pt['PT_Name'],
                         "region": pt['Region'],
                         "city": pt['City'],
                         "address": pt['ADDRESS'],
                         "hitn": pt['Indoor'],
                         "worktime": pt['WorkTime'],
                         "schedule": pt['DeliverySchedule']}
        my_feature = geojson.Feature(geometry=my_point, properties=my_properties)
        geo_list.append(my_feature)

    return geojson.FeatureCollection(geo_list)


if __name__ == "__main__":
    data = get_data(url=URL)
    f = open('pickpoin.geojson', 'w').write(str(data))



