3.4.6

API Version 5.7.5

# Hondana Changelog
Fix Release.

## Added

## Changes
- Rename `Client.permissions` to `Client.user_info`. (6c5fbacf296ed510090714362bc9bb0710c00b5d)

## Fixes
- Fix import paths potentially shadowing builtin paths, namely `token` and `types`. (6c5fbacf296ed510090714362bc9bb0710c00b5d)

### Notes
The above fix should have been a breaking change, but as it was not to the "user facing" part of the codebase, mainly the
types submodule and renaming of `token.Permissions` to `user.UserInfo`.
I expect this will be a breaking change in a very minute number of usercode, and can only offer an apology for this.

### Noted Contributors
