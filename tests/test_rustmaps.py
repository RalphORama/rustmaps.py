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

import pytest
import random
from rustmaps import __version__
from rustmaps import Rustmaps
from os import getenv

RUSTMAPS_API_KEY = str(getenv('RUSTMAPS_API_KEY'))
MAP_SEED = 590877946
MAP_SIZE = 2500
MAP_ID = '474b4c64-ab86-4128-a075-e88737fa5820'


@pytest.mark.dependency()
def test_version():
    """Assert version number is correct."""
    assert __version__ == '0.1.0', "rustmaps.py is the wrong version."


@pytest.mark.dependency(depends=['test_version'])
def test_api_key():
    """Assert we successfully retrieved the API key from its env var."""
    assert len(RUSTMAPS_API_KEY) == 36, 'RUSTMAPS_API_KEY is not 36 chars.'


@pytest.mark.dependency(depends=['test_version', 'test_api_key'])
def test_callback_url():
    """Send a test payload to the callback URL to make sure it's live."""
    pass


# create API wrapper object we'll use for the rest of our tests
w = Rustmaps(RUSTMAPS_API_KEY)


@pytest.mark.dependency(depends=['test_version', 'test_api_key'])
def test_get_map_by_seed():
    """Make sure map seed, size, and ID all match so we know tests are sane."""
    print(
        f'Fetching details about map with seed {MAP_SEED} and size {MAP_SIZE}'
    )

    map_data = w.get_map(MAP_SEED, MAP_SIZE)
    map_id = map_data['id']

    assert map_id == MAP_ID, (
        f"get_map() returned unexpected ID {map_id}"
    )


@pytest.mark.dependency(depends=['test_version', 'test_api_key'])
def test_get_map_by_id():
    """Request info about a map using its UUID designator."""
    map_data = w.get_map_by_id(MAP_ID)
    map_seed = map_data['seed']
    map_size = map_data['size']

    assert map_seed == MAP_SEED
    assert map_size == MAP_SIZE


@pytest.mark.dependency(depends=['test_version', 'test_api_key'])
def test_list_maps():
    """Test searching for maps using a serialized filter."""
    # TODO: implement this test when the function itself is implemented
    pass


@pytest.mark.dependency(depends=['test_version', 'test_api_key'])
def test_generate_new_map_nocallback():
    """Generate a new map without a callback URL."""
    random_seed = random.randint(w.MIN_MAP_SEED, w.MAX_MAP_SEED)
    random_size = random.randint(w.MIN_MAP_SIZE, w.MAX_MAP_SIZE)

    r = w.generate_map(random_seed, random_size)

    assert r['exists'] is False, (
        f'Map size {random_size} with seed {random_seed} already exists.'
    )
    assert len(r['mapId']) == 36, (
        f"Expected 36 char UUID for mapId, got {r['mapId']} instead."
    )


@pytest.mark.dependency(depends=['test_version', 'test_api_key'])
def test_generate_existing_map_nocallback():
    """Generate an existing map without a callback URL."""
    r = w.generate_map(MAP_SEED, MAP_SIZE)

    assert r['exists'] is True
    assert r['mapId'] == MAP_ID


@pytest.mark.dependency(depends=['test_version', 'test_api_key', 'test_callback_url'])
def test_generate_new_map_with_callback():
    """Generate a new map, make sure callback URL is used."""
    pass


@pytest.mark.dependency(depends=['test_version', 'test_api_key', 'test_callback_url'])
def test_generate_existing_map_with_callback():
    """Generate an existing map, make sure callback URL is used."""
    pass
