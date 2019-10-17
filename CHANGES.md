# ShovelBot v0.2.0

* Fixed the updater crashing while trying to read the settings file.
* Fixed extensions breaking due to being set up on another thread.
* Fixed the Twitch extension not properly emitting a message object.
* Ensured the request factor isn't None.
* Fixed the command parser crashing due to setting path changes.
* Added log statements to the close sequence.
* Ensured the settings dialog is disposed of during the closing sequence as to not hang the application.
* Ensured the token converter uses the proper converter id.
* Fixed the token generator breaking during the 2FA flow.
* Added PRIVMSG parsing.
* Ensuring the bot doesn't attempt to reconnect to Twitch if there's no reason to.


# ShovelBot v0.1.0

* Initial Release
