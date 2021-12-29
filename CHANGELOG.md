1.1.5

# Hondana Changelog

## Added
- `hondana.chapter.ChapterAtHome` type added for ease of use. (75681c2d091459b3cee79819ab8fcb09e77cbb7d)
- Added `__eq__` and `__ne__` to primary library objects for use. (75681c2d091459b3cee79819ab8fcb09e77cbb7d, 9694dfac98039e96ee5f233e114984f0cf100910 and d1cc78a1787dc50462898c763a3570dff5def8e9)
- `Chapter.external_url` attribute added as this was missed at an earlier stage. (75681c2d091459b3cee79819ab8fcb09e77cbb7d)
- `hondana.ChapterUpload` has been added as a first attempt to upload chapters to MangaDex. (85ef3741b441c86397f193dce3609e682a0fae8a)
- `hondana.utils.delta_to_format` helper util was added to convert a `datetime.timedelta` to valid ISO8601 DateInterval string. (8d2e2e2fd3cc16eaa534b6a265cb6e0f4837785b)

## Changes
- `Client.create_scanlator_group`'s `publish_delay` parameter has changed to accept both `datetime.timedelta` and `str`. (8d2e2e2fd3cc16eaa534b6a265cb6e0f4837785b)
- `Client.update_scanlator_group`'s `publish_delay` parameter has changed to accept both `datetime.timedelta` and `str`. (8d2e2e2fd3cc16eaa534b6a265cb6e0f4837785b)
- `ScanlatorGroup.update`'s `publish_delay` parameter has changed to accept both `datetime.timedelta` and `str`. (8d2e2e2fd3cc16eaa534b6a265cb6e0f4837785b)

## Fixes


### Notes
