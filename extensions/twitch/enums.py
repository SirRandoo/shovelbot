# This file is part of Twitch for ShovelBot.
#
# Twitch for ShovelBot is free software:
# you can redistribute it
# and/or modify it under the
# terms of the GNU General
# Public License as published by
# the Free Software Foundation,
# either version 3 of the License,
# or (at your option) any later
# version.
#
# Twitch for ShovelBot is distributed in
# the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without
# even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with
# Twitch for ShovelBot.  If not,
# see <https://www.gnu.org/licenses/>.
import enum

__all__ = ['Scopes']


class Scopes(enum.Enum):
    # "New Twitch API" scopes
    # Analytics
    READ_EXTENSION_ANALYTICS = 'analytics:read:extensions'
    READ_GAME_ANALYTICS = 'analytics:read:games'
    
    # Bits
    READ_BITS = 'bits:read'
    
    # Channels
    READ_CHANNEL_SUBSCRIPTIONS = 'channel:read:subscriptions'
    
    # Clips
    EDIT_CLIPS = 'clips:edit'
    
    # Users
    EDIT_USER = 'user:edit'
    EDIT_USER_BROADCAST = 'user:edit:broadcast'
    READ_USER_BROADCAST = 'user:read:broadcast'
    READ_USER_EMAIL = 'user:read:email'
    
    # "Chat & PubSub" scopes
    MODERATE_CHANNEL = 'channel:moderate'
    EDIT_CHAT = 'chat:edit'
    READ_CHAT = 'chat:read'
    READ_WHISPERS = 'whispers:read'
    EDIT_WHISPERS = 'whispers:edit'
