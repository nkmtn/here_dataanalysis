import requests
import geojson
import json
import re
from bs4 import BeautifulSoup

URL = "https://grozd.ru/Customer/AddressPopup?_=1610473258319"


def extract_data_json(url):
    res = requests.get(f'{url}')

    # Парсинг полученной HTML разметки
    soup = BeautifulSoup(res.text, 'html.parser')

    # Извлекаем массив объектов по тегу <script>
    scripts = soup.findAll('script')

    # Извлечение данных из нужного скрипта
    for index, script in enumerate(scripts):
        script_content = script.string

        # Проверка на наличие объекта с данными о пунктах
        if script_content is not None and "console.log" in script_content:
            match = re.findall(r"console.log\((.+)\);\\n *\$\(document\)\.ready", str(script_content))
            match = str(match[0]).replace('\\"', '\"')
            data = json.loads(match)

            return parse_detailed_info(data)

    print("Error while extracting data")
    return False


# Вспомагательная функция преобразования данных
def parse_detailed_info(data_json):
    data = data_json["ShippingMethods"][1]["PickupPoints"]
    for obj in data:

        feature = {}

        try:
            feature = {
                "properties": {
                    "address": obj['Address']['Address1'],
                    "phone": obj['Address']['PhoneNumber'],
                    "schedule": obj["Schedule"]
                },
                "coordinates": {
                    "lat": float(obj["GeoLat"]),
                    "lon": float(obj["GeoLon"])
                }
            }
        except:
            feature = {
                "properties": {
                    "address": obj['Address']['Address1'],
                    "phone": None,
                    "schedule": None,
                },
                "coordinates": {}
            }

        yield feature


def to_geojson(features):
    geo_list = []
    for feature in features:
        geo_feature = {
            "type": "Feature",
            "properties": feature["properties"],
            "geometry": {
                "type": "Point",
                "coordinates": [feature["coordinates"]['lon'], feature["coordinates"]['lat']]
            }
        }
        geo_list.append(geo_feature)
    return geojson.FeatureCollection(geo_list)


if __name__ == '__main__':
    data = to_geojson(extract_data_json(URL))
    f = open('gvozd.geojson', 'w').write(str(data))
