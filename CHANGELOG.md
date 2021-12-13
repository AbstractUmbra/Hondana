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
- `hondana.Order` enum added for further use in... ()
- ... `hondana.MangaListOrderQuery`, a query helper for parameters. ()
- ... `hondana.FeedOrderQuery`, a query helper for parameters. ()
- ... `hondana.MangaDraftListOrderQuery`, a query helper for parameters. ()
- ... `hondana.CoverArtListOrderQuery`, a query helper for parameters. ()
- ... `hondana.ScanlatorGroupListOrderQuery`, a query helper for parameters. ()
- ... `hondana.AuthorListOrderQuery`, a query helper for parameters. ()
- ... `hondana.UserOrderQuery`, a query helper for parameters. ()

## Changes
- Added docstrings to missing members, all objects should be documented now. ()
- Stricter pyright rules. ()

## Fixes
- `hondana.MANGADEX_TIME_REGEX` is now fixed to support proper times. (396a067d7df6f84e4b027c86e9e4a127c2d9633f)

### Notes
