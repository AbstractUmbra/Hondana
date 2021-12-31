1.1.7

# Hondana Changelog

## Added
- `Client.get_my_feed` has the new `exluded_groups/uploaders` parameter. (7968bc5283990670323bdaba3ceeaf8b61192a96)
- `Client.manga_feed` has the new `exluded_groups/uploaders` parameter. (7968bc5283990670323bdaba3ceeaf8b61192a96)
- `Client.chapter_list` has the new `exluded_groups/uploaders` parameter. (7968bc5283990670323bdaba3ceeaf8b61192a96)
- `Client.get_custom_list_manga_feed` has the new `exluded_groups/uploaders` parameter. (7968bc5283990670323bdaba3ceeaf8b61192a96)
- `Manga.feed` has the new `exluded_groups/uploaders` parameter. (7968bc5283990670323bdaba3ceeaf8b61192a96)
- `Manga.chapter_list` has the new `exluded_groups/uploaders` parameter. (7968bc5283990670323bdaba3ceeaf8b61192a96)
- `Client.chapter_list`'s `uploader` parameter now also supports `list[str]`. (7968bc5283990670323bdaba3ceeaf8b61192a96)
- `ChapterUpload.__repr__`. (320dc14b27b5acfa79a71a23235402734dccd7f8)


## Changes


## Fixes
- `ChapterUpload.delete_images` now removes them from the internal `uploaded` attribute too, for accurate representation. (cc1e49fa02d01fe9f0e9fbd9fa489272de9d2936)


### Notes
