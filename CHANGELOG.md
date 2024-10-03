3.6.0

API Version 5.10.2

# Hondana Changelog
Hondana release, see below for finer details.

## Added

## Changes

## Fixes
- README having incorrect html rendering an underline where it wasn't needed. (e0a1bf0bed28ee5d3ae54bad0fa6b6519c45c2c7)
- Handling of failures in gaining a refresh token, therefor resulting in a re-authentication cycle. (9e8948d9e56f98bb9bd8c8fca663476b5de0c0e9)
- Fix incorrect typing and allowed usage of `QueryTags`. (4aebb64207f8fd0f81cf6acc2bc6c0f641bb433b)
  - Improvements on `QueryTags` internal resolution. (552e980429117dc137cfbaf0e2906bcd1dc8a37a and f54421dccd8f46fc03636e2771512fb51de25b17)
  - Added regression test for above. (bd38de7cc0ddd2828a16d9d57567d12165f5151b)
- Correct aiohttp CookieJar usage. (c799aa32aacd830c635e65a33a4ed70e8adb8b9f)
- Correct overeager sending of authorization headers to all MangaDex related endpoints. (1269b057657388e00ae90273512e3864d64f1850)

- Misc fixes around metadata and tooling updates. (a767411036c275f54ec93823c41792ec4ffc68ef, 52ab3961d7aa67e05bb3df45d65cf951a57e5129)

### Notes

### Noted Contributors

@EvieePy for the README fix.
