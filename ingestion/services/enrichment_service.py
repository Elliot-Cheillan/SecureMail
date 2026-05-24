import asyncio
import aiohttp
import asyncwhois
from datetime import datetime
import logging
from ingestion.config import HTTP_CONCURRENCY, RDAP_CONCURRENCY, BATCH_SIZE

logger = logging.getLogger(__name__)


async def _get_creation_date(
    client, domain, cache, rdap_semaphore
):  # the requests limits is on config, don't touch it or the database will have many missing values
    if not domain or domain == "Unknown":
        return "Unknown"
    if domain in cache:
        return cache[domain]

    async with rdap_semaphore:
        try:
            _, parsed = await asyncio.wait_for(
                client.aio_rdap(domain),
                timeout=3.0,
            )
            date = parsed.get("created")

            if isinstance(date, datetime):
                creation = date.strftime("%Y-%m-%d")
            elif isinstance(date, str):
                creation = date[:10]
            else:
                creation = "No Info"

        except asyncio.TimeoutError:  # some conlusion to make if it return an error :
            creation = "Timeout"  # dead or unreachable domain (suspicious)
        except Exception as e:
            msg = str(e).lower()
            if "404" in msg or "not found" in msg:
                creation = "Protected"  # domain exists but info is hidden (suspicious but could be a famous domain or site)
            elif "429" in msg:
                creation = "Rate Limited"  # too many requests — the RDAP is already very low, should make a cache but it's too hard
            elif "422" in msg or "400" in msg:
                creation = "Invalid"  # invalid URL or asyncwhois lib issue (can't do anything more)
            elif "403" in msg:
                creation = "Forbidden"  # access deliberately denied (very suspicious)
            else:
                creation = "Error"

    cache[domain] = creation
    return creation


async def _get_redirect_url(
    session, url, http_semaphore
):  # the requests limit is in config, can touch it i didn't try with more but no problem with concurrency at 100
    # and this is the rdap concurrency the real problem
    if not url or url == "Unknown":
        return "Unknown"

    async with http_semaphore:
        try:
            async with session.head(
                url,
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=3),
                ssl=False,
            ) as response:
                final = str(response.url)
                return final if final != url else "No Redirect"

        except asyncio.TimeoutError:  # some interpretations of errors / returns values
            return "Timeout"  # dead or slow link (suspicious if recent)
        except aiohttp.ClientSSLError:
            return "SSL Error"  # invalid certificate (very suspicious)
        except aiohttp.ClientConnectionError:
            return (
                "Connection Error"  # dead site or expired domain (suspicious if recent)
            )
        except aiohttp.TooManyRedirects:
            return "Redirect Loop"  # redirect loop (classic spam/ad pattern)
        except Exception as e:
            msg = str(e).lower()
            if "403" in msg:
                return "Forbidden"  # access denied (may be anti-bot, not necessarily suspicious)
            elif "404" in msg:
                return "Not Found"  # dead link (suspicious if recent)
            else:
                return "Error"


async def _enrich_all(cursor, conn):
    # it normally fetch only links not enriched, the batch size is 2000 and you can change it in config, may be a lot
    # cause i don't thin anyone will insert more than 2000 mails in one session
    cursor.execute(
        """
        SELECT ID, URL, Domain FROM Links
        WHERE Domain_Creation_Date = 'Not Computed'
           OR Redirect_URL = 'Not Computed'
    """
    )
    links = cursor.fetchall()

    if not links:
        logger.info("No links to enrich.")
        return

    logger.info(f"{len(links)} links to enrich.")

    client = asyncwhois.DomainClient()
    http_semaphore = asyncio.Semaphore(HTTP_CONCURRENCY)
    rdap_semaphore = asyncio.Semaphore(RDAP_CONCURRENCY)
    domain_cache = {}
    processed = 0

    async with aiohttp.ClientSession(
        headers={"User-Agent": "Mozilla/5.0"},
        connector=aiohttp.TCPConnector(limit=HTTP_CONCURRENCY),
    ) as session:

        for i in range(0, len(links), BATCH_SIZE):
            batch = links[i : i + BATCH_SIZE]

            rdap_tasks = [
                _get_creation_date(client, domain, domain_cache, rdap_semaphore)
                for _, _, domain in batch
            ]
            redirect_tasks = [
                _get_redirect_url(session, url, http_semaphore) for _, url, _ in batch
            ]

            rdap_results, redirect_results = await asyncio.gather(
                asyncio.gather(
                    *rdap_tasks, return_exceptions=True
                ),  # rdap is way too long compared to redirect, it must take some time for mails with lot of links
                asyncio.gather(*redirect_tasks, return_exceptions=True),
            )

            cursor.executemany(
                "UPDATE Links SET Domain_Creation_Date = ?, Redirect_URL = ? WHERE ID = ?",
                [
                    (
                        rdap if not isinstance(rdap, Exception) else "Error",
                        redirect if not isinstance(redirect, Exception) else "Error",
                        link_id,
                    )
                    for (link_id, _, _), rdap, redirect in zip(
                        batch, rdap_results, redirect_results
                    )
                ],
            )
            conn.commit()

            processed += len(batch)
            if processed % 2000 == 0 or processed == len(links):
                logger.info(
                    f"Enrichment: {processed}/{len(links)} links processed."
                )  # the logger have a file in pipeline root, but may not be useful since it's just inserts progression or errors


def enrich_links(cursor, conn):
    asyncio.run(_enrich_all(cursor, conn))
