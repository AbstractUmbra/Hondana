API Reference
=============

.. currentmodule:: hondana

Client
------
.. autoclass:: Client
    :members:

API Models
----------

Artist
~~~~~~
.. autoclass:: Artist()
    :members:

Author
~~~~~~
.. autoclass:: Author()
    :members:

Chapter
~~~~~~~
.. autoclass:: Chapter()
    :members:

.. autoclass:: ChapterAtHome()
    :members:

.. autoclass:: UploadData()
    :members:

.. autoclass:: PreviouslyReadChapter()
    :members:

Chapter Upload
~~~~~~~~~~~~~~
.. autoclass:: ChapterUpload()
    :members:

Collections
~~~~~~~~~~~
.. autoclass:: MangaCollection()
    :members: items

.. autoclass:: MangaRelationCollection()
    :members: items

.. autoclass:: ChapterFeed()
    :members: items

.. autoclass:: AuthorCollection()
    :members: items

.. autoclass:: CoverCollection()
    :members: items

.. autoclass:: ScanlatorGroupCollection()
    :members: items

.. autoclass:: ReportCollection()
    :members: items

.. autoclass:: UserCollection()
    :members: items

.. autoclass:: CustomListCollection()
    :members: items

.. autoclass:: LegacyMappingCollection()
    :members: items

.. autoclass:: ChapterReadHistoryCollection()
    :members: items

Cover
~~~~~
.. autoclass:: Cover()
    :members:

CustomList
~~~~~~~~~~
.. autoclass:: CustomList()
    :members:

Legacy
~~~~~~
.. autoclass:: LegacyItem()
    :members:

Manga
~~~~~
.. autoclass:: Manga()
    :members:

.. autoclass:: MangaRelation()
    :members:

.. autoclass:: MangaStatistics()
    :members:

.. autoclass:: MangaRating()
    :members:

Query
~~~~~~~~
.. currentmodule:: hondana.query

.. autoclass:: MangaListOrderQuery

.. autoclass:: FeedOrderQuery

.. autoclass:: MangaDraftListOrderQuery

.. autoclass:: CoverArtListOrderQuery

.. autoclass:: ScanlatorGroupListOrderQuery

.. autoclass:: AuthorListOrderQuery

.. autoclass:: UserListOrderQuery

.. autoclass:: ArtistIncludes

.. autoclass:: AuthorIncludes

.. autoclass:: ChapterIncludes

.. autoclass:: CoverIncludes

.. autoclass:: CustomListIncludes

.. autoclass:: MangaIncludes

.. autoclass:: ScanlatorGroupIncludes

.. autoclass:: UserReportIncludes

.. currentmodule:: hondana

Relationship
~~~~~~~~~~~~
.. autoclass:: Relationship()
    :members:

Report
~~~~~~
.. autoclass:: ReportDetails
    :members:

.. autoclass:: UserReport()
    :members:

.. autoclass:: Report()
    :members:

Scanlation Group
~~~~~~~~~~~~~~~~
.. autoclass:: ScanlatorGroup()
    :members:

Tag
~~~
.. autoclass:: Tag()
    :members:

QueryTags
~~~~~~~~~
.. autoclass:: QueryTags
    :members:

Token
~~~~~
.. autoclass:: Permissions()
    :members:

User
~~~~
.. autoclass:: User()
    :members:


Utilities
---------
.. autoclass:: hondana.utils.Route
    :members:

.. autoclass:: hondana.utils.CustomRoute
    :members:

.. autoclass:: hondana.utils.MANGADEX_TIME_REGEX
    :members:

.. autoclass:: hondana.utils.MANGADEX_URL_REGEX
    :members:

.. autofunction:: hondana.utils.php_query_builder

.. autofunction:: hondana.utils.delta_to_iso

.. autofunction:: hondana.utils.iso_to_delta

.. autofunction:: hondana.utils.clean_isoformat


Enumerations
-------------

We provide some enumeration types to avoid the API from being stringly typed
in case the strings change in future.

.. currentmodule:: hondana.query

.. class:: Order
    :canonical: hondana.enums.Order

    Decides the ordering of the query.

    .. attribute:: ascending

        Sorts the query by key ascending.

    .. attribute:: descending

        Sorts the query by key descending.

.. currentmodule:: hondana
.. class:: ContentRating
    :canonical: hondana.enums.ContentRating

    Specifies the content rating of the manga.

    .. attribute:: safe

        Rated safe.

    .. attribute:: suggestive

        Rated suggestive.

    .. attribute:: erotic

        Rated erotic.

    .. attribute:: pornographic

        Rated pornographic.

.. class:: PublicationDemographic
    :canonical: hondana.enums.PublicationDemographic

    Specifies the demographic aim.

    .. attribute:: shounen

        This manga is aimed at shounen fans.

    .. attribute:: shoujo

        This manga is aimed at shoujo fans.

    .. attribute:: josei

        This manga is aimed at josei fans.

    .. attribute:: seinen

        This manga is aimed at seinen fans.

.. class:: CustomListVisibility
    :canonical: hondana.enums.CustomListVisibility

    Specifies the visibility of a custom list.

    .. attribute:: public

        This custom list is public.

    .. attribute:: private

        This custom list is private.

.. class:: ReportCategory
    :canonical: hondana.enums.ReportCategory

    Specifies the category a report belongs to.

    .. attribute:: manga

        This report is about a manga.

    .. attribute:: chapter

        This report is about a chapter.

    .. attribute:: scanlation_group

        This report is about a scanlation group.

    .. attribute:: user

        This report is about a user.

    .. attribute:: author

        This report is about an author.

.. class:: MangaStatus
    :canonical: hondana.enums.MangaStatus

    Specifies the current manga publication status.

    .. attribute:: ongoing

        This manga is currently ongoing.

    .. attribute:: completed

        This manga has completed publication.

    .. attribute:: hiatus

        This manga is currently on hiatus.

    .. attribute:: cancelled

        This manga has been cancelled.

.. class:: ReadingStatus
    :canonical: hondana.enums.ReadingStatus

    Specifies the current reading status for this manga

    .. attribute:: reading

        This manga is currently being read.

    .. attribute:: on_hold

        This manga has been put on hold.

    .. attribute:: plan_to_read

        This manga is currently being planned to read.

    .. attribute:: dropped

        This manga was dropped.

    .. attribute:: re_reading

        This manga is currently being re-read.

    .. attribute:: completed

        This manga has been completed.

.. class:: MangaState
    :canonical: hondana.enums.MangaState

    The current state of this manga draft.

    .. attribute:: draft

        This manga is currently in draft.

    .. attribute:: submitted

        This manga has been submitted.

    .. attribute:: published

        This manga has been published.

    .. attribute:: rejected

        This manga was rejected.

.. class:: MangaRelationType
    :canonical: hondana.enums.MangaRelationType

    Specifies the relation type to the parent manga.

    .. attribute:: monochrome

        The monochrome relation of the manga.

    .. attribute:: main_story

        The main story relation of the manga.

    .. attribute:: adapted_from

        The lead manga this one was adapter from.

    .. attribute:: based_on

        The manga that adapts from this one.

    .. attribute:: prequel

        The prequel to this manga.

    .. attribute:: side_story

        A side story to the current manga.

    .. attribute:: doujinshi

        A doujinshi relation of the current manga.

    .. attribute:: same_franchise

        A manga from the same franchise.

    .. attribute:: shared_universe

        A manga from the same universe.

    .. attribute:: sequel

        A sequel to the current manga.

    .. attribute:: spin_off

        A spin off of the current manga.

    .. attribute:: alternate_story

        An alternate story of the current manga.

    .. attribute:: preserialization

        A preserialization to the current manga.

    .. attribute:: alternate_version

        An alternate version to the current manga.

.. class:: ReportReason
    :canonical: hondana.enums.ReportReason

    A superclass for all Report Reason subclasses.

.. class:: AuthorReportReason
    :canonical: hondana.enums.AuthorReportReason

    Specifies the report reason for author objects.

    .. attribute:: duplicate_entry

        The author is a duplicate entry.

    .. attribute:: information_to_correct

        There is incorrect information in the stored data of this author.

    .. attribute:: other

        Encapsulates misc reporting reasons.

    .. attribute:: troll_entry

        A misleading or intentionally erroneous entry.

.. class:: ChapterReportReason
    :canonical: hondana.enums.ChapterReportReason

    Specifies the report reason for Chapter objects.

    .. attribute:: credit_page_in_the_middle_of_the_chapter

        The credit page for scan/tl/typeset group is in the middle of the chapter.

    .. attribute:: dupplicate_upload_from_same_user_or_group

        This scanlator group or user has a duplicate upload for this chapter.

    .. attribute:: extraneous_political_or_racebaiting_or_offensive_content

        This chapter contains unnecessary content.

    .. attribute:: fake_or_spam_chapter

        This chapter was created to be fake or spam.

    .. attribute:: group_lock_evasion

        This chapter was uploaded by a group evading a lock on their uploading capabilities.

    .. attribute:: images_not_loading

        This chapter has images that will not load.

    .. attribute:: incorrect_chapter_number

        This chapter's number is incorrect.

    .. attribute:: incorrect_group

        This chapter has an incorrect scanlator group assigned.

    .. attribute:: incorrect_or_duplicate_pages

        This chapter has incorrect or duplicate pages.

    .. attribute:: incorrect_or_missing_chapter_title

        This chapter has an incorrect or missing title.

    .. attribute:: incorrect_or_missing_volume_number

        This chapter has an incorrect or missing volume number.

    .. attribute:: missing_pages

        This chapter has missing pages.

    .. attribute:: naming_rules_broken

        This chapter breaks the naming rules/conventions.

    .. attribute:: official_release_or_raw

        This chapter is from an official release or is a direct raw.

    .. attribute:: other

        Encapsulates miscellaneous report reasons.

    .. attribute:: pages_out_of_order

        This chapter has pages that are out of order.

    .. attribute:: released_before_raws_released

        This chapter was released before the source raw.

    .. attribute:: uploaded_on_wrong_manga

        This chapter has been uploaded on the wrong manga.

    .. attribute:: watermarked_images

        This chapter has watermarked images.


.. class:: ScanlationGroupReportReason
    :canonical: hondana.enums.ScanlationGroupReportReason

    Specifies the report reason for Scanlator Group objects.

    .. attribute:: duplicate_entry

        This scanlator group is a duplicate entry.

    .. attribute:: group_claim_request

        This report is a request to claim this group.

    .. attribute:: inactivity_request

        This report is to notify of group inactivity.

    .. attribute:: information_to_correct

        There is information to correct on this group.

    .. attribute:: other

        Encapsulates miscellaneous report reasons.

    .. attribute:: troll_entry

        This group is a troll creation.


.. class:: MangaReportReason
    :canonical: hondana.enums.MangaReportReason

    Specifies the report reason for Manga objects.

    .. attribute:: duplicate_entry

        This manga is a duplicate entry.

    .. attribute:: information_to_correct

        This manga has information to be corrected.

    .. attribute:: other

        Encapsulates miscellaneous report reasons.

    .. attribute:: troll_entry

        This manga is a troll creation.


.. class:: UserReportReason
    :canonical: hondana.enums.UserReportReason

    Specifies the report reason for User objects.

    .. attribute:: offensive_username_or_biography_or_avatar

        This user has an offensive entry on their public profile.

    .. attribute:: other

        Encapsulates miscellaneous report reasons.

    .. attribute:: spambot

        This user is a spambot.
