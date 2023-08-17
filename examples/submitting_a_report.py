from __future__ import annotations

import asyncio

import hondana

# We need to log in as reports cannot be submitted anonymously.


async def main() -> None:
    async with hondana.Client(client_id="...", client_secret="...") as client:
        # let's get a manga
        manga = await client.get_manga("...")

        # ... but we realise it is incorrect or has the wrong data.
        # we'll submit a report for correction:
        report = hondana.ReportDetails(
            category=hondana.ReportCategory.manga,
            reason=hondana.MangaReportReason.information_to_correct,
            details="The attributed author of this manga is not correct.",
            target_id=manga.id,
        )

        # and we send it off:
        await client.create_report(report)


asyncio.run(main())
