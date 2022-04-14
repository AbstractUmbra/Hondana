3.0.0

API Version 5.5.8!

# Hondana Changelog

## Added
- `hondana.UploadData` was added as the return type for `ChapterUpload.upload_images` to provide more access to error and success information. (99a7a37c68cebc86094cb1082d426b9b815398d6)

## Changes
- BREAKING: `Client.view_manga` has been deprecated in favour of `Client.get_manga`. (256a0a0a890483a140567681f6e3b15fe194673e)
- BREAKING: `ChapterUpload.upload_images`, and `Client.upload_chapter` now take `pathlib.Path` objects instead of raw `bytes` due to requiring access to the filenames for error checking. (99a7a37c68cebc86094cb1082d426b9b815398d6)

## Fixes
- Internal types fixes to comply with proper practice and pyright usage. (39e317b021d4d7b6f44bddf2c4e6d64e89206621)
- Docs fixes. (27d8312e3576f0fd0c6ac410e7db048f95d76030)

### Notes

### Noted Contributors
