1.1.6

# Hondana Changelog

## Added
- `ChapterUpload.abandon` method has been added. (b9d8593c5d9904888a8bdf7bd5cef9ca9bbe49ba)
- `Client.abandon_upload_session` method was added for ease, so you don't need to open the context manager to abandon one. (732a7b1e6de9ea0f10662fad0e91a16e101e7d8c)

## Changes
- `ChapterUpload` methods now have authentication checks applied. (b9d8593c5d9904888a8bdf7bd5cef9ca9bbe49ba)
- `ChapterUpload` http methods have been cleaned up as needed. (b9d8593c5d9904888a8bdf7bd5cef9ca9bbe49ba)

## Fixes
- `ChapterUpload` no longer tries to commit when you abandon the current session. (0648a13db9e5400006b727bf43b962344b4f154d)


### Notes
