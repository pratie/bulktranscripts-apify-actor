# Download All Transcripts From a YouTube Channel (Bulk YouTube Transcripts)

Get the transcript of **every video on a YouTube channel or playlist** in one run: up to **1,000 videos per run**, with Shorts, live streams and bigger channels in blocks. One dataset row per video with the full text, paragraphs, title, channel, duration and upload date, plus timestamped segments if you want them. Export as JSON, CSV or Excel.

Powered by [BulkTranscripts](https://bulktranscripts.co), the YouTube transcript service behind the BulkTranscripts web app, REST API and MCP server.

## TL;DR

- **Channels:** `https://www.youtube.com/@TED`, `/channel/UC…`, `/c/name`, `/user/name`
- **Shorts and live streams:** set *Channel content* to Shorts or Live streams
- **Playlists:** `https://www.youtube.com/playlist?list=…` (public or unlisted)
- **Single videos:** `https://www.youtube.com/watch?v=…`, `youtu.be/…`, `/shorts/…`
- **Speed:** a 1,000-video channel takes about 7 minutes to extract on BulkTranscripts' servers (about 2 new videos per second), then about a minute to save to the dataset
- **Cost:** the Actor is free on Apify; transcripts use your BulkTranscripts credits: 30 free, then $4.99 for 200. Videos you already have are free to fetch again.

## How to download every transcript from a YouTube channel

1. **Get a BulkTranscripts API key.** Sign in at [bulktranscripts.co/app](https://bulktranscripts.co/app?tab=mcp) and create a key in the MCP & API tab. New accounts include **30 free transcripts**, no card needed.
2. **Paste the channel link** into *YouTube URLs*. Add as many channels, playlists or videos as you like, one per line.
3. **Set *Max videos per channel or playlist*** (up to 1,000). Channels start with the newest upload.
4. **Optional:** pick *Channel content* (Videos, Shorts or Live streams), a caption language, and *Include timestamped segments*.
5. **Paste your API key** and click **Start**.
6. **Download the dataset** as JSON, CSV, Excel or HTML, or send it on with Apify integrations.
7. **Channel bigger than 1,000 videos?** Run again with *Start at video #* set to 1001, then 2001, and so on. Videos you already have cost nothing.

## Try it without a key

Click **Start** with the example input and leave the API key empty: the example video runs free, so you can see the output before signing up. Your own videos, playlists and channels need a key.

## What people use it for

- **Research a creator or a whole niche.** Pull a channel's back catalogue and feed it to ChatGPT, Claude or NotebookLM.
- **Build a dataset.** Search, analysis, fine-tuning data or RAG over thousands of videos.
- **Monitor channels on a schedule.** Run it daily with Apify Schedules; videos you already have are not charged again.
- **Feed automations.** Connect the dataset to Make, Zapier, n8n, Google Sheets or a webhook.

## Input

| Field | What it does |
|---|---|
| `urls` | Videos, playlists and channels, one per line. |
| `apiKey` | Your BulkTranscripts API key (or the license key from a credit pack). Stored as a secret. Optional for the example video only. |
| `maxVideos` | Most videos to take from each channel or playlist (1 to 1,000, default 50). |
| `channelContent` | `videos` (default), `shorts` or `live`: which tab of a channel to read. |
| `startAt` | 1 is the newest video. Use 1001, 2001… for channels over 1,000 videos. |
| `language` | Preferred caption language code, e.g. `en`, `es`, `de`. Falls back to the video's available captions. |
| `includeSegments` | Add timestamped segments (start, duration, text) to each row. |

## Output

One row per video:

```json
{
  "videoId": "fNk_zzaMoSs",
  "url": "https://www.youtube.com/watch?v=fNk_zzaMoSs",
  "title": "Vectors | Chapter 1, Essence of linear algebra",
  "channel": "3Blue1Brown",
  "status": "ok",
  "language": "en",
  "captionSource": "manual_caption",
  "wordCount": 1800,
  "durationSeconds": 592,
  "uploadDate": "2016-08-05",
  "transcript": "The fundamental, root-of-it-all building block for linear algebra is the vector...",
  "paragraphs": ["The fundamental, root-of-it-all building block...", "..."],
  "sourceUrl": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"
}
```

Videos without a transcript get a row too, with `status` saying why (for example `no_transcript`, `members_only`, `private_video`) and no charge.

## Real numbers

From BulkTranscripts' production database, last 30 days to 14 October 2026:

| Measure | Result |
|---|---|
| Jobs completed | 1,652 |
| Transcripts delivered | 58,779 |
| Videos that returned a transcript | 94.0% |
| Skipped (no captions, members-only, private, age-restricted; not charged) | 4.8% |
| Genuine failures (not charged) | 1.2% |
| Fresh fetch per video | 4.2 s median, parallel within a job |
| 1,000-video channel, nothing cached | about 6½ minutes to extract |

## Limitations

- **Only videos with captions have a transcript.** About 5% of videos have none, or are members-only, private or age-restricted. They are listed with a status and never charged.
- **These are YouTube's captions, not a new transcription.** Most are auto-captions, so names and jargon keep the auto-caption mistakes.
- **1,000 videos per channel or playlist per run.** Bigger channels run in blocks with *Start at video #*.
- **Private playlists can't be read.** Set the playlist to *Unlisted* in YouTube Studio first.
- **No translation.** You get the preferred language when the video has it, otherwise its available track.

## Pricing

The Actor itself is free to run on Apify; a run uses very little compute because the extraction happens on BulkTranscripts' servers.

Transcripts use **BulkTranscripts credits**: one credit per new transcript. Videos already in your BulkTranscripts library are free to fetch again, forever, in any format. Every account starts with 30 free credits; packs are $4.99 for 200, $14.99 for 1,200 (enough for a 1,000-video channel) and $29 for 5,000, and never expire. See [bulktranscripts.co/#pricing](https://bulktranscripts.co/#pricing).

If your balance runs out mid-run, the Actor saves everything fetched so far and stops with a message; add credits and run again, and the videos you already have cost nothing.

## FAQ

**Can I download all the transcripts from a YouTube channel at once?** Yes. Paste the channel URL, set *Max videos* up to 1,000 and start. Every video with captions comes back as one dataset row; larger channels run in blocks of 1,000.

**Does it get Shorts and live streams?** Yes. Set *Channel content* to Shorts or Live streams to read those tabs instead of regular uploads.

**How fast is it?** About 2 new videos per second on BulkTranscripts' servers, so a 1,000-video channel takes about 7 minutes plus about a minute to save the dataset. Videos already in your library come back almost instantly.

**Which videos work?** Any public or unlisted video with captions, manual or auto-generated.

**Can I use the same credits elsewhere?** Yes. The same account works in the [BulkTranscripts web app](https://bulktranscripts.co/download-all-youtube-channel-transcripts), the [REST API](https://bulktranscripts.co/docs) and the [MCP server](https://bulktranscripts.co/youtube-mcp-server) for ChatGPT, Claude and Cursor.

## Changelog

- **2026-10-14:** Shorts and live streams (*Channel content*), *Start at video #* for channels over 1,000 videos, and results saved 25 at a time, so a 1,000-video channel finishes in minutes instead of about half an hour.
- **2026-10-05:** First release: channels, playlists and videos; example video runs without a key.

## Support

Questions, or a video that should work but doesn't: hello@bulktranscripts.co.

BulkTranscripts is not affiliated with YouTube or Google.
