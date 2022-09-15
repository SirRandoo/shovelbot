"""
This file is part of ShovelBot.

ShovelBot is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

ShovelBot is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
ShovelBot.  If not, see <https://www.gnu.org/licenses/>.
"""
import enum

__all__ = ['Scopes']


class Scopes(enum.Enum):
    # "New Twitch API" scopes
    # Analytics
    READ_EXTENSION_ANALYTICS = 'analytics:read:extensions'
    READ_GAME_ANALYTICS = 'analytics:read:games'
    READ_BITS = 'bits:read'
    RUN_COMMERCIALS = 'channel:edit:commercial'
    MANAGE_BROADCAST = 'channel:manage:broadcast'
    MANAGE_EXTENSIONS = 'channel:manage:extensions'
    MANAGE_REDEMPTIONS = 'channel:manage:redemptions'
    READ_HYPE_TRAIN = 'channel:read:hype_train'
    READ_REDEMPTIONS = 'channel:read:redemptions'
    READ_CHANNEL_SUBSCRIPTIONS = 'channel:read:subscriptions'
    READ_STREAM_KEY = 'channel:read:stream_key'
    EDIT_CLIPS = 'clips:edit'
    EDIT_USER = 'user:edit'
    EDIT_FOLLOWS = 'user:edit:follows'
    READ_BROADCAST = 'user:read:broadcast'
    READ_USER_EMAIL = 'user:read:email'
