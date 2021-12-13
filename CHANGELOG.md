1.0.0

Breaking release!

# Hondana Changelog

## Added
- `hondana.Includes` base type for making `includes[]` paramter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- `hondana.ArtistIncludes` type for helping with Artist based `includes[]` parameter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- `hondana.AuthorIncludes` type for helping with Author based `includes[]` parameter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- `hondana.ChapterIncludes` type for helping with Chapter based `includes[]` parameter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- `hondana.CoverIncludes` type for helping with Cover based `includes[]` parameter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- `hondana.CustomListIncludes` type for helping with CustomList based `includes[]` parameter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- `hondana.MangaIncludes` type for helping with manga based `includes[]` parameter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- `hondana.ScanlatorGroupIncludes` type for helping with ScanlatorGroup based `includes[]` parameter helpers. (5dba67aec3d30918bd7617e4f095d332048cb197)
- Basic error handling to token refresh flow. (ee786994636afd778453f9cb0185715fd38a6484)
- `hondana.Order` enum added for further use in... (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)
- ... `hondana.MangaListOrderQuery`, a query helper for parameters. (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)
- ... `hondana.FeedOrderQuery`, a query helper for parameters. (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)
- ... `hondana.MangaDraftListOrderQuery`, a query helper for parameters. (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)
- ... `hondana.CoverArtListOrderQuery`, a query helper for parameters. (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)
- ... `hondana.ScanlatorGroupListOrderQuery`, a query helper for parameters. (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)
- ... `hondana.AuthorListOrderQuery`, a query helper for parameters. (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)
- ... `hondana.UserOrderQuery`, a query helper for parameters. (661cf4a4a56de100ee1683508df84028694c4073 and 9af0d4c7de571b8215c1fad34cc538af88c714e1)

## Changes
- Added docstrings to missing members, all objects should be documented now. (be77c0c88996b8d3d7f8afc4871baedad0cf2463, 9af0d4c7de571b8215c1fad34cc538af88c714e1 and fb60d698ba936e817397d2e0554ab166f59d859e)
- Stricter pyright rules. (1087a5bbfccc37a3b7c1041e5e9f298ab91da627)
- `hondana.CustomList` now has previously mentioned caching behaviour on method calls. (9f88374000046b8568400a6123e85e14978e74fb)
- `hondana.utils` module was mildly re-written and cleaned up. (692f2ba2fdff5fbb623797c9b5b89cb444f36ace)

## Fixes
- `hondana.MANGADEX_TIME_REGEX` is now fixed to support proper times. (396a067d7df6f84e4b027c86e9e4a127c2d9633f)
- Remove erroneous imports throughout project. (many)

### Notes
