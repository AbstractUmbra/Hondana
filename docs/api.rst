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

Chapter Upload
~~~~~~~~~~~~~~
.. autoclass:: ChapterUpload
    :members:

Collections
~~~~~~~~~~~
.. autoclass:: hondana.collections.BaseCollection
    :members: items

.. autoclass:: MangaCollection
    :members: items

.. autoclass:: MangaRelationCollection
    :members: items

.. autoclass:: ChapterFeed
    :members: items

.. autoclass:: AuthorCollection
    :members: items

.. autoclass:: CoverCollection
    :members: items

.. autoclass:: ScanlatorGroupCollection
    :members: items

.. autoclass:: ReportCollection
    :members: items

.. autoclass:: UserCollection
    :members: items

.. autoclass:: CustomListCollection
    :members: items

.. autoclass:: LegacyMappingCollection
    :members: items

Cover
~~~~~
.. autoclass:: Cover()
    :members:

CustomList
~~~~~~~~~~
.. autoclass:: CustomList()

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

Relationship
~~~~~~~~~~~~
.. currentmodule:: hondana

.. autoclass:: Relationship()
    :members:

Report
~~~~~~

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

Enumerations
-------------

We provide some enumeration types to avoid the API from being stringly typed
in case the strings change in future.

.. currentmodule:: hondana.query
.. class:: Order

    Decides the ordering of the query.

    .. attribute:: ascending

        Sorts the query by key ascending.

    .. attribute:: descending

        Sorts the query by key descending.

.. currentmodule:: hondana
.. class:: ContentRating

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

    Specifies the visibility of a custom list.

    .. attribute:: public

        This custom list is public.

    .. attribute:: private

        This custom list is private.

.. class:: ReportCategory

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
