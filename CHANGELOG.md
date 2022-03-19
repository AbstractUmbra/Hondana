2.1.2

API Version 5.5.7!

# Hondana Changelog

## Added

## Changes

## Fixes
- `ScanlatorGroup.publish_delay` is now (correctly) Optional. (2ae4806997cae6e54e785c4e6e906ffd6a9032f3)
- New utility added and utilised for sending datetimes to mangadex. It now cleans and coverts them to UTC from aware timezones. (11ff66854a82168a2fa0bce104f82d7fb63469f4)
- `Cover.url` now supports passing a parent manga id, as it is generally a "sub-relationship" meaning it has no relationships to parse for the parent manga. (802795d9f92a3d06e0e1bcb21d1602a6ad0c3b67)

### Notes
- `Client.view_manga` method has been marked as deprecated in favour of `Client.view_manga` and will be removed in version 3.0. (588c2fdc2956db5435c2aa5792281d3a78ef7396)
- Due to this being a fix release, there is some pending internal changes that are not fully implemented across the board.

### Noted Contributors
@Axelancerr - cleaning up my bad grammar all year 'round.
