3.7.0

API Version 5.12.0

# Hondana Changelog
Hondana release, see below for finer details.

## Added
- `Chapter.is_unavailable` was added to help deal with the DMCA strikes on MangaDex. (4d989fee009f9c61f24c9de4b164b4c81623f9b8)

## Changes
- Internal only changes to the Python tooling (PDM to uv). (f2ea0c6a172c40c6edd39c6fd2d93bc98ef90a3c and 0e2f77326a86967e15ab306d4da8a48f4793998c)
- Internal test case changes. (f471a8f94ede28762aea4a382eec3748eb59e675 and b7433bee1f5c296e6688cf8cbe31e0601e7be9a2)

## Fixes
- `Author/Artist.namicomi` may not actually be present on API responses leading to an internal KeyError. (a7b2bf6f3512fa3eb12dfdccb2604710feb220d0)

### Notes

### Noted Contributors
