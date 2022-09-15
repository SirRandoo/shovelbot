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
import dataclasses
import typing

from ..enums import Scopes

__all__ = ['Token']


@dataclasses.dataclass(frozen=True)
class Token:
    client_id: str
    data: str
    scopes: typing.List[Scopes]

    # Scope methods
    def has_scope(self, scope: Scopes) -> bool:
        """Returns whether or not this token has the scope specified."""
        return scope.lower() in self.scopes

    def can_read_extension_analytics(self) -> bool:
        """Whether or not this token can be used to view analytics data for
        its extension."""
        return self.has_scope(Scopes.READ_EXTENSION_ANALYTICS)

    def can_read_game_analytics(self) -> bool:
        """Whether or not this token can be used to view analytics data for
        its game."""
        return self.has_scope(Scopes.READ_GAME_ANALYTICS)

    def can_read_bits(self) -> bool:
        """Whether or not this token can be used to view bit information in
        its account holder's channel."""
        return self.has_scope(Scopes.READ_BITS)

    def can_read_channel_subscriptions(self) -> bool:
        """Whether or not this token can be used to view its account holder's
        subscriber list, and check if a user is subscribed to their channel."""
        return self.has_scope(Scopes.READ_CHANNEL_SUBSCRIPTIONS)

    def can_edit_clips(self) -> bool:
        """Whether or not this token can be used to manage its account holder's
        clips."""
        return self.has_scope(Scopes.EDIT_CLIPS)

    def can_edit_user(self) -> bool:
        """Whether or not this token can be used to manage its account holder's
        account."""
        return self.has_scope(Scopes.EDIT_USER)

    def can_edit_broadcast(self) -> bool:
        """Whether or not this token can be used to edit its account holder's
        broadcast configuration, including extension configuration."""
        return self.has_scope(Scopes.EDIT_USER_BROADCAST)

    def can_read_broadcast(self) -> bool:
        """Whether or not this token can be used to read its account holder's
        broadcast configuration, including extension configurations."""
        return self.has_scope(Scopes.READ_USER_BROADCAST) or self.can_read_broadcast()

    def can_read_email(self) -> bool:
        """Whether or not this token can be used to read its account holder's
        email address."""
        return self.has_scope(Scopes.READ_USER_EMAIL)

    def can_moderate_chat(self) -> bool:
        """Whether or not this token can be used to moderate a chat on behalf
        of the account holder."""
        return self.has_scope(Scopes.MODERATE_CHANNEL)

    def can_edit_chat(self) -> bool:
        """Whether or not this token can be used to send chat and room messages
        on behalf of the token's account holder."""
        return self.has_scope(Scopes.EDIT_CHAT)

    def can_read_chat(self) -> bool:
        """Whether or not this token can be used to read chat and room messages."""
        return self.has_scope(Scopes.READ_CHAT)

    def can_read_whispers(self) -> bool:
        """Whether or not this token can be used to read whispers sent to the
        token's account holder."""
        return self.has_scope(Scopes.READ_WHISPERS)

    def can_send_whispers(self) -> bool:
        """Whether or not this token can be used to send whispers on behalf
        of the token's account holder."""
        return self.has_scope(Scopes.EDIT_WHISPERS)
