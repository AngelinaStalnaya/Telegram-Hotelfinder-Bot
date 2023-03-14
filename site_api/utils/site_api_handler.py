import json
from typing import Dict, List

import requests

from database.common.models import Photo
from database.core import crud
from settings import SiteSettings

site = SiteSettings()

headers: Dict = {
    "content-type": "application/json",
    "X-RapidAPI-Key": site.api_key.get_secret_value(),
    "X-RapidAPI-Host": site.host_api
}

url: str = "https://" + site.host_api
params: Dict = {"fragment": "true", "json": "true"}


def _make_get_response(url: str, params: Dict, method: str = "GET", headers: object = headers,
                       success: object = 200) -> requests.Response | int:  # basic response function for 'get' method
    if headers is None:
        headers = headers
    if params is None:
        params = params
    response = requests.request(
        method,
        url,
        headers=headers,
        params=params
    )

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _make_post_response(url: str, json: Dict, headers=headers,
                                             method: str = "POST", success=200) -> requests.Response | int:  # basic response function for 'post' method
    response = requests.request(
        method,
        url,
        json=json,
        headers=headers
    )

    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_location_data(location: str, url: str = url, headers=headers,
                       func=_make_get_response) -> dict:

    url = f"{url}/locations/v3/search"
    location = location.lower()

    querystring = {'q': f'{location}',
                   'locale': 'en_IE',
                   'langid': '6153',
                   'siteid': '300000019'}

    response = func(url, params=querystring, headers=headers)
    response = response.text.encode('utf-8')
    response_location_data = json.loads(response)

    for dict_box in response_location_data['sr']:
        if dict_box['@type'] == 'gaiaRegionResult' and dict_box['regionNames']['lastSearchName'].lower() == location:
            location_data = {
                'gaiaId': dict_box['gaiaId'],
                'coordinates': dict_box['coordinates'],
                'fullName': dict_box['regionNames']['fullName']
            }
            return location_data


def _get_price_sort_available_offers(location: str, sort: str, check_in: str,
                                                              check_out: str, url: str = url,
                                                              headers=headers,
                                                              func=_make_post_response) -> List[Dict]:
    url = f"{url}/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 19,
        "locale": "en_IE",
        "siteId": 300000019,
        "destination": {"regionId": location},
        "checkInDate": {
            "day": int(check_in[0:2]),
            "month": int(check_in[3:5]),
            "year": int(check_in[6:])
        },
        "checkOutDate": {
            "day": int(check_out[0:2]),
            "month": int(check_out[3:5]),
            "year": int(check_out[6:])
        },
        "resultsStartingIndex": 0,
        "rooms": [{"adults": 2}],
        "sort": sort,
        "filters": {"availableFilter": "SHOW_AVAILABLE_ONLY"}
    }
    response = func(url, json=payload, headers=headers)
    response_allprice = json.loads(response.text)
    price_sort_properties = return_property_list(response=response_allprice)
    return price_sort_properties


def _get_bestdeal_available_offers(location_gaia: str, location_lat: str,
                                                            location_long: str, check_in: str,
                                                            check_out: str, cost_max: int,
                                                            cost_min: int, distance_max: int,
                                                            url: str = url, headers=headers,
                                                            func=_make_post_response) -> List[Dict]:
    url = f"{url}/properties/v2/list"

    payload = {
        "currency": "USD",
        "eapid": 19,
        "locale": "en_IE",
        "siteId": 300000019,
        "destination": {"regionId": location_gaia},
        "checkInDate": {
            "day": int(check_in[0:2]),
            "month": int(check_in[3:5]),
            "year": int(check_in[6:])
        },
        "checkOutDate": {
            "day": int(check_out[0:2]),
            "month": int(check_out[3:5]),
            "year": int(check_out[6:])
        },
        "rooms": [{"adults": 2}],
        "resultsStartingIndex": 0,
        "filters": {"availableFilter": "SHOW_AVAILABLE_ONLY",
                    "price": {"max": cost_max, "min": cost_min},
                    'poi': f'{location_lat}, {location_long}:{location_gaia}'
                    }
    }
    response = func(url, json=payload, headers=headers)
    response_bestdeal = json.loads(response.text)
    best_properties = return_property_list(response=response_bestdeal, distance_max=distance_max)
    return best_properties


def _get_property_photos_and_address(property_id: int, url: str = url,
                                                                     headers=headers,
                                                                     func=_make_post_response) -> tuple[int, str]:

    property_photos = list()
    url = f"{url}/properties/v2/detail"

    payload = {
        "currency": "USD",
        "eapid": 19,
        "locale": "en_IE",
        "siteId": 300000019,
        "propertyId": f'{property_id}'
    }
    response = func(url, json=payload, headers=headers)
    response_property_photo = json.loads(response.text)
    gallery_link = response_property_photo['data']['propertyInfo']['propertyGallery']['images']
    all_photos = len(gallery_link)

    for photo_num in range(all_photos):
        load = {'hotel_address': f"{response_property_photo['data']['propertyInfo']['summary']['location']['address']['addressLine']}",
                      'hotel_name': f"{response_property_photo['data']['propertyInfo']['summary']['name']}",
                      'hotel_id': f"{response_property_photo['data']['propertyInfo']['summary']['id']}",
                      'urls': f"{gallery_link[photo_num]['image']['url']}"}
        property_photos.append(load)
    crud.create_many(model=Photo, data=property_photos)

    address = response_property_photo['data']['propertyInfo']['summary']['location']['address']['addressLine']
    return all_photos, address


def _make_property_url(region_id: int, property_id: int) -> str:

    basic_url = 'https://www.expedia.com/'
    hotel_url = f'{basic_url}d{region_id}.h{property_id}.Hotel-Information'
    return hotel_url


def return_property_list(response: json, distance_max: int = None) -> List[Dict]:
    property_list = list()
    if response is not None:
        for property in response['data']['propertySearch']['propertySearchListings']:

            if property['__typename'] == 'Property':
                property_data = {
                    'name': property['name'],
                    'property_id': property['id'],
                    'distance': property['destinationInfo']['distanceFromDestination']['value'],
                    'price_total': f"{property['price']['lead']['amount']} "
                                          f"{property['price']['lead']['currencyInfo']['code']}"
                                          f" {property['price']['displayMessages'][1]['lineItems'][0]['value']}",
                    'price_for_night': property['price']['displayMessages'][2]['lineItems'][0]['value']
                 }
                property_list.append(property_data)
        if distance_max is None:
            return property_list
        else:
            best_properties = [hotel for hotel in property_list if hotel['distance'] <= distance_max]
            return best_properties
    else:
        print('Unreal request data')




class SiteApiInterface:

    @staticmethod
    def get_location(location: str):
        return _get_location_data(location=location)

    @staticmethod
    def get_all_price(location: str, sort: str, check_in: str,
                      check_out: str):
        return _get_price_sort_available_offers(location=location, sort=sort,
                                                check_in=check_in, check_out=check_out,)

    @staticmethod
    def get_bestdeal(location_gaia: str, location_lat: str, location_long: str, check_in: str,
                     check_out: str, cost_max: int, cost_min: int, distance_max: int):
        return _get_bestdeal_available_offers(location_gaia=location_gaia,
                                                   location_lat=location_lat,
                                                   location_long=location_long, check_in=check_in,
                                                   check_out=check_out, cost_max=cost_max,
                                                   cost_min=cost_min, distance_max=distance_max)

    @staticmethod
    def get_property_url(region_id: int, property_id: int):
        return _make_property_url(region_id=region_id, property_id=property_id)

    @staticmethod
    def get_photos_and_address(property_id: int):
        return _get_property_photos_and_address(property_id=property_id)


site_api = SiteApiInterface()

if __name__ == "__main__":

    site_api()
