"""enums.py.

rustmaps.py - A Python 3 wrapper for the rustmaps.com HTTP REST API
Copyright (C) 2022  Ralph Drake

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from enum import Enum


class MonumentAlignment(Enum):
    """Represents the four cardinal edges of a custom map.

    Used when specifying custom locations for small/large oil rig.

    Thanks to @Mr. Blue#1050 from the RustMaps.com Discord for explaining this.
    """

    TOP = 0
    LEFT = 1
    RIGHT = 2
    BOTTOM = 3
