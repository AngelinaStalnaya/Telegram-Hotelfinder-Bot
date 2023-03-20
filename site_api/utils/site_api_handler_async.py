from typing import Dict, List, Any
from functools import wraps

import aiohttp
import asyncio

from aiogram.utils import json
from aiohttp import ClientSession

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


def attach_session(function):  # decorator for attaching client's session for requests
        @wraps(function)
        async def async_wrapper(*args, **kwargs):
            async with aiohttp.ClientSession() as session:
                result = await function(*args, **kwargs, session=session)
            await asyncio.sleep(0.1)
            return result
        return async_wrapper


@attach_session
async def _make_get_response(url: str, session: ClientSession, params: Dict = params,
                                                      headers: Dict = headers,
                                                      success: object = 200) -> dict | int:   #  basic response function for 'get' method

    async with session.get(url=url, headers=headers,
                                           params=params, allow_redirects=True) as response:

            status_code = response.status
            response_data = await response.json(encoding='utf-8')
    await session.close()

    if status_code == success:
         return response_data
    return status_code


@attach_session
async def _make_post_response(url: str, json: Dict, session: ClientSession, headers=headers,
                                                        success=200) -> dict[str, Any] | int:  # basic response function for 'post' method


    async with session.post(url=url, json=json, headers=headers) as response:
        status_code = response.status
        response_data = await response.json(encoding='utf-8')

    await session.close()

    if status_code == success:
        return response_data
    return status_code


async def _get_location_data(location: str, url: str = url,
                                                  headers=headers, func=_make_get_response) -> dict:

    url = f"{url}/locations/v3/search"
    location = location.lower()

    querystring = {'q': f'{location}',
                   'locale': 'en_IE',
                   'langid': '6153',
                   'siteid': '300000019'}

    response_location_data = await func(url, params=querystring, headers=headers)
    for dict_box in response_location_data['sr']:

        if dict_box['@type'] == 'gaiaRegionResult' and dict_box['regionNames']['lastSearchName'].lower() == location:
            location_data = {
                'gaiaId': dict_box['gaiaId'],
                'coordinates': dict_box['coordinates'],
                'fullName': dict_box['regionNames']['fullName']
            }
            return location_data


async def _get_price_sort_available_offers(location: str, sort: str, check_in: str,
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

    response = await func(url, json=payload, headers=headers)
    price_sort_properties = await return_property_list(response=response)

    return price_sort_properties


async def _get_bestdeal_available_offers(location_gaia: str, location_lat: str,
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

    response = await func(url=url, json=payload, headers=headers)
    best_properties = await return_property_list(response=response, distance_max=distance_max)

    return best_properties


async def _get_property_photos_and_address(property_id: int,
                                                                     url: str = url, headers=headers,
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

    response_property_photo = await func(url=url, json=payload, headers=headers)
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


async def _make_property_url(region_id: int, property_id: int) -> str:

    basic_url = 'https://www.expedia.com/'
    hotel_url = f'{basic_url}d{region_id}.h{property_id}.Hotel-Information'
    return hotel_url


async def return_property_list(response: json, distance_max: int = None) -> List[Dict]:
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
    async def get_location(location: str):
        return await _get_location_data(location=location)

    @staticmethod
    async def get_all_price(location: str, sort: str, check_in: str,
                      check_out: str):
        return await _get_price_sort_available_offers(location=location, sort=sort,
                                                check_in=check_in, check_out=check_out)

    @staticmethod
    async def get_bestdeal(location_gaia: str, location_lat: str, location_long: str, check_in: str,
                     check_out: str, cost_max: int, cost_min: int, distance_max: int):
        return await _get_bestdeal_available_offers(location_gaia=location_gaia,
                                                   location_lat=location_lat,
                                                   location_long=location_long, check_in=check_in,
                                                   check_out=check_out, cost_max=cost_max,
                                                   cost_min=cost_min, distance_max=distance_max)

    @staticmethod
    async def get_property_url(region_id: int, property_id: int):
        return await _make_property_url(region_id=region_id, property_id=property_id)

    @staticmethod
    async def get_photos_and_address(property_id: int):
        return await _get_property_photos_and_address(property_id=property_id)


