# rustmaps.py - A Python 3 wrapper for the rustmaps.com HTTP REST API
# Copyright (C) 2022  Ralph Drake
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Wrapper class for the RustMaps.com REST API.

Raises:
    ValueError: _Map seed is outside of allowed bounds._
    ValueError: _Map size is outside of allowed bounds._
    NotImplementedError: _This part of the API isn't implemented_.
    NotImplementedError: _This part of the API isn't implemented_.
    RuntimeError: _The API returned an unhandled exception_.
    HTTPError: _The request returned an erronious HTTP status code_.
"""

import requests
from typing import Union
from . import __version__


class Rustmaps:
    """rustmaps.py Main API Wrapper Class.

    Raises:
        ValueError: _Map seed/size/id is outside of allowed bounds._
        NotImplementedError: _This part of the API wrapper isn't finished._
        RuntimeError: _The API failed to generate the map._
        HTTPError: _The request returned an erronious HTTP status code._
    """

    def __init__(self, api_key: str, staging=False, barren=False,
                 request_timeout=1000):
        """_Initialize API Wrapper with an API key and optional params_.

        Args:
            api_key (str): _36 character UUID API key provided by rustmaps.com_
            staging (bool, optional): _Generate the map on the stagin branch?_
                Defaults to False.
            barren (bool, optional): _Generate a barren map?_
                Defaults to False.
            request_timeout (int, optional): _Timeout for API requests in ms._
                Defaults to 1000 (1 second).
        """
        self.__api_key = api_key
        self.__staging = staging
        self.__barren = barren
        self.__request_timeout = request_timeout

        # internal constants
        self.__API_URL = 'https://rustmaps.com/api/v2'
        self.__HEADERS = {
            'X-API-Key': self.__api_key,
            'User-Agent': f'rustmaps.py/{__version__}',
            'accept': 'application/json'
        }

        # public constants
        self.MIN_MAP_SEED = 0
        self.MAX_MAP_SEED = 2147483645
        self.MIN_MAP_SIZE = 1000
        self.MAX_MAP_SIZE = 6000

    def __validate_map_seed(self, seed: int) -> bool:
        """_Validate user-provided map seed_.

        Args:
            seed (int): _The desired map seed_.

        Raises:
            ValueError: _Raised when provided seed is out of bounds_.

        Returns:
            bool: _`True` when seed is valid. Error raised otherwise_.
        """
        if seed >= self.MIN_MAP_SEED and seed <= self.MAX_MAP_SEED:
            return True
        else:
            raise ValueError((
                f'{seed} is out of range. '
                f'[{self.MIN_MAP_SEED}:{self.MAX_MAP_SEED}]'
            ))

    def __validate_map_size(self, size: int) -> bool:
        """_Validate user-provided map size_.

        Args:
            size (int): _The desired map size_.

        Raises:
            ValueError: _Raised when provided size is out of bounds_.

        Returns:
            bool: _`True` when size is valid. Error raised otherwise._
        """
        if size >= self.MIN_MAP_SIZE and size <= self.MAX_MAP_SIZE:
            return True
        else:
            raise ValueError((
                f'{size} is out of range. '
                f'[{self.MIN_MAP_SIZE}:{self.MAX_MAP_SIZE}]'
            ))

    def __validate_map_id(self, id: str) -> bool:
        raise NotImplementedError

    def __get_map_data(self, url: str) -> Union[list, bool]:
        """_Request info about a map, agnostic of seed/size or mapId_.

        Args:
            url (str): _The API endpoint URL._

        Raises:
            HTTPError: _The request returned an erronious status code._

        Returns:
            Union[list, bool]: _Returns `False` if map doesn't exist, or a
                `list` JSON object with map data._
        """
        r = requests.get(url, headers=self.__HEADERS,
                         timeout=self.__request_timeout)

        # Map exists
        if r.status_code == 200:
            return r.json()
        # Map doesn't exist (hasn't been generated)
        elif r.status_code == 404:
            return False
        # Map is currently generating
        elif r.status_code == 409:
            return r.json()
        # Something has gone horribly wrong!
        else:
            r.raise_for_status()

    def get_map(self, seed: int, size: int) -> Union[list, bool]:
        """_Request info about a map of size `size` and seed `seed`_.

        Args:
            seed (int): _The seed of the map._
            size (int): _The size of the map._

        Returns:
            list: _The JSON response from a successful API request._
            bool: _`False` if the map hasn't been generated yet._
        """
        self.__validate_map_seed(seed)
        self.__validate_map_size(size)

        REQUEST_URL = (
            f'{self.__API_URL}/maps/{seed}/{size}'
            f'?staging={self.__staging}&barren={self.__barren}'
        )

        return self.__get_map_data(REQUEST_URL)

    def get_map_by_id(self, map_id: str) -> Union[list, bool]:
        """_Request info about a map associated with a `map_id` UUID_.

        Args:
            map_id (str): _UUID associated with a generated map._

        Returns:
            list: _The JSON response from a successful API request._
            bool: _`False` if the map hasn't been generated yet._
        """
        # TODO: validate map_id
        # self.__validate_map_id(map_id)

        REQUEST_URL = (
            f'{self.__API_URL}/maps/{map_id}'
            f'?staging={self.__staging}&barren={self.__barren}'
        )

        return self.__get_map_data(REQUEST_URL)

    def list_maps(self, filter: str, page=0):
        """_Search generated maps with filter, return paginated results_.

        Args:
            filter (str): _Proprietary serialized filter data._
            page (int, optional): _Zero-based page number of results._
                Defaults to 0.

        Raises:
            NotImplementedError: _This endpoint is not yet implemented._
        """
        # TODO: Implement this endpoint.
        raise NotImplementedError

    def generate_map(self, seed: int, size: int,
                     callback_url: str = None) -> list:
        """_Request the generation of a new map_.

        Args:
            seed (int): _The seed of the new map._
            size (int): _The size of the new map._
            callback_url (str, optional): _Once map generation is finished,
                rustmaps will send a POST request to this URL._
                Defaults to None.

        Raises:
            HTTPError: _The request returned an erronious status code._
            RuntimeError: _The API failed to generate the map._

        Returns:
            list: _The JSON response data from the API._
        """
        REQUEST_URL = (
            f'{self.__API_URL}/maps/{seed}/{size}'
            f'?staging={self.__staging}&barren={self.__barren}'
        )

        r = requests.post(REQUEST_URL, headers=self.__HEADERS,
                          timeout=self.__request_timeout)

        # Map has started generating
        if r.status_code == 200:
            response_json = r.json()
            response_json['exists'] = False

            return response_json
        # Failed to start generating map (seed/size out of bounds, etc.)
        elif r.status_code == 400:
            if r.json() and r.json()['reason']:
                raise RuntimeError(r.json()['reason'])
            else:
                r.raise_for_status()
        # Map already exists
        elif r.status_code == 409:
            response_json = r.json()
            response_json['exists'] = True

            return response_json
        # Something has gone horribly wrong!
        else:
            r.raise_for_status()
