3.1.0

API Version 5.6.1

# Hondana Changelog

Mostly a documentation update, but one minor change with `version` parameters.

## Added

## Changes
- Removed `Client.create_settings_template` as this will be a MandaDex admin/staff only endpoint. (078dcad34dd27019ab4240d4c08e8b973ed26a8d)
- Updated documentation for `Client.delete_user`. (715092d40c276b4bc387cb61f60e48bd403825bb)
- Removed useless captcha handling from HTTP request flow. (ba236cd32e0e7ec5ac262f1a098a2d3b3a5fb38b)
  - This actually cannot be done via 3rd party applications, period.
- Updated documentation for `Client.recover_account`. (0057b6ab7c65f2ec148a77d14e4abc8594997872)
- Updated documentation for `Client.get_at_home_url`. (9dcbe5e74f44c7834b98499cec1b9c54d13136a8)
- Removed the `version` parameter for creation endpoints, as this was ignored on MD's side as it is supposed to be provided by the user. (3fefb07d68c848949ed0343c18385cfafd05891a)
- Add some clarity around `publish_at` in the documentation. (ccd3f4d41401f14c915a4810fc12fa06ed5a4bf1)
- Add small informational relating to the `include_future_updates` boolean in feed endpoints. (c077f9331aeaa8e562de0c84a04d8cf1459a40cc)
- Add note about `Client.my_chapter_read_history`. (673d344e9e4d8771c75452bfb209bbb2789c8d7b)

## Fixes

### Notes
- Most changes in this version has been based on information from MangaDex staff themselves, listed below.

### Noted Contributors
@Tristan971 for their feedback on the library and helping clear up some documentation and knowledge inconsistencies.
