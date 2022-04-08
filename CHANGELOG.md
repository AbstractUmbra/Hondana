2.2.2

API Version 5.5.8!

# Hondana Changelog

## Added
- Added a depreacted utility decorator for use in deprecated methods. (14a7db9837bbe78212c462f845278777c246e3bf)
- `end` key-word argument in `Chapter.download` for the ability to download select pages. (4cdc304481216ac080fc9b8e8bf18696449e022b)
- `Chapter.download_bytes` for downloading chapter images and yielding the raw bytes, rather than dumping to a file. (4cdc304481216ac080fc9b8e8bf18696449e022b)
- Add capability to edit chapters with `ChapterUpload` and all helper methods. (97689c8980707905a0448b07264820ef1508315f)

## Changes
- GitHub actions have been improved to use newer versions and caching where necessary. (d379cbaeaa55d323c7898490c2578deb4a3ddf7f and 81d84279ca7dc71c0d1989506cc9db39bddf4dce)

## Fixes
- Internal utility fixes for the relationship parsing utility. (3c60835c635bc17de80e8fd5f283780c549b0521 and b11fc4f0dd3c745c262e7a768842aa22a4c748c8)
- Fixes `title` and `volume` parameters of `Client.upload_session` as they should have been optional. (12d1cf4f97913204000ebfb5b384ae5f3a061f47 and 5d0dfe3f4c58c03619463c9a194199db27922f4e)
    - Also fixed a bug in the chapter upload process thanks to incorrect documentation. (12d1cf4f97913204000ebfb5b384ae5f3a061f47)

### Notes
- `Client.view_manga` is marked as deprecated and due for removal in version 3.0 in favour of `Client.get_manga`.
- I have tested the upload capabilities as best I can using the [official test manga](https://mangadex.org/title/f9c33607-9180-4ba6-b85c-e4b5faee7192/official-test-manga).

### Noted Contributors
@PythonCoderAS - For working on 4cdc304481216ac080fc9b8e8bf18696449e022b and improving the library.
