3.5.0

API Version 5.10.2

# Hondana Changelog
Hondana release, see below for finer details.

## Added
- Add our own twist on the MangaDex logo for Hondana. (c07e92c4cc3844f4e6207f62b6429d2b3c522676)
- Actions workflows now cache poetry installs and their venvs per Python version. (a38d458b1aae182db53e0711e228eea4f9dbdedf and aa5478f717021f6f05f5e8beb06249abc3624e07)
- OAuth2 authentication flow. (34cf81b7e906efb091a964f874355c48e5d31332, 1ffd47337522881f6171b155f5aa5cf590a750ff, 1d461960c9d13d6ea62725201a077ad2bc45030b, 723a3f2b59b5f558bc896a5e8f5ca6e26d1fd398, 8e595d5f9b7ffccd3e9aa1f35a80b9d9b0e1f7b6, 1829a611ee48258f927eea085e9c80a1e52d63cd, 004b1219e64034fca29431abdb7631ea87be70b7)
- Capability of using `Client` as a context manager for entry and exit cleanup. (c6048469de99e063dd76425fffa6ce7fa81bc03e)
- Add `exLicensed` key to ScanlatorGroup. (feaa7a71acda325ff77f0dfa0c8d75cd70ec84ce)
- `utils.to/from_json` is now within the public API. (7ceade163906494caa12e059deeb6e8c3eca25d7, 69e944d79d92a89dbdf39a9b3df9bb1f0372685b)
- Added capability to use the [dev api](https://api.mangadex.dev). (fe9caff66db7057aebcb2b8f47e427fed226462d and d8e5c6c74f7187df586d86cf602d3c2b20cbc5d1)
- Add NamiComi to `Author/Artist` types. (23adaf289445956924d916b64cc1590fb4d5f9df)
- Add a way to check if an upload requires approval. (f745f6fd29a2ec12b404b2b2c51239205ec0cb55)

## Changes
- Remove `.webp` from allowed image formats as Mangadex doesn't support them. (9686262ee65839e8993cb77b7d030ac982dc054f)
- Several iterations of updating dependencies. (Too many SHAs to list)
- Switch to dedicated `pyright` workflow versus manually installing and running it. (c2e846ff95cd07023f5ebe2160f5d57b71ef1ddc)
- Utilise speedier json parsing for local json stores, if present. (67b6997cb07ae0fc856b1db8eef4e01cea374149)
- Test payload updates. (Too many SHAs to list)
- Revamped the documentation. (9e506aeaa67a07401d8bc5c7a910374682088eb6, 1ba07e882929fec0dde37720d7a17f6a8339f072)
- Fixed library's tooling to account for the fact it is 3.11+. (1db76d08aaa4c29fd9a7aaadc8661a8c3b818fd7, 8d942ffe6fc01fed6beb9de8811b17a283ec5a4b, 8d7b891e645075426a5cb136795ddfd740066007, dfcdcc2b4a484d053a244a3a59e57666a769877a)
- Update Manga report reasons. (5a196bc0d78f2113faa9f4bb54c5484b4e9a4d22 and 661339ae9adaefdb4fbfa333d7bf647f3f142dc7)
- Update Manga tags. (de07abfb8d859c67296db15111227d589058a962)

## Fixes
- ReadTheDocs configuration file for building with later poetry versions. (116107be7666e1b35a622703a3bd9ec4b5176855)
- Fix incorrect query parameter. (e47dfbca444edd45b1f04b7eb169a8e801e7548b)
- Amended debug logging to restrict sensitive info that was needlessly included. (4a48b94669ecfdfbf080d5e01d496e27466b2221)
- Allow passing `None` to the `year` parameter of `Client.manga_list`. (bc0451b0b9d4596e718fc15a415cf99f32ffa66f, 308f061863e855c68c0729fc8d5e1156980650c0)

### Notes
Apologies for the massive changelog, hopefully nothing is missed!

### Noted Contributors
@Random-Cow for fixing a query parameter. (e47dfbca444edd45b1f04b7eb169a8e801e7548b)
@oliver-ni for touching up and correcting my bad edit of the logo. (c07e92c4cc3844f4e6207f62b6429d2b3c522676)
