# Hondana Tests

## Primer

I want to note firstly, that no tests here will contact the MangaDex API at any stage.

The reasoning behind this stems from a few things, in no particular order:

- Ratelimits are present, I'd rather a test suite not fail due to this.
- Moral obligation. The idea is to not abuse the API with a barrage of requests that are not necessary, which these would be.
- After having communicated directly with the team who maintain MD (for free, no less!), I'd rather not get beaten up... or worse.

The solution I've decided on, is to keep payloads from the API stored locally. These payloads will be from a specific query, and then with one "complete" payload, and some mangled in some way.

I will maintain these payloads manually, or perhaps have a "one-time" use script any time there is a data change on each payload type.
