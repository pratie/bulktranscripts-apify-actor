"""YouTube Transcripts in Bulk: an Apify Actor on top of the BulkTranscripts API.

Single videos go to GET /api/v1/transcript. Channels and playlists start a
bulk job (POST /api/v1/bulk), which BulkTranscripts runs on its own servers;
the Actor waits for it, pages through the outcomes, and reads each finished
transcript back. Those reads are free, because a bulk job puts every video in
the caller's library first. One dataset row per video.

Credits are the caller's own: the run uses the BulkTranscripts API key from
the input, so a transcript costs one credit the first time and nothing after.
"""
from __future__ import annotations

import asyncio
import re
from urllib.parse import parse_qs, urlparse

import httpx
from apify import Actor

API = "https://bulktranscripts.co/api/v1"
KEY_URL = "https://bulktranscripts.co/app?tab=mcp"
PRICING_URL = "https://bulktranscripts.co/#pricing"
USER_AGENT = "bulktranscripts-apify-actor/1.0"

VIDEO_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
PATH_VIDEO = re.compile(r"/(?:shorts|live|embed|v)/([A-Za-z0-9_-]{11})")

# Outcomes a bulk job reports per video. ok/cached have a transcript in the
# caller's library; the rest are reported as they are.
HAS_TRANSCRIPT = {"ok", "cached"}


class OutOfCredits(Exception):
    pass


class ApiFailure(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def video_id_of(raw: str) -> str | None:
    """The 11-character video id for a video link, or None for anything else
    (playlists and channels go through a bulk job)."""
    text = raw.strip()
    if VIDEO_ID.match(text):
        return text
    try:
        url = urlparse(text if "://" in text else "https://" + text)
    except ValueError:
        return None
    host = (url.hostname or "").lower()
    if host.endswith("youtu.be"):
        vid = url.path.strip("/").split("/")[0]
        return vid if VIDEO_ID.match(vid) else None
    if "youtube.com" not in host:
        return None
    if url.path == "/watch":
        vid = (parse_qs(url.query).get("v") or [""])[0]
        return vid if VIDEO_ID.match(vid) else None
    match = PATH_VIDEO.search(url.path)
    return match.group(1) if match else None


class Client:
    def __init__(self, api_key: str):
        self.http = httpx.AsyncClient(
            base_url=API,
            headers={"Authorization": "Bearer " + api_key, "User-Agent": USER_AGENT},
            timeout=httpx.Timeout(120.0, connect=15.0),
        )

    async def close(self) -> None:
        await self.http.aclose()

    async def call(self, method: str, path: str, **kwargs) -> dict:
        """One API call with the waits the API asks for. Rate limits and
        busy servers are retried after Retry-After; network errors and 5xx
        a few times with backoff."""
        attempt = 0
        while True:
            attempt += 1
            try:
                response = await self.http.request(method, path, **kwargs)
            except httpx.HTTPError as exc:
                if attempt >= 4:
                    raise ApiFailure(0, "network_error", "Could not reach BulkTranscripts: %s" % exc)
                await asyncio.sleep(5 * attempt)
                continue
            try:
                body = response.json()
            except ValueError:
                body = {}
            if response.status_code < 400:
                return body
            error = body.get("error") if isinstance(body.get("error"), dict) else {}
            code = error.get("code") or "http_%d" % response.status_code
            message = error.get("message") or response.text[:300]
            if response.status_code in (429, 503) and attempt < 12:
                wait = _retry_after(response, error)
                Actor.log.info("BulkTranscripts asked us to wait %ss (%s).", wait, code)
                await asyncio.sleep(wait)
                continue
            if response.status_code >= 500 and attempt < 4:
                await asyncio.sleep(5 * attempt)
                continue
            if code == "out_of_credits":
                raise OutOfCredits(message)
            raise ApiFailure(response.status_code, code, message)


def _retry_after(response: httpx.Response, error: dict) -> int:
    for value in (response.headers.get("Retry-After"), error.get("retry_after")):
        try:
            return max(1, min(int(float(value)), 120))
        except (TypeError, ValueError):
            continue
    return 20


def iso_date(value: str | None) -> str | None:
    """YouTube's 20160807 as 2016-08-07; anything else unchanged."""
    if isinstance(value, str) and len(value) == 8 and value.isdigit():
        return "%s-%s-%s" % (value[:4], value[4:6], value[6:])
    return value


def transcript_row(data: dict, source: str, include_segments: bool) -> dict:
    row = {
        "videoId": data.get("video_id"),
        "url": data.get("url"),
        "title": data.get("title"),
        "channel": data.get("channel"),
        "status": "ok",
        "language": data.get("language"),
        "captionSource": data.get("source"),
        "wordCount": data.get("word_count"),
        "durationSeconds": data.get("duration"),
        "uploadDate": iso_date(data.get("upload_date")),
        "transcript": data.get("text"),
        "paragraphs": data.get("paragraphs") or [],
        "sourceUrl": source,
    }
    if include_segments:
        row["segments"] = data.get("segments") or []
    return row


def status_row(video_id: str | None, source: str, status: str, message: str | None,
               title: str | None = None, url: str | None = None) -> dict:
    return {
        "videoId": video_id,
        "url": url or ("https://www.youtube.com/watch?v=" + video_id if video_id else None),
        "title": title,
        "status": status,
        "error": message,
        "sourceUrl": source,
    }


async def fetch_transcript(client: Client, video: str, language: str, include_segments: bool) -> dict:
    return await client.call("GET", "/transcript", params={
        "video": video,
        "language": language,
        "segments": "1" if include_segments else "0",
    })


async def run_video(client: Client, video: str, source: str, language: str,
                    include_segments: bool) -> int:
    try:
        data = await fetch_transcript(client, video, language, include_segments)
    except ApiFailure as exc:
        if exc.status == 401:
            raise
        await Actor.push_data(status_row(video, source, exc.code, exc.message))
        return 0
    await Actor.push_data(transcript_row(data, source, include_segments))
    return 1


async def run_bulk(client: Client, source: str, max_videos: int, language: str,
                   include_segments: bool) -> int:
    """Start a bulk job for a channel or playlist, wait for it, then read
    every finished transcript back from the library (free)."""
    try:
        job = await client.call("POST", "/bulk", json={
            "url": source, "max_videos": max_videos, "language": language})
    except ApiFailure as exc:
        if exc.status == 401:
            raise
        await Actor.push_data(status_row(None, source, exc.code, exc.message, url=source))
        return 0
    run_id = job["run_id"]
    title = (job.get("source") or {}).get("title") or source
    Actor.log.info("Bulk job %s started for %s.", run_id, title)
    while job.get("status") == "running":
        await asyncio.sleep(max(3, min(int(job.get("check_again_in_seconds") or 10), 60)))
        job = await client.call("GET", "/bulk/%s" % run_id)
        title = (job.get("source") or {}).get("title") or title
        await Actor.set_status_message("%s: %s of %s videos done" % (
            title, job.get("completed", 0), job.get("videos_found") or "?"))
    if job.get("error"):
        Actor.log.warning("Bulk job for %s ended with: %s", title, job["error"])

    delivered = 0
    cursor = None
    while True:
        params = {"limit": 100}
        if cursor is not None:
            params["cursor"] = cursor
        page = await client.call("GET", "/bulk/%s/results" % run_id, params=params)
        for item in page.get("items") or []:
            vid = item.get("video_id")
            if item.get("status") in HAS_TRANSCRIPT and vid:
                delivered += await run_video(client, vid, source, language, include_segments)
            else:
                error = item.get("error") or {}
                await Actor.push_data(status_row(
                    vid, source, item.get("status") or "unknown",
                    error.get("message") if isinstance(error, dict) else None,
                    title=item.get("title"), url=item.get("url")))
        cursor = page.get("next_cursor")
        if cursor is None:
            break
    if job.get("quota"):
        raise OutOfCredits("%d videos from %s were not fetched because the balance ran out."
                           % (job["quota"], title))
    return delivered


async def main() -> None:
    async with Actor:
        actor_input = await Actor.get_input() or {}
        api_key = (actor_input.get("apiKey") or "").strip()
        urls = [u.strip() for u in actor_input.get("urls") or [] if isinstance(u, str) and u.strip()]
        max_videos = max(1, min(int(actor_input.get("maxVideos") or 50), 1000))
        language = (actor_input.get("language") or "en").strip() or "en"
        include_segments = bool(actor_input.get("includeSegments"))

        if not api_key:
            await Actor.fail(status_message=(
                "Add your BulkTranscripts API key. Create one free at %s (new accounts "
                "include 30 transcripts)." % KEY_URL))
            return
        if not urls:
            await Actor.fail(status_message="Add at least one YouTube video, playlist or channel URL.")
            return

        client = Client(api_key)
        delivered = 0
        seen_videos: set[str] = set()
        try:
            account = await client.call("GET", "/account")
            billing = account.get("billing") or account
            Actor.log.info("BulkTranscripts account ready, %s credits available.",
                           billing.get("remaining", "unknown"))
            for index, source in enumerate(urls, 1):
                await Actor.set_status_message("Source %d of %d: %s" % (index, len(urls), source))
                video = video_id_of(source)
                if video:
                    if video in seen_videos:
                        continue
                    seen_videos.add(video)
                    delivered += await run_video(client, video, source, language, include_segments)
                else:
                    delivered += await run_bulk(client, source, max_videos, language, include_segments)
        except OutOfCredits as exc:
            message = ("Out of BulkTranscripts credits after %d transcripts. %s Add credits at %s "
                       "and run again: videos already fetched are free." % (delivered, exc, PRICING_URL))
            Actor.log.warning(message)
            await Actor.exit(status_message=message)
            return
        except ApiFailure as exc:
            if exc.status == 401:
                await Actor.fail(status_message=(
                    "BulkTranscripts did not accept that API key. Create one or copy yours at %s."
                    % KEY_URL))
                return
            await Actor.fail(status_message="BulkTranscripts error %s: %s" % (exc.code, exc.message))
            return
        finally:
            await client.close()

        await Actor.exit(status_message="Done: %d transcript%s saved to the dataset." % (
            delivered, "" if delivered == 1 else "s"))
