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

import re
import requests
import time
from math import ceil
from typing import Union
from warnings import warn
from . import __version__
from .enums import MonumentAlignment


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
        self._api_key = api_key
        self._staging = staging
        self._barren = barren
        self._request_timeout = request_timeout

        # List of request timestamps, used for internal rate limits
        # Stored in Epoch format, UTC timezone.
        # max requests within the last 60 seconds: 80
        # max requests within the last 3600 seconds: 3600
        self._request_timestamps = []

        # internal constants
        self._API_URL = 'https://rustmaps.com/api/v2'
        self._HEADERS = {
            'X-API-Key': self._api_key,
            'User-Agent': f'rustmaps.py/{__version__}',
            'accept': 'application/json'
        }
        self._UUID_PATTERN = re.compile(
            r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$',
            re.IGNORECASE
        )

        # public constants
        self.MIN_MAP_SEED = 0
        self.MAX_MAP_SEED = 2147483645
        self.MIN_MAP_SIZE = 1000
        self.MAX_MAP_SIZE = 6000
        self.MAX_REQUESTS_PER_MINUTE = 80
        self.MAX_REQUESTS_PER_HOUR = 3600

    def _is_rate_limited(self) -> bool:
        """Check if we are hitting rustmaps.com's API rate limit.

        Returns:
            bool: `True` if we are rate limited, `False` otherwise.
        """
        # Return early if we don't have any timestamps yet, why not
        if len(self._request_timestamps) == 0:
            return False

        reqs_this_minute = 0
        reqs_this_hour = 0
        now = time.time_ns()

        for stamp in self._request_timestamps:
            # Convert no. of seconds passed since `stamp` to an interger
            stamp_diff = int(ceil((now - stamp) / (10 ** 9)))

            if stamp_diff > 3600:
                self._request_timestamps.remove(stamp)
                continue

            if stamp_diff <= 60:
                reqs_this_minute += 1
            if stamp_diff <= 3600:
                reqs_this_hour += 1

        return (
            (reqs_this_minute >= self.MAX_REQUESTS_PER_MINUTE)
            or
            (reqs_this_hour >= self.MAX_REQUESTS_PER_HOUR)
        )

    def _validate_uuid(self, uuid: str) -> bool:
        return bool(self._UUID_PATTERN.match(uuid))

    def _validate_map_seed(self, seed: int) -> bool:
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

    def _validate_map_size(self, size: int) -> bool:
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

    def _get_map_data(self, url: str) -> Union[list, bool]:
        """_Request info about a map, agnostic of seed/size or mapId_.

        Args:
            url (str): _The API endpoint URL._

        Raises:
            HTTPError: _The request returned an erronious status code._

        Returns:
            Union[list, bool]: _Returns `False` if map doesn't exist, or a
                `list` JSON object with map data._
        """
        if self._is_rate_limited():
            warn(
                'Skipping request because the rate limit is reached.',
                RuntimeWarning,
                stacklevel=2
            )
            return

        self._request_timestamps.append(time.time_ns())
        r = requests.get(url, headers=self._HEADERS,
                         timeout=self._request_timeout)

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
        self._validate_map_seed(seed)
        self._validate_map_size(size)

        REQUEST_URL = (
            f'{self._API_URL}/maps/{seed}/{size}'
            f'?staging={self._staging}&barren={self._barren}'
        )

        return self._get_map_data(REQUEST_URL)

    def get_map_by_id(self, map_id: str) -> Union[list, bool]:
        """_Request info about a map associated with a `map_id` UUID_.

        Args:
            map_id (str): _UUID associated with a generated map._

        Returns:
            list: _The JSON response from a successful API request._
            bool: _`False` if the map hasn't been generated yet._
        """
        if not self._validate_uuid(map_id):
            raise ValueError(f'{map_id} is not a valid UUID')

        REQUEST_URL = (
            f'{self._API_URL}/maps/{map_id}'
            f'?staging={self._staging}&barren={self._barren}'
        )

        return self._get_map_data(REQUEST_URL)

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

    def list_outposts(self) -> Union[list, None]:
        """Fetch a list of custom Outpost layouts available to the user.

        Raises:
            NotImplementedError: This method is not implemented yet.

        Returns:
            list: A list of available custom outpost layouts.
            None: No custom outpost layouts are available.
        """
        # TODO: Also implement class field to store custom outpost list?
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
        if self._is_rate_limited():
            warn(
                'Skipping request because the rate limit is reached.',
                RuntimeWarning
            )
            return

        REQUEST_URL = (
            f'{self._API_URL}/maps/{seed}/{size}'
            f'?staging={self._staging}&barren={self._barren}'
        )

        self._request_timestamps.append(time.time_ns())
        r = requests.post(REQUEST_URL, headers=self._HEADERS,
                          timeout=self._request_timeout)

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

    def generate_custom_map(
        self,
        seed: int,
        size: int,
        name: str = None,
        generate_ring_road=-1,
        remove_small_powerlines=False,
        remove_large_powerlines=False,
        remove_car_wrecks=False,
        remove_rivers=False,
        modify_tiers=False,
        terrain={'enabled': False, 'island_intensity': 0},
        large_oil_rig_pos={
            'enabled': False,
            'alignment': MonumentAlignment.TOP,
            'position': 0.5
        },
        small_oil_rig_pos={
            'enabled': False,
            'alignment': 0,
            'position': 0.5
        },
        custom_outpost={
            'enabled': False,
            'prefab_name': 'default'
        },
        large_monuments={},
        small_monuments={},
        harbors={},
        safezones={},
        water_wells={},
        caves={},
        mountains={},
        quarries={}
    ):
        """Generate a custom map with user-specified parameters.

        Args:
            seed (int): The seed of the map.
            size (int): The size of the map.
            name (str): Unused. Defaults to None.
            generate_ring_road (int, optional): Whether to generate a road that encircles the map. Possible values are: -1 (agnostic), 0 (do not generate), and 1 (force generation). Defaults to -1.
            remove_small_powerlines (bool, optional): Disable small powerline generation? Defaults to False.
            remove_large_powerlines (bool, optional): Disable large powerline generation? Defaults to False.
            remove_car_wrecks (bool, optional): Disable static car wrecks spawning next to roads? Defaults to False.
            remove_rivers (bool, optional): Disable river generation? Defaults to False.
            modify_tiers (bool, optional): Enable arbitrary monument placement for better odds of generating desired monuments. Defaults to False.
            terrain (dict, optional): Define the amount of smaller islands that spawn around the map. Set island_intensity to 0 for no islands, up to 10 for lots of islands. Defaults to {'enabled': False, 'island_intensity': 0}.
            large_oil_rig_pos (dict, optional): Define a custom spawn position on the map's edge for large oil rig. Defaults to { 'enabled': False, 'alignment': MonumentAlignment.TOP, 'position': 0.5 }.
            small_oil_rig_pos (dict, optional): Define a custom spawn position on the map's edge for small oil rig. Defaults to { 'enabled': False, 'alignment': 0, 'position': 0.5 }.
            custom_outpost (dict, optional): Specify a custom Outpost prefab to use during generation. Defaults to { 'enabled': False, 'prefab_name': 'default' }.
            large_monuments (dict, optional): Dict of large monuments and their generation options. Defaults to {}.
            small_monuments (dict, optional): Dict of small monuments and their generation options. Defaults to {}.
            harbors (dict, optional): Dict of harbor monuments and their generation options. Defaults to {}.
            safezones (dict, optional): Dict of safe zone monuments and their generation options. Defaults to {}.
            water_wells (dict, optional): Dict of water well monuments and their generation options. Defaults to {}.
            caves (dict, optional): Dict of cave prefabs and their generation options. Defaults to {}.
            mountains (dict, optional): Dict of mountain prefabs and their generation options. Defaults to {}.
            quarries (dict, optional): Dict of quarry monuments and their generation options. Defaults to {}.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """ # noqa E501
        # TODO: implement enum for generate_ring_road?
        # TODO: define "default" dicts for large_monuments, small_monuments,
        #       harbors, safezones, water_wells, caves, mountains, and quarries
        raise NotImplementedError
